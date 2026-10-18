"""Tests for trace collection and its use in the retrieval pipeline."""
import json

import pytest

from src import observability
from src.retrieve import pipeline


def test_log_event_is_ignored_without_a_trace():
    observability._events.set(None)
    observability.log_event("orphan")
    assert observability.trace_events() == []


def test_span_records_latency_and_fields():
    observability.new_trace()
    with observability.span("stage", k=3):
        pass

    (event,) = observability.trace_events()
    assert event["stage"] == "stage"
    assert event["k"] == 3
    assert event["latency_ms"] >= 0


def test_span_records_error_and_reraises():
    observability.new_trace()
    with pytest.raises(ValueError):
        with observability.span("boom"):
            raise ValueError("bad")

    (event,) = observability.trace_events()
    assert "ValueError" in event["error"]


def test_new_trace_resets_events():
    observability.new_trace()
    observability.log_event("first")
    observability.new_trace()
    assert observability.trace_events() == []


def test_write_trace_writes_summary_and_events(tmp_path):
    observability.new_trace()
    with observability.span("stage"):
        pass

    path = observability.write_trace(str(tmp_path / "traces"), label="a b/c")

    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["summary"]["trace_id"] == observability.current_trace_id()
    assert payload["events"][0]["stage"] == "stage"
    assert "/" not in path.name and " " not in path.name


def test_answer_emits_stage_events(monkeypatch):
    candidates = [
        {
            "chunk_id": 1,
            "content": "Refunds take 5 days.",
            "source_file": "refund.md",
            "chunk_index": 0,
            "keyword_rank": 1,
            "semantic_rank": 1,
        }
    ]
    monkeypatch.setattr(pipeline, "hybrid_candidates", lambda q, k, filters: candidates)
    monkeypatch.setattr(
        pipeline,
        "expand_to_parent_context",
        lambda children, data_folder, radius: children,
    )

    class FakeResponse:
        class message:
            content = " Five days. "

    monkeypatch.setattr(
        pipeline.ollama_client, "chat", lambda **kwargs: FakeResponse
    )

    result = pipeline.answer("How long?", "policies", use_reranker=False)

    assert result["answer"] == "Five days."
    stages = observability.trace_summary()["stages"]
    assert {
        "request.start",
        "retrieval.hybrid",
        "retrieval.candidates",
        "selection.context",
        "retrieval.parent_context",
        "retrieval.parent_context.result",
        "generation.llm",
        "generation.complete",
    } <= set(stages)
    assert "How long?" not in json.dumps(observability.trace_events())
