"""Tests for src.ingest.text_cleaner."""
from src.ingest.text_cleaner import (
    clean_text,
    collapse_whitespace,
    normalize_unicode,
    remove_boilerplate,
    remove_empty_sections,
)


def test_normalize_unicode_replaces_artifacts():
    text = "hello\u00a0world\u200b\ufeff\u2028line2\u2029line3"
    result = normalize_unicode(text)
    assert result == "hello world\nline2\nline3"


def test_collapse_whitespace_collapses_spaces_and_tabs():
    text = "a\tb    c"
    assert collapse_whitespace(text) == "a b c"


def test_collapse_whitespace_limits_blank_lines_to_one():
    text = "para one\n\n\n\n\npara two"
    assert collapse_whitespace(text) == "para one\n\npara two"


def test_collapse_whitespace_strips_trailing_line_whitespace():
    text = "line one   \nline two\t"
    assert collapse_whitespace(text) == "line one\nline two"


def test_remove_boilerplate_drops_page_numbers_and_markers():
    text = "\n".join([
        "Real content line",
        "Page 3 of 10",
        "42",
        "CONFIDENTIAL",
        "More real content",
    ])
    result = remove_boilerplate(text)
    assert result == "Real content line\nMore real content"


def test_remove_boilerplate_keeps_lines_not_matching_patterns():
    text = "Section 42 has interesting details"
    assert remove_boilerplate(text) == text


def test_remove_empty_sections_drops_short_paragraphs():
    text = "This is a long enough paragraph to keep.\n\nshort\n\nAnother long paragraph here."
    result = remove_empty_sections(text, min_chars=10)
    assert "short" not in result
    assert "long enough paragraph" in result
    assert "Another long paragraph" in result


def test_clean_text_runs_full_pipeline():
    text = (
        "Title\u00a0Line\n\n"
        "Page 1 of 2\n\n"
        "Actual paragraph content worth keeping.\n\n"
        "short"
    )
    result = clean_text(text)
    assert result == result.strip()
    assert "\u00a0" not in result
    assert "Page 1 of 2" not in result
    assert "short" not in result
    assert "Title Line" in result
    assert "Actual paragraph content worth keeping." in result


def test_clean_text_returns_empty_string_for_boilerplate_only_input():
    text = "Page 1 of 1\nCONFIDENTIAL\n7"
    assert clean_text(text) == ""
