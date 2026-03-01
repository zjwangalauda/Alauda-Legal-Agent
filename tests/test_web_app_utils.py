"""Unit tests for web_app utility logic — zip slip protection and version strings.

These tests do NOT import streamlit or web_app.py directly; they test the
underlying logic patterns used in that module.
"""

import os
import tempfile

import pytest


# ------------------------------------------------------------------
# 1. Zip slip protection logic
# ------------------------------------------------------------------
class TestZipSlipProtection:
    """
    The web_app.py zip extraction code validates each member path like this:

        member_path = os.path.realpath(os.path.join(extract_dir, member))
        if not member_path.startswith(os.path.realpath(extract_dir) + os.sep) \
                and member_path != os.path.realpath(extract_dir):
            raise ValueError(...)

    We replicate that exact logic here and verify it catches path traversal.
    """

    @staticmethod
    def _validate_zip_member(extract_dir: str, member: str) -> None:
        """Replica of the zip-slip guard from web_app.py."""
        member_path = os.path.realpath(os.path.join(extract_dir, member))
        if (
            not member_path.startswith(os.path.realpath(extract_dir) + os.sep)
            and member_path != os.path.realpath(extract_dir)
        ):
            raise ValueError(f"Zip slip detected: {member}")

    def test_safe_member_passes(self):
        """A normal relative path inside the extract dir should be accepted."""
        with tempfile.TemporaryDirectory() as extract_dir:
            # Should NOT raise
            self._validate_zip_member(extract_dir, "contracts/agreement.pdf")

    def test_path_traversal_with_dotdot_is_rejected(self):
        """A member like '../../etc/passwd' must be rejected."""
        with tempfile.TemporaryDirectory() as extract_dir:
            with pytest.raises(ValueError, match="Zip slip detected"):
                self._validate_zip_member(extract_dir, "../../etc/passwd")

    def test_path_traversal_leading_slash_is_rejected(self):
        """An absolute path member must be rejected."""
        with tempfile.TemporaryDirectory() as extract_dir:
            with pytest.raises(ValueError, match="Zip slip detected"):
                self._validate_zip_member(extract_dir, "/etc/passwd")

    def test_nested_safe_path_passes(self):
        """Deeply nested safe paths should be accepted."""
        with tempfile.TemporaryDirectory() as extract_dir:
            self._validate_zip_member(extract_dir, "a/b/c/d/file.txt")

    def test_dotdot_inside_safe_path_that_resolves_outside(self):
        """A path like 'subdir/../../outside' that escapes must be rejected."""
        with tempfile.TemporaryDirectory() as extract_dir:
            with pytest.raises(ValueError, match="Zip slip detected"):
                self._validate_zip_member(extract_dir, "subdir/../../outside.txt")

    def test_current_dir_member_passes(self):
        """The extract directory itself (empty member resolving to extract_dir) should pass."""
        with tempfile.TemporaryDirectory() as extract_dir:
            # os.path.join(extract_dir, "") == extract_dir, and realpath matches
            self._validate_zip_member(extract_dir, "")


# ------------------------------------------------------------------
# 2. Version string checks — all source files should be V6.2
# ------------------------------------------------------------------
class TestVersionStrings:
    """Ensure that the version has been uniformly updated to V6.2 in source files."""

    # The two main source files that contain version references
    _SOURCE_DIR = os.path.join(os.path.dirname(__file__), os.pardir)

    def _read_source(self, filename: str) -> str:
        path = os.path.normpath(os.path.join(self._SOURCE_DIR, filename))
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def test_no_v61_in_alauda_legal_agent(self):
        """alauda_legal_agent.py must not contain any leftover V6.1 references."""
        content = self._read_source("alauda_legal_agent.py")
        assert "V6.1" not in content, "Found stale V6.1 reference in alauda_legal_agent.py"

    def test_no_v61_in_web_app(self):
        """web_app.py must not contain any leftover V6.1 references."""
        content = self._read_source("web_app.py")
        assert "V6.1" not in content, "Found stale V6.1 reference in web_app.py"

    def test_v62_present_in_alauda_legal_agent(self):
        """alauda_legal_agent.py should contain V6.2 version strings."""
        content = self._read_source("alauda_legal_agent.py")
        assert "V6.2" in content, "V6.2 version string missing from alauda_legal_agent.py"

    def test_v62_present_in_web_app(self):
        """web_app.py should contain V6.2 version strings."""
        content = self._read_source("web_app.py")
        assert "V6.2" in content, "V6.2 version string missing from web_app.py"

    def test_no_v61_in_docx_redline_engine(self):
        """docx_redline_engine.py must not contain any leftover V6.1 references."""
        content = self._read_source("docx_redline_engine.py")
        assert "V6.1" not in content, "Found stale V6.1 reference in docx_redline_engine.py"
