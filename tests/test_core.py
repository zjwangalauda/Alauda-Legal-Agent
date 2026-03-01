"""Core unit tests for alauda_legal_agent module."""

import os
import tempfile

import pytest

from alauda_legal_agent import (
    MAX_CONTRACT_CHARS,
    ComprehensiveReviewReport,
    MultiDocReviewReport,
    extract_text_from_file,
    get_mock_response,
)


# ------------------------------------------------------------------
# 1. Constants
# ------------------------------------------------------------------
class TestConstants:
    def test_max_contract_chars_is_positive(self):
        assert MAX_CONTRACT_CHARS > 0

    def test_max_contract_chars_value(self):
        assert MAX_CONTRACT_CHARS == 500_000


# ------------------------------------------------------------------
# 2. Pydantic model validation
# ------------------------------------------------------------------
class TestPydanticModels:
    def test_comprehensive_report_minimal(self):
        report = ComprehensiveReviewReport(
            contract_name="Test Contract",
            commercial_summary=[],
            legal_reviews=[],
            cxo_view={
                "approval_recommendation": "test",
                "deal_breaker_summary": "none",
                "strategic_advice": "proceed",
            },
        )
        assert report.contract_name == "Test Contract"
        assert report.legal_reviews == []

    def test_multi_doc_report_minimal(self):
        report = MultiDocReviewReport(
            project_name="Test Project",
            document_hierarchy=[],
            commercial_summary=[],
            hidden_backdoors=[],
            cxo_view={
                "approval_recommendation": "test",
                "deal_breaker_summary": "none",
                "strategic_advice": "proceed",
            },
        )
        assert report.project_name == "Test Project"
        assert report.hidden_backdoors == []

    def test_comprehensive_report_missing_required_field(self):
        with pytest.raises(Exception):
            ComprehensiveReviewReport(
                contract_name="Test",
                # missing commercial_summary, legal_reviews, cxo_view
            )

    def test_multi_doc_report_missing_required_field(self):
        with pytest.raises(Exception):
            MultiDocReviewReport(
                project_name="Test",
                # missing other required fields
            )


# ------------------------------------------------------------------
# 3. Mock response correctness
# ------------------------------------------------------------------
class TestMockResponse:
    def test_single_mode_returns_comprehensive_report(self):
        result = get_mock_response("single")
        assert isinstance(result, ComprehensiveReviewReport)
        assert result.contract_name
        assert len(result.commercial_summary) > 0
        assert len(result.legal_reviews) > 0

    def test_multi_mode_returns_multi_doc_report(self):
        result = get_mock_response("multi")
        assert isinstance(result, MultiDocReviewReport)
        assert result.project_name
        assert len(result.document_hierarchy) > 0
        assert len(result.hidden_backdoors) > 0

    def test_mock_cxo_view_populated(self):
        for mode in ("single", "multi"):
            result = get_mock_response(mode)
            assert result.cxo_view.approval_recommendation
            assert result.cxo_view.deal_breaker_summary
            assert result.cxo_view.strategic_advice


# ------------------------------------------------------------------
# 4. extract_text_from_file
# ------------------------------------------------------------------
class TestExtractText:
    def test_plain_text_file(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("Hello World")
            f.flush()
            path = f.name
        try:
            text = extract_text_from_file(path)
            assert "Hello World" in text
        finally:
            os.unlink(path)

    def test_unsupported_doc_format_raises(self):
        with tempfile.NamedTemporaryFile(suffix=".doc", delete=False) as f:
            path = f.name
        try:
            with pytest.raises(ValueError, match="不受支持"):
                extract_text_from_file(path)
        finally:
            os.unlink(path)

    def test_nonexistent_file_returns_empty(self):
        text = extract_text_from_file("/tmp/_nonexistent_file_12345.pdf")
        assert text == ""
