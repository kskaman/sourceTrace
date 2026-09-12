"""Tests for the recursive_split chunker in src.ingest.pipeline."""
from src.ingest.pipeline import recursive_split


def test_recursive_split_returns_single_chunk_for_short_text():
    text = "A short paragraph that fits in one chunk."
    chunks = recursive_split(text, chunk_size=512)
    assert chunks == [text]


def test_recursive_split_returns_empty_list_for_blank_text():
    assert recursive_split("   \n\n  ", chunk_size=512) == []
    assert recursive_split("", chunk_size=512) == []


def test_recursive_split_splits_on_paragraph_breaks_first():
    paragraphs = [f"Paragraph {i} " + ("word " * 10) for i in range(5)]
    text = "\n\n".join(paragraphs)

    chunks = recursive_split(text, chunk_size=80)

    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk) <= 80


def test_recursive_split_respects_chunk_size_for_long_unsplittable_text():
    # No separators at all, forces the hard-split fallback.
    text = "a" * 2000

    chunks = recursive_split(text, chunk_size=512, overlap=50)

    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk) <= 512
    assert "".join(chunks).replace("a", "") == ""  # all chunks are just "a"s


def test_recursive_split_hard_fallback_produces_overlapping_chunks():
    text = "0123456789" * 100  # 1000 chars, no separators

    chunks = recursive_split(text, chunk_size=200, overlap=50)

    assert len(chunks) > 1
    # Consecutive chunks should overlap by the requested amount.
    first_tail = chunks[0][-50:]
    second_head = chunks[1][:50]
    assert first_tail == second_head
