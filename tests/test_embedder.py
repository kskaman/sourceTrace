"""Tests for src.ingest.embedder."""
import pytest

from src.ingest import embedder


def test_embed_chunks_returns_one_vector_per_text():
    texts = ["Hello world", "Another sentence to embed", "Third one"]
    vectors = embedder.embed_chunks(texts, batch_size=2)

    assert len(vectors) == len(texts)
    assert all(len(vec) == 384 for vec in vectors)  # all-MiniLM-L6-v2 dimension


def test_embed_chunks_handles_empty_list():
    assert embedder.embed_chunks([]) == []


def test_embed_chunks_with_retry_matches_embed_chunks_on_success():
    texts = ["A simple sentence."]
    vectors = embedder.embed_chunks_with_retry(texts, batch_size=64)

    assert len(vectors) == 1
    assert len(vectors[0]) == 384


def test_embed_chunks_with_retry_retries_then_succeeds(monkeypatch):
    real_encode = embedder.model.encode
    calls = {"count": 0}

    def flaky_encode(batch, show_progress_bar=False):
        calls["count"] += 1
        if calls["count"] == 1:
            raise RuntimeError("simulated transient failure")
        return real_encode(batch, show_progress_bar=show_progress_bar)

    monkeypatch.setattr(embedder.model, "encode", flaky_encode)
    monkeypatch.setattr(embedder.time, "sleep", lambda _: None)

    vectors = embedder.embed_chunks_with_retry(["retry me"], batch_size=64, max_retries=3)

    assert calls["count"] == 2
    assert len(vectors) == 1


def test_embed_chunks_with_retry_raises_after_max_retries(monkeypatch):
    def always_fails(batch, show_progress_bar=False):
        raise RuntimeError("permanent failure")

    monkeypatch.setattr(embedder.model, "encode", always_fails)
    monkeypatch.setattr(embedder.time, "sleep", lambda _: None)

    with pytest.raises(RuntimeError):
        embedder.embed_chunks_with_retry(["will fail"], batch_size=64, max_retries=2)
