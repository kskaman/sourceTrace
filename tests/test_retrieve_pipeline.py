"""Tests for retrieval orchestration and model fallback behavior."""
import pytest

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


def test_answer_expands_selected_children_before_generation(monkeypatch):
    child = {
        "chunk_id": 2,
        "content": "precise match",
        "source_file": "policy.md",
        "file_path": "docs/policy.md",
        "chunk_index": 1,
        "keyword_rank": 1,
        "semantic_rank": 1,
    }
    parent_context = [
        {**child, "chunk_id": 1, "chunk_index": 0, "content": "qualification"},
        child,
        {**child, "chunk_id": 3, "chunk_index": 2, "content": "exception"},
    ]
    monkeypatch.setattr(
        pipeline, "hybrid_candidates", lambda question, k, filters: [child]
    )
    expansion_calls = []

    def fake_expand(children, data_folder, radius):
        expansion_calls.append((children, data_folder, radius))
        return parent_context

    monkeypatch.setattr(pipeline, "expand_to_parent_context", fake_expand)

    class FakeResponse:
        class message:
            content = "Complete answer."

    prompts = []

    def fake_chat(**kwargs):
        prompts.append(kwargs["messages"][0]["content"])
        return FakeResponse()

    monkeypatch.setattr(pipeline.ollama_client, "chat", fake_chat)

    result = pipeline.answer(
        "What is the policy?",
        data_folder="policies",
        k=1,
        n=1,
        use_reranker=False,
    )

    assert expansion_calls == [([child], "policies", 2)]
    assert result["context"] == parent_context
    assert "qualification" in prompts[0]
    assert "exception" in prompts[0]
    assert "[policy.md#chunk-0]" in prompts[0]
    assert "[policy.md#chunk-2]" in prompts[0]


def test_answer_does_not_backfill_after_parent_windows_are_deduplicated(monkeypatch):
    children = [
        {
            "chunk_id": chunk_id,
            "content": f"match {chunk_id}",
            "source_file": "policy.md",
            "file_path": "docs/policy.md",
            "chunk_index": chunk_id,
            "keyword_rank": chunk_id,
            "semantic_rank": None,
        }
        for chunk_id in (1, 2)
    ]
    retrieval_calls = []

    def fake_candidates(question, k, filters):
        retrieval_calls.append((question, k, filters))
        return children

    monkeypatch.setattr(pipeline, "hybrid_candidates", fake_candidates)
    monkeypatch.setattr(
        pipeline,
        "expand_to_parent_context",
        lambda selected, data_folder, radius: [selected[0]],
    )

    class FakeResponse:
        class message:
            content = "Answer from unique context."

    monkeypatch.setattr(
        pipeline.ollama_client,
        "chat",
        lambda **kwargs: FakeResponse(),
    )

    result = pipeline.answer(
        "What is the policy?",
        data_folder="policies",
        k=2,
        n=2,
        use_reranker=False,
    )

    assert len(retrieval_calls) == 1
    assert result["context"] == [children[0]]


@pytest.mark.parametrize("k, n", [(0, 1), (-1, 1), (1, 0), (1, -1)])
def test_answer_rejects_non_positive_limits(k, n):
    with pytest.raises(ValueError, match="positive integer"):
        pipeline.answer("question", "policies", k=k, n=n)