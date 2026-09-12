"""Tests for src.ingest.document_parser."""
import pytest

from src.ingest.document_parser import ParsedDocument, parse_document


def test_parse_markdown_extracts_front_matter_as_metadata(corpus_dir):
    doc = parse_document(corpus_dir / "refund_policy.md")

    assert isinstance(doc, ParsedDocument)
    assert doc.metadata["title"] == "Refund Policy"
    assert doc.metadata["category"] == "Operations"
    assert doc.metadata["doc_type"] == "policy"  # overridden by front matter
    assert doc.metadata["owner"] == "Finance"
    assert doc.metadata["classification"] == "Public"
    assert doc.metadata["source"] == "refund_policy.md"
    assert not doc.text.lstrip().startswith("---")  # front matter fence stripped
    assert "# Refund Policy" in doc.text


def test_parse_html_extracts_meta_tags_and_strips_tags(corpus_dir):
    doc = parse_document(corpus_dir / "vpn_access_guide.html")

    assert doc.metadata["title"] == "VPN Access Guide"
    assert doc.metadata["category"] == "IT"
    assert doc.metadata["doc_type"] == "guide"  # overridden by <meta> tags
    assert doc.metadata["owner"] == "IT Operations"
    assert "VPN Access Guide" in doc.text
    assert "font-family" not in doc.text  # <style> content must be stripped
    assert "<" not in doc.text


def test_parse_docx_extracts_paragraph_text(corpus_dir):
    doc = parse_document(corpus_dir / "it_asset_management_policy.docx")

    assert doc.metadata["doc_type"] == "docx"
    assert doc.metadata["source"] == "it_asset_management_policy.docx"
    assert len(doc.text.strip()) > 0
    assert doc.pages == [doc.text]


def test_parse_pdf_extracts_text_per_page(corpus_dir):
    doc = parse_document(corpus_dir / "rsu_vesting_schedule.pdf")

    assert doc.metadata["doc_type"] == "pdf"
    assert doc.metadata["total_pages"] == len(doc.pages)
    assert len(doc.pages) >= 1
    assert len(doc.text.strip()) > 0


def test_parse_document_routes_txt_like_markdown(tmp_path):
    txt_file = tmp_path / "note.txt"
    txt_file.write_text("Plain text content.", encoding="utf-8")

    doc = parse_document(txt_file)

    assert doc.metadata["doc_type"] == "markdown"
    assert doc.text == "Plain text content."


def test_parse_document_raises_on_unsupported_extension(tmp_path):
    bad_file = tmp_path / "data.xyz"
    bad_file.write_text("content", encoding="utf-8")

    with pytest.raises(ValueError):
        parse_document(bad_file)
