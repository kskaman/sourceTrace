"""Tests for using contextual prefixes during candidate reranking."""

from src.retrieve import hybrid, reranker


def test_keyword_search_returns_context_prefix(monkeypatch):
    monkeypatch.setattr(
        hybrid,
        "_fetch_rows",
        lambda sql, params: [
            (
                7,
                "Refunds arrive in five days.",
                "Finance refund timing policy.",
                "refund.md",
                "markdown",
                "Finance",
                2,
                None,
                0.75,
            )
        ],
    )

    (candidate,) = hybrid.keyword_search("refund timing", k=1)

    assert candidate["content"] == "Refunds arrive in five days."
    assert candidate["context_prefix"] == "Finance refund timing policy."


def test_semantic_search_returns_context_prefix(monkeypatch):
    monkeypatch.setattr(
        "src.retrieve.embedder.embed_query", lambda query: [0.0] * 384
    )
    monkeypatch.setattr(
        hybrid,
        "_fetch_rows",
        lambda sql, params: [
            (
                8,
                "Records may be retained for legal obligations.",
                "EU customer deletion and retention policy.",
                "retention.md",
                "markdown",
                "Legal",
                4,
                None,
                0.91,
            )
        ],
    )

    (candidate,) = hybrid.semantic_search("legal retention", k=1)

    assert candidate["content"] == "Records may be retained for legal obligations."
    assert candidate["context_prefix"] == "EU customer deletion and retention policy."
    assert candidate["semantic_score"] == 0.91


def test_reranker_scores_contextual_text_but_preserves_raw_content(monkeypatch):
    class FakeModel:
        def __init__(self):
            self.pairs = None

        def predict(self, pairs, show_progress_bar):
            self.pairs = pairs
            return [0.8]

    model = FakeModel()
    monkeypatch.setattr(reranker, "_model", model)
    candidate = {
        "chunk_id": 7,
        "content": "Refunds arrive in five days.",
        "context_prefix": "Finance refund timing policy.",
    }

    (selected,) = reranker.rerank("When do refunds arrive?", [candidate], top_n=1)

    assert model.pairs == [
        (
            "When do refunds arrive?",
            "Finance refund timing policy.\n\nRefunds arrive in five days.",
        )
    ]
    assert selected["content"] == candidate["content"]


def test_reranker_handles_baseline_chunk_without_context_prefix(monkeypatch):
    class FakeModel:
        def __init__(self):
            self.pairs = None

        def predict(self, pairs, show_progress_bar):
            self.pairs = pairs
            return [0.5]

    model = FakeModel()
    monkeypatch.setattr(reranker, "_model", model)
    candidate = {
        "chunk_id": 8,
        "content": "Baseline chunk text.",
        "context_prefix": None,
    }

    reranker.rerank("question", [candidate], top_n=1)

    assert model.pairs == [("question", "Baseline chunk text.")]