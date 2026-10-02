"""Tests for retrieval orchestration and model fallback behavior."""

from src.retrieve import pipeline


def test_answer_returns_message_without_calling_models_when_index_is_empty(
    monkeypatch,
):
    retrieval_calls = []

    def fake_hybrid_candidates(question, k, filters):
        retrieval_calls.append((question, k, filters))
        return []

    monkeypatch.setattr(pipeline, "hybrid_candidates", fake_hybrid_candidates)

    def fail_if_called(*args, **kwargs):
        raise AssertionError("No model should be called for an empty index")

    monkeypatch.setattr(pipeline, "select_context", fail_if_called)
    monkeypatch.setattr(pipeline.ollama_client, "chat", fail_if_called)

    result = pipeline.answer("Where is the policy?", data_folder="policies")

    assert result == {
        "answer": pipeline.NO_INDEXED_REFERENCES_MESSAGE,
        "context": [],
        "candidate_count": 0,
    }
    assert retrieval_calls == [
        ("Where is the policy?", 20, {"data_folder": "policies"})
    ]