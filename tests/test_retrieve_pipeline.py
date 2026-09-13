"""Tests for retrieval orchestration and model fallback behavior."""

from src.retrieve import pipeline


def test_answer_returns_message_without_calling_models_when_index_is_empty(
    monkeypatch,
):
    monkeypatch.setattr(pipeline, "hybrid_candidates", lambda question, k: [])

    def fail_if_called(*args, **kwargs):
        raise AssertionError("No model should be called for an empty index")

    monkeypatch.setattr(pipeline, "select_context", fail_if_called)
    monkeypatch.setattr(pipeline.ollama_client, "chat", fail_if_called)

    result = pipeline.answer("Where is the policy?")

    assert result == {
        "answer": pipeline.NO_INDEXED_REFERENCES_MESSAGE,
        "context": [],
        "candidate_count": 0,
    }