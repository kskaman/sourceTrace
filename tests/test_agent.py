"""Tests for the agentic RAG loop: tool calls, budgets, degradation and tracing."""
import json
from types import SimpleNamespace

import pytest

from src import observability
from src.retrieve import agent, pipeline

REAL_DECOMPOSE = agent._decompose


def _chunk(index, source="policy.md", content=None):
    return {
        "chunk_id": index,
        "content": content or f"content {index}",
        "source_file": source,
        "chunk_index": index,
        "keyword_rank": index + 1,
        "semantic_rank": index + 1,
    }


def _tool_call(query, k=None, name="search"):
    arguments = {"query": query}
    if k is not None:
        arguments["k"] = k
    return SimpleNamespace(function=SimpleNamespace(name=name, arguments=arguments))


def _response(content="", tool_calls=None):
    return SimpleNamespace(
        message=SimpleNamespace(content=content, tool_calls=tool_calls),
        prompt_eval_count=10,
        eval_count=5,
    )


class ScriptedLLM:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def __call__(self, **kwargs):
        self.calls.append(
            {**kwargs, "messages": [dict(m) for m in kwargs["messages"]]}
        )
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


@pytest.fixture(autouse=True)
def no_real_decomposition(monkeypatch):
    monkeypatch.setattr(agent, "_decompose", lambda query: [])


@pytest.fixture()
def searches(monkeypatch):
    seen = []

    def fake_hybrid(query, k, filters):
        seen.append({"query": query, "k": k, "filters": filters})
        return [_chunk(0), _chunk(1)]

    monkeypatch.setattr(agent, "hybrid_candidates", fake_hybrid)
    monkeypatch.setattr(
        agent, "select_context", lambda candidates, n, use_reranker, query: candidates[:n]
    )
    return seen


def _install(monkeypatch, responses):
    llm = ScriptedLLM(responses)
    monkeypatch.setattr(agent.ollama_client, "chat", llm)
    return llm


def _stages():
    return [event["stage"] for event in observability.trace_events()]


def test_agent_searches_then_answers_with_citations(monkeypatch, searches):
    llm = _install(
        monkeypatch,
        [
            _response(tool_calls=[_tool_call("refund window")]),
            _response("Five days [policy.md#chunk-0]."),
        ],
    )

    result = agent.agent_answer("How long?", "policies", max_steps=4)

    assert result["answer"] == "Five days [policy.md#chunk-0]."
    assert result["steps"] == 2
    assert result["search_calls"] == 1
    assert result["stop_reason"] == "answered"
    assert [c["chunk_index"] for c in result["context"]] == [0, 1]
    assert searches == [
        {"query": "refund window", "k": 20, "filters": {"data_folder": "policies"}}
    ]
    tool_message = llm.calls[1]["messages"][-1]
    assert tool_message["role"] == "tool"
    assert json.loads(tool_message["content"])["results"][0]["marker"] == "policy.md#chunk-0"
    assert llm.calls[0]["tools"] == [agent.SEARCH_TOOL]


def test_agent_trace_has_step_tool_and_citation_events(monkeypatch, searches):
    _install(
        monkeypatch,
        [
            _response(tool_calls=[_tool_call("q")]),
            _response("Answer [policy.md#chunk-0] [other.md#chunk-9]."),
            _response("Still [other.md#chunk-9]."),
        ],
    )

    result = agent.agent_answer("Q?", "policies")

    assert result["trace_id"] == observability.current_trace_id()
    stages = set(_stages())
    assert {
        "request.start",
        "agent.llm",
        "agent.llm.result",
        "agent.tool.search",
        "agent.tool.result",
        "agent.citations",
        "agent.final",
        "retrieval.hybrid",
    } <= stages
    events = observability.trace_events()
    citations = next(e for e in events if e["stage"] == "agent.citations")
    assert citations["ungrounded"] == ["other.md#chunk-9"]
    summary = observability.trace_summary()
    assert summary["prompt_tokens"] == 30
    assert summary["completion_tokens"] == 15
    assert summary["stages"]["agent.llm"]["count"] == 3
    # Retrieval runs inside the tool span, so its events point at it.
    tool_span = next(e for e in events if e["stage"] == "agent.tool.search")
    retrieval = next(e for e in events if e["stage"] == "retrieval.hybrid")
    assert retrieval["parent_id"] == tool_span["span_id"]
    assert "Q?" not in json.dumps([e for e in events if e["stage"] == "request.start"])


def test_answer_without_searching_triggers_a_forced_search(monkeypatch, searches):
    llm = _install(
        monkeypatch,
        [_response("Five days."), _response("Five days [policy.md#chunk-0].")],
    )

    result = agent.agent_answer("How long?", "policies")

    assert [s["query"] for s in searches] == ["How long?"]
    assert result["search_calls"] == 1
    assert result["answer"] == "Five days [policy.md#chunk-0]."
    assert "agent.forced_search" in _stages()
    # The model's unsearched answer is not kept in the conversation.
    assert llm.calls[1]["messages"][2]["content"] == ""


def test_answer_from_outside_knowledge_is_blocked_when_nothing_relevant_was_found(
    monkeypatch,
):
    monkeypatch.setattr(agent, "hybrid_candidates", lambda query, k, filters: [])
    _install(
        monkeypatch,
        [_response(tool_calls=[_tool_call("capital of France")]), _response("Paris.")],
    )

    result = agent.agent_answer("Capital of France?", "policies")

    assert result["answer"] == "I don't know."
    assert result["stop_reason"] == "no_evidence"
    assert "agent.answer_blocked" in _stages()


def test_no_search_is_possible_with_a_single_step_so_the_answer_is_blocked(monkeypatch, searches):
    _install(monkeypatch, [_response("Paris.")])

    result = agent.agent_answer("Q?", "policies", max_steps=1)

    assert result["answer"] == "I don't know."
    assert searches == []


def test_agent_limits_chunks_per_search_to_n(monkeypatch, searches):
    _install(
        monkeypatch,
        [_response(tool_calls=[_tool_call("q", k=50)]), _response("done [policy.md#chunk-0]")],
    )

    result = agent.agent_answer("Q?", "policies", n=1)

    assert len(result["context"]) == 1


def test_search_budget_withholds_the_tool_and_forces_an_answer(monkeypatch, searches):
    llm = _install(
        monkeypatch,
        [
            _response(tool_calls=[_tool_call("one")]),
            _response(tool_calls=[_tool_call("two")]),
            _response("Final [policy.md#chunk-0]."),
        ],
    )

    result = agent.agent_answer("Q?", "policies", max_steps=6, max_search_calls=2)

    assert result["search_calls"] == 2
    assert result["answer"] == "Final [policy.md#chunk-0]."
    assert llm.calls[2]["tools"] is None


def test_extra_tool_calls_in_one_step_are_refused(monkeypatch, searches):
    llm = _install(
        monkeypatch,
        [
            _response(tool_calls=[_tool_call("one"), _tool_call("two")]),
            _response("Final [policy.md#chunk-0]."),
        ],
    )

    agent.agent_answer("Q?", "policies", max_search_calls=1)

    assert [s["query"] for s in searches] == ["one"]
    refused = json.loads(llm.calls[1]["messages"][-1]["content"])
    assert "budget" in refused["error"]
    assert "agent.tool.refused" in _stages()


def test_repeated_query_reuses_results_but_counts_against_budget(monkeypatch, searches):
    _install(
        monkeypatch,
        [
            _response(tool_calls=[_tool_call("same")]),
            _response(tool_calls=[_tool_call("same")]),
            _response("Final [policy.md#chunk-0]."),
        ],
    )

    result = agent.agent_answer("Q?", "policies", max_search_calls=5)

    assert len(searches) == 1
    assert result["search_calls"] == 2
    assert "agent.tool.repeat" in _stages()


def test_unknown_tool_or_empty_query_is_refused(monkeypatch, searches):
    llm = _install(
        monkeypatch,
        [
            _response(tool_calls=[_tool_call("x", name="delete_everything"), _tool_call("")]),
            _response("Final."),
            _response("Final [policy.md#chunk-0]."),
        ],
    )

    agent.agent_answer("Q?", "policies")

    assert "non-empty" in llm.calls[1]["messages"][-1]["content"]
    # Refused calls do not search; only the forced fallback search runs.
    assert [s["query"] for s in searches] == ["Q?"]


def test_last_step_never_offers_the_tool(monkeypatch, searches):
    llm = _install(
        monkeypatch,
        [_response(tool_calls=[_tool_call("one")]), _response("Final [policy.md#chunk-0].")],
    )

    agent.agent_answer("Q?", "policies", max_steps=2)

    assert llm.calls[1]["tools"] is None


def test_step_budget_exhausted_when_model_keeps_calling_tools(monkeypatch, searches):
    _install(
        monkeypatch,
        [_response(tool_calls=[_tool_call("one")]), _response(tool_calls=[_tool_call("two")])],
    )

    result = agent.agent_answer("Q?", "policies", max_steps=2, max_search_calls=5)

    assert result["stop_reason"] == "step_budget_exhausted"
    assert "step budget" in result["answer"]


def test_search_failure_is_reported_to_the_model_not_raised(monkeypatch, searches):
    def broken(query, k, filters):
        raise RuntimeError("db down")

    monkeypatch.setattr(agent, "hybrid_candidates", broken)
    llm = _install(
        monkeypatch,
        [_response(tool_calls=[_tool_call("q")]), _response("I don't know.")],
    )

    result = agent.agent_answer("Q?", "policies")

    assert result["answer"] == "I don't know."
    assert "search unavailable" in llm.calls[1]["messages"][-1]["content"]
    assert "agent.tool.error" in _stages()


def test_llm_failure_degrades_to_the_standard_pipeline(monkeypatch):
    _install(monkeypatch, [RuntimeError("model does not support tools")])
    fallback_calls = []

    def fake_standard(question, data_folder, k, n, use_reranker):
        fallback_calls.append((question, data_folder, k, n, use_reranker))
        return {"answer": "standard", "context": [], "candidate_count": 0}

    monkeypatch.setattr(agent, "answer_within_trace", fake_standard)

    result = agent.agent_answer("Q?", "policies", k=7, n=3, use_reranker=False)

    assert result["answer"] == "standard"
    assert result["mode"] == "standard-fallback"
    assert result["trace_id"] == observability.current_trace_id()
    assert fallback_calls == [("Q?", "policies", 7, 3, False)]
    assert "agent.degraded" in _stages()


@pytest.mark.parametrize(
    "kwargs", [{"k": 0}, {"n": 0}, {"max_steps": 0}, {"max_search_calls": -1}]
)
def test_agent_rejects_non_positive_limits(kwargs):
    with pytest.raises(ValueError, match="positive integer"):
        agent.agent_answer("Q?", "policies", **kwargs)


def test_search_call_written_as_text_is_recovered_and_executed(monkeypatch, searches):
    text_call = '{"name": "search", "parameters": {"query": "refund window", "k": 2}}'
    llm = _install(
        monkeypatch,
        [_response(f"Let me look. {text_call}"), _response("Five days [policy.md#chunk-0].")],
    )

    result = agent.agent_answer("How long?", "policies")

    assert [s["query"] for s in searches] == ["refund window"]
    assert result["answer"] == "Five days [policy.md#chunk-0]."
    assert result["search_calls"] == 1
    assert llm.calls[1]["messages"][2]["content"] == "Let me look."
    assert "agent.tool.text_call" in _stages()


def test_text_call_is_stripped_from_the_answer_when_tool_is_withheld(monkeypatch, searches):
    text_call = '{"name": "search", "parameters": {"query": "again"}}'
    _install(
        monkeypatch,
        [
            _response(tool_calls=[_tool_call("q")]),
            _response(f"Not enough info [policy.md#chunk-0]. {text_call}"),
        ],
    )

    result = agent.agent_answer("Q?", "policies", max_steps=2)

    assert result["answer"] == "Not enough info [policy.md#chunk-0]."
    assert [s["query"] for s in searches] == ["q"]


def test_non_search_json_in_an_answer_is_left_alone(monkeypatch, searches):
    answer = 'Config: {"name": "retries", "parameters": {"n": 3}} [policy.md#chunk-0] ["search"]'
    _install(monkeypatch, [_response(tool_calls=[_tool_call("q")]), _response(answer)])

    assert agent.agent_answer("Q?", "policies")["answer"] == answer


def test_invalid_k_still_runs_the_search_with_the_default_limit(monkeypatch, searches):
    _install(
        monkeypatch,
        [_response(tool_calls=[_tool_call("q", k="many")]), _response("done [policy.md#chunk-0]")],
    )

    result = agent.agent_answer("Q?", "policies", n=1)

    assert [s["query"] for s in searches] == ["q"]
    assert len(result["context"]) == 1
    assert "agent.tool.invalid_arguments" in _stages()


def test_answer_with_evidence_but_no_citation_is_flagged(monkeypatch, searches):
    _install(
        monkeypatch,
        [
            _response(tool_calls=[_tool_call("q")]),
            _response("Five days."),
            _response("Five days."),
        ],
    )

    result = agent.agent_answer("Q?", "policies")

    assert result["answer"] == "Five days."
    events = observability.trace_events()
    citations = next(e for e in events if e["stage"] == "agent.citations")
    assert citations["missing_citations"] is True
    repair = next(e for e in events if e["stage"] == "agent.citations.repair")
    assert repair["outcome"] == "unchanged"


def test_uncited_answer_is_repaired_with_a_tool_free_turn(monkeypatch, searches):
    llm = _install(
        monkeypatch,
        [
            _response(tool_calls=[_tool_call("q")]),
            _response("Five days."),
            _response("Five days [policy.md#chunk-1]."),
        ],
    )

    result = agent.agent_answer("Q?", "policies")

    assert result["answer"] == "Five days [policy.md#chunk-1]."
    assert result["steps"] == 2
    assert llm.calls[2]["tools"] is None
    request = llm.calls[2]["messages"][-1]["content"]
    assert "[policy.md#chunk-0]" in request and "[policy.md#chunk-1]" in request
    events = observability.trace_events()
    assert next(e for e in events if e["stage"] == "agent.citations.repair")["outcome"] == "repaired"
    citations = next(e for e in events if e["stage"] == "agent.citations")
    assert citations["missing_citations"] is False


def test_repair_may_abstain_when_evidence_does_not_support_an_answer(monkeypatch, searches):
    _install(
        monkeypatch,
        [
            _response(tool_calls=[_tool_call("q")]),
            _response("Paris."),
            _response("I don't know."),
        ],
    )

    assert agent.agent_answer("Q?", "policies")["answer"] == "I don't know."


def test_repair_failure_keeps_the_original_answer(monkeypatch, searches):
    _install(
        monkeypatch,
        [_response(tool_calls=[_tool_call("q")]), _response("Five days."), RuntimeError("down")],
    )

    assert agent.agent_answer("Q?", "policies")["answer"] == "Five days."
    assert "agent.citations.repair" in _stages()


def test_chunks_below_min_rerank_score_are_dropped_from_search_results(monkeypatch):
    monkeypatch.setattr(
        agent,
        "hybrid_candidates",
        lambda query, k, filters: [_chunk(0), _chunk(1), _chunk(2)],
    )
    scored = [
        dict(_chunk(0), rerank_score=0.9),
        dict(_chunk(1), rerank_score=0.0001),
        _chunk(2),
    ]
    monkeypatch.setattr(agent, "select_context", lambda *a, **k: scored)
    monkeypatch.setitem(agent.CONFIG, "min_rerank_score", 0.05)
    llm = _install(
        monkeypatch,
        [_response(tool_calls=[_tool_call("q")]), _response("Yes [policy.md#chunk-0].")],
    )

    result = agent.agent_answer("Q?", "policies")

    assert [c["chunk_index"] for c in result["context"]] == [0, 2]
    markers = [r["marker"] for r in json.loads(llm.calls[1]["messages"][-1]["content"])["results"]]
    assert markers == ["policy.md#chunk-0", "policy.md#chunk-2"]
    assert "selection.relevance_filter" in _stages()


def test_all_chunks_irrelevant_leaves_the_model_with_no_results(monkeypatch):
    monkeypatch.setattr(agent, "hybrid_candidates", lambda query, k, filters: [_chunk(0)])
    monkeypatch.setattr(
        agent, "select_context", lambda *a, **k: [dict(_chunk(0), rerank_score=0.0)]
    )
    monkeypatch.setitem(agent.CONFIG, "min_rerank_score", 0.05)
    llm = _install(
        monkeypatch,
        [_response(tool_calls=[_tool_call("capital of France")]), _response("I don't know.")],
    )

    result = agent.agent_answer("Q?", "policies")

    assert result["context"] == []
    payload = json.loads(llm.calls[1]["messages"][-1]["content"])
    assert payload["results"] == []
    assert "No relevant chunks" in payload["note"]


def test_relevance_filter_can_be_disabled(monkeypatch):
    monkeypatch.setattr(agent, "hybrid_candidates", lambda query, k, filters: [_chunk(0)])
    monkeypatch.setattr(
        agent, "select_context", lambda *a, **k: [dict(_chunk(0), rerank_score=0.0)]
    )
    monkeypatch.setitem(agent.CONFIG, "min_rerank_score", 0.0)
    _install(
        monkeypatch,
        [_response(tool_calls=[_tool_call("q")]), _response("Yes [policy.md#chunk-0].")],
    )

    assert len(agent.agent_answer("Q?", "policies")["context"]) == 1


def _scored_by_query(monkeypatch, scores):
    """Fake retrieval where each query only finds the chunk it is about."""
    chunks = {q: dict(_chunk(i), chunk_id=i) for i, q in enumerate(scores)}
    monkeypatch.setattr(agent, "hybrid_candidates", lambda query, k, filters: [chunks.get(query, _chunk(9))])

    def fake_select(candidates, n, use_reranker, query):
        return [dict(c, rerank_score=scores.get(query, 0.0)) for c in candidates]

    monkeypatch.setattr(agent, "select_context", fake_select)
    monkeypatch.setitem(agent.CONFIG, "min_rerank_score", 0.05)


def test_compound_query_with_no_relevant_chunks_is_retried_as_sub_queries(monkeypatch):
    _scored_by_query(monkeypatch, {"refunds": 0.9, "vpn": 0.4})
    monkeypatch.setattr(agent, "_decompose", lambda query: ["refunds", "vpn"])
    llm = _install(
        monkeypatch,
        [
            _response(tool_calls=[_tool_call("refunds and vpn", k=1)]),
            _response("Both [policy.md#chunk-0] [policy.md#chunk-1]."),
        ],
    )

    result = agent.agent_answer("Q?", "policies", max_search_calls=1)

    assert [c["chunk_index"] for c in result["context"]] == [0, 1]
    payload = json.loads(llm.calls[1]["messages"][-1]["content"])
    assert [r["marker"] for r in payload["results"]] == ["policy.md#chunk-0", "policy.md#chunk-1"]
    assert "agent.search.decomposed" in _stages()


def test_decomposition_is_skipped_when_the_first_search_finds_something(monkeypatch, searches):
    monkeypatch.setattr(
        agent, "_decompose", lambda query: pytest.fail("must not decompose after a hit")
    )
    _install(
        monkeypatch,
        [_response(tool_calls=[_tool_call("q")]), _response("Yes [policy.md#chunk-0].")],
    )

    agent.agent_answer("Q?", "policies")


def test_decompose_ignores_single_or_failed_decomposition(monkeypatch):
    import types
    import sys

    module = types.ModuleType("src.retrieve.query_transform")
    module.decompose = lambda query: [query]
    monkeypatch.setitem(sys.modules, "src.retrieve.query_transform", module)
    observability.new_trace()

    assert REAL_DECOMPOSE("capital of France") == []

    def broken(query):
        raise RuntimeError("ollama down")

    module.decompose = broken
    assert REAL_DECOMPOSE("a and b") == []
    assert "agent.search.decompose_failed" in _stages()

    module.decompose = lambda query: ["a", "b", "b", "c", "d"]
    assert REAL_DECOMPOSE("a and b and c and d") == ["a", "b", "c"]


def test_standard_answer_marks_its_mode(monkeypatch):
    monkeypatch.setattr(pipeline, "hybrid_candidates", lambda q, k, filters: [])

    pipeline.answer("Q?", "policies")

    start = next(e for e in observability.trace_events() if e["stage"] == "request.start")
    assert start["mode"] == "standard"
