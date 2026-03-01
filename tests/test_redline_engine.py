"""Unit tests for docx_redline_engine.py — WordRedlineEngine."""

import os
import shutil
import tempfile
import zipfile

from docx_redline_engine import WordRedlineEngine

# ---------------------------------------------------------------------------
# Helper: create a minimal valid .docx file (zip with word/document.xml)
# ---------------------------------------------------------------------------
_W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def _make_mini_docx(path: str, paragraphs: list[str] | None = None) -> None:
    """Create a tiny but structurally valid .docx so WordRedlineEngine can open it."""
    if paragraphs is None:
        paragraphs = ["Hello world."]

    body_children = ""
    for text in paragraphs:
        body_children += (
            f'<w:p><w:r><w:t xml:space="preserve">{text}</w:t></w:r></w:p>\n'
        )

    doc_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<w:document xmlns:w="{_W_NS}">'
        f"<w:body>{body_children}</w:body>"
        "</w:document>"
    )

    content_types_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Override PartName="/word/document.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
        "</Types>"
    )

    rels_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
        "</Relationships>"
    )

    doc_rels_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        "</Relationships>"
    )

    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("word/document.xml", doc_xml)
        zf.writestr("[Content_Types].xml", content_types_xml)
        zf.writestr("_rels/.rels", rels_xml)
        zf.writestr("word/_rels/document.xml.rels", doc_rels_xml)



# ------------------------------------------------------------------
# 1. Context manager protocol (__enter__ / __exit__)
# ------------------------------------------------------------------
class TestContextManager:
    def test_enter_returns_self(self):
        """__enter__ must return the engine instance itself."""
        tmp = tempfile.NamedTemporaryFile(suffix=".docx", delete=False)
        tmp.close()
        _make_mini_docx(tmp.name)
        try:
            engine = WordRedlineEngine(tmp.name)
            result = engine.__enter__()
            assert result is engine
            engine.__exit__(None, None, None)
        finally:
            if os.path.exists(tmp.name):
                os.unlink(tmp.name)

    def test_with_statement_works(self):
        """The engine should be usable in a `with` block without errors."""
        tmp = tempfile.NamedTemporaryFile(suffix=".docx", delete=False)
        tmp.close()
        _make_mini_docx(tmp.name)
        try:
            with WordRedlineEngine(tmp.name) as engine:
                assert isinstance(engine, WordRedlineEngine)
                temp_dir = engine.temp_dir
                assert os.path.isdir(temp_dir)
            # After exiting the context, temp_dir should be cleaned up
            assert not os.path.exists(temp_dir)
        finally:
            if os.path.exists(tmp.name):
                os.unlink(tmp.name)

    def test_exit_returns_false(self):
        """__exit__ must return False so exceptions are not suppressed."""
        tmp = tempfile.NamedTemporaryFile(suffix=".docx", delete=False)
        tmp.close()
        _make_mini_docx(tmp.name)
        try:
            engine = WordRedlineEngine(tmp.name)
            ret = engine.__exit__(None, None, None)
            assert ret is False
        finally:
            if os.path.exists(tmp.name):
                os.unlink(tmp.name)


# ------------------------------------------------------------------
# 2. cleanup() removes the temp directory
# ------------------------------------------------------------------
class TestCleanup:
    def test_cleanup_removes_temp_dir(self):
        tmp = tempfile.NamedTemporaryFile(suffix=".docx", delete=False)
        tmp.close()
        _make_mini_docx(tmp.name)
        try:
            engine = WordRedlineEngine(tmp.name)
            temp_dir = engine.temp_dir
            assert os.path.isdir(temp_dir)
            engine.cleanup()
            assert not os.path.exists(temp_dir)
        finally:
            if os.path.exists(tmp.name):
                os.unlink(tmp.name)

    def test_cleanup_idempotent(self):
        """Calling cleanup() twice must not raise."""
        tmp = tempfile.NamedTemporaryFile(suffix=".docx", delete=False)
        tmp.close()
        _make_mini_docx(tmp.name)
        try:
            engine = WordRedlineEngine(tmp.name)
            engine.cleanup()
            engine.cleanup()  # second call should be a no-op
        finally:
            if os.path.exists(tmp.name):
                os.unlink(tmp.name)


# ------------------------------------------------------------------
# 3. __del__ doesn't crash if temp_dir already removed
# ------------------------------------------------------------------
class TestDel:
    def test_del_after_cleanup_does_not_crash(self):
        """If temp_dir is already removed, __del__ must silently succeed."""
        tmp = tempfile.NamedTemporaryFile(suffix=".docx", delete=False)
        tmp.close()
        _make_mini_docx(tmp.name)
        try:
            engine = WordRedlineEngine(tmp.name)
            engine.cleanup()
            # Manually invoke __del__ — should not raise
            engine.__del__()
        finally:
            if os.path.exists(tmp.name):
                os.unlink(tmp.name)

    def test_del_without_temp_dir_attr(self):
        """__del__ must not crash even if temp_dir attribute is missing."""
        tmp = tempfile.NamedTemporaryFile(suffix=".docx", delete=False)
        tmp.close()
        _make_mini_docx(tmp.name)
        try:
            engine = WordRedlineEngine(tmp.name)
            td = engine.temp_dir
            del engine.temp_dir  # remove the attribute
            engine.__del__()  # should not raise (hasattr check)
            # Manually clean up since the engine can no longer do it
            if os.path.exists(td):
                shutil.rmtree(td, ignore_errors=True)
        finally:
            if os.path.exists(tmp.name):
                os.unlink(tmp.name)


# ------------------------------------------------------------------
# 4. _normalize() method
# ------------------------------------------------------------------
class TestNormalize:
    def test_strips_non_word_chars_and_lowercases(self):
        tmp = tempfile.NamedTemporaryFile(suffix=".docx", delete=False)
        tmp.close()
        _make_mini_docx(tmp.name)
        try:
            engine = WordRedlineEngine(tmp.name)
            assert engine._normalize("Hello, World!") == "helloworld"
            engine.cleanup()
        finally:
            if os.path.exists(tmp.name):
                os.unlink(tmp.name)

    def test_normalize_unicode(self):
        tmp = tempfile.NamedTemporaryFile(suffix=".docx", delete=False)
        tmp.close()
        _make_mini_docx(tmp.name)
        try:
            engine = WordRedlineEngine(tmp.name)
            result = engine._normalize("合同 - 第一条")
            # \W+ strips the spaces and dash; Chinese chars are \w in Python regex
            assert result == "合同第一条"
            engine.cleanup()
        finally:
            if os.path.exists(tmp.name):
                os.unlink(tmp.name)

    def test_normalize_empty_string(self):
        tmp = tempfile.NamedTemporaryFile(suffix=".docx", delete=False)
        tmp.close()
        _make_mini_docx(tmp.name)
        try:
            engine = WordRedlineEngine(tmp.name)
            assert engine._normalize("") == ""
            engine.cleanup()
        finally:
            if os.path.exists(tmp.name):
                os.unlink(tmp.name)

    def test_normalize_only_special_chars(self):
        tmp = tempfile.NamedTemporaryFile(suffix=".docx", delete=False)
        tmp.close()
        _make_mini_docx(tmp.name)
        try:
            engine = WordRedlineEngine(tmp.name)
            assert engine._normalize("!@#$%^&*()") == ""
            engine.cleanup()
        finally:
            if os.path.exists(tmp.name):
                os.unlink(tmp.name)


# ------------------------------------------------------------------
# 5. apply_redline() returns False for empty / whitespace input
# ------------------------------------------------------------------
class TestApplyRedlineEdgeCases:
    def test_apply_redline_returns_false_for_empty_string(self):
        tmp = tempfile.NamedTemporaryFile(suffix=".docx", delete=False)
        tmp.close()
        _make_mini_docx(tmp.name)
        try:
            engine = WordRedlineEngine(tmp.name)
            result = engine.apply_redline("", "replacement", "reason")
            assert result is False
            engine.cleanup()
        finally:
            if os.path.exists(tmp.name):
                os.unlink(tmp.name)

    def test_apply_redline_returns_false_for_whitespace_only(self):
        tmp = tempfile.NamedTemporaryFile(suffix=".docx", delete=False)
        tmp.close()
        _make_mini_docx(tmp.name)
        try:
            engine = WordRedlineEngine(tmp.name)
            # Whitespace normalizes to empty after _normalize() strips \W+
            result = engine.apply_redline("   \t\n  ", "replacement", "reason")
            assert result is False
            engine.cleanup()
        finally:
            if os.path.exists(tmp.name):
                os.unlink(tmp.name)

    def test_apply_redline_returns_false_for_no_match(self):
        """When the snippet doesn't appear in the document, return False."""
        tmp = tempfile.NamedTemporaryFile(suffix=".docx", delete=False)
        tmp.close()
        _make_mini_docx(tmp.name, paragraphs=["This is the only paragraph."])
        try:
            engine = WordRedlineEngine(tmp.name)
            result = engine.apply_redline(
                "text that does not exist anywhere", "replacement", "reason"
            )
            assert result is False
            engine.cleanup()
        finally:
            if os.path.exists(tmp.name):
                os.unlink(tmp.name)

    def test_apply_redline_returns_true_for_match(self):
        """When the snippet matches a paragraph, return True."""
        tmp = tempfile.NamedTemporaryFile(suffix=".docx", delete=False)
        tmp.close()
        _make_mini_docx(tmp.name, paragraphs=["The liability cap shall not exceed fees paid."])
        try:
            engine = WordRedlineEngine(tmp.name)
            result = engine.apply_redline(
                "liability cap shall not exceed", "revised text", "reason"
            )
            assert result is True
            engine.cleanup()
        finally:
            if os.path.exists(tmp.name):
                os.unlink(tmp.name)
