# agent.py - Agentic RAG: the LLM decides when and what to retrieve via a bounded tool loop
import json
import logging
import re
from types import SimpleNamespace

from ollama import Client

from .hybrid import hybrid_candidates
from .pipeline import (
    _positive_limit,
    answer_within_trace,
    select_context,
)
from ..config import CONFIG
from ..observability import log_event, new_trace, span

logger = logging.getLogger(__name__)

ollama_client = Client(host=CONFIG["ollama_host"])

LLM_MODEL = CONFIG["llm_model"]
CONTENT_EXCERPT_CHARS = 800
MAX_SUB_QUERIES = 3
INSUFFICIENT_ANSWER = "I don't know."
CITATION_PATTERN = re.compile(r"\[([^\[\]#]+#chunk-\d+)\]")

SYSTEM_PROMPT = """You are an internal assistant. To answer the user's question, call the `search` tool to retrieve relevant chunks from the knowledge base. You may call `search` several times. If the question has several parts or compares topics, search for each part separately with a short, focused query instead of one combined query.

When you have enough evidence to answer:
- Use only the chunks returned by your search calls. Do not rely on outside knowledge.
- Cite each fact with the exact marker returned with the chunk, including the chunk identifier, e.g. [hipaa_compliance_overview.md#chunk-6].
- Only cite markers that were returned by a search call.
- If the evidence is insufficient, reply exactly: "I don't know."

Do not call `search` again after you have produced the final answer."""

SEARCH_TOOL = {
    "type": "function",
    "function": {
        "name": "search",
        "description": (
            "Search the internal knowledge base. Returns the most relevant chunks, "
            "each with a citation marker and a content excerpt."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query in natural language",
                },
                "k": {
                    "type": "integer",
                    "description": "Number of chunks to return",
                },
            },
            "required": ["query"],
        },
    },
}


def chunk_marker(chunk: dict) -> str:
    return f"{chunk['source_file']}#chunk-{chunk['chunk_index']}"


def _serialise_chunks(chunks: list[dict]) -> str:
    """Compact tool-result payload handed back to the LLM."""
    payload: dict = {
        "results": [
            {"marker": chunk_marker(c), "content": c["content"][:CONTENT_EXCERPT_CHARS]}
            for c in chunks
        ]
    }
    if not chunks:
        payload["note"] = (
            "No relevant chunks found for this query. If it covers several topics, search "
            "each topic separately; otherwise answer that you don't know."
        )
    return json.dumps(payload)


def _parse_arguments(raw) -> dict:
    if isinstance(raw, str):
        raw = json.loads(raw or "{}")
    return dict(raw or {})


def _search_once(
    query: str,
    top_n: int,
    data_folder: str,
    candidate_k: int,
    use_reranker: bool,
) -> list[dict]:
    with span("retrieval.hybrid", k=candidate_k):
        candidates = hybrid_candidates(
            query, k=candidate_k, filters={"data_folder": data_folder}
        )
    log_event("retrieval.candidates", candidate_count=len(candidates))
    if not candidates:
        return []
    with span(
        "selection.context",
        method="rerank" if use_reranker else "interleave",
        input_count=len(candidates),
        top_n=top_n,
    ):
        return _drop_irrelevant(
            select_context(candidates, n=top_n, use_reranker=use_reranker, query=query)
        )


def _decompose(query: str) -> list[str]:
    """Split a compound query into focused sub-queries; empty when it is not compound."""
    try:
        from .query_transform import decompose

        with span("agent.search.decompose"):
            parts = decompose(query)
    except Exception as exc:
        log_event("agent.search.decompose_failed", error=repr(exc))
        return []
    unique = list(dict.fromkeys(p for p in parts if p and p != query))
    return unique[:MAX_SUB_QUERIES] if len(unique) >= 2 else []


def _run_search(
    query: str,
    k: int,
    data_folder: str,
    candidate_k: int,
    max_chunks: int,
    use_reranker: bool,
    question: str,
) -> list[dict]:
    """Hybrid retrieval scoped to the data folder, then rerank (or interleave) to k chunks.

    If nothing relevant is found and the user's question is compound, it is retried as
    separate sub-questions: a combined query dilutes the reranker score of each topic.
    """
    top_n = min(max(k, 1), max_chunks)
    chunks = _search_once(query, top_n, data_folder, candidate_k, use_reranker)
    if chunks:
        return chunks
    sub_queries = _decompose(question)
    if not sub_queries:
        return []
    log_event("agent.search.decomposed", sub_query_count=len(sub_queries))
    merged: dict[int, dict] = {}
    for sub_query in sub_queries:
        for chunk in _search_once(sub_query, top_n, data_folder, candidate_k, use_reranker):
            merged.setdefault(chunk["chunk_id"], chunk)
    ranked = sorted(merged.values(), key=lambda c: c.get("rerank_score", 0.0), reverse=True)
    return ranked[:max_chunks]


def _drop_irrelevant(chunks: list[dict]) -> list[dict]:
    """Drop chunks whose rerank score is below MIN_RERANK_SCORE; unscored chunks are kept."""
    min_score = CONFIG["min_rerank_score"]
    if min_score <= 0:
        return chunks
    relevant = [c for c in chunks if c.get("rerank_score", 1.0) >= min_score]
    if len(relevant) < len(chunks):
        log_event(
            "selection.relevance_filter",
            min_score=min_score,
            kept=len(relevant),
            dropped=len(chunks) - len(relevant),
        )
    return relevant


def _assistant_message(content: str, tool_calls) -> dict:
    entry: dict = {"role": "assistant", "content": content}
    if tool_calls:
        entry["tool_calls"] = [
            {
                "function": {
                    "name": tc.function.name,
                    "arguments": _parse_arguments(tc.function.arguments),
                }
            }
            for tc in tool_calls
        ]
    return entry


def _extract_text_tool_calls(content: str) -> tuple[str, list]:
    """Pull `search` calls that a small model wrote as JSON text instead of a real tool call.

    Returns the content with those JSON objects removed and the recovered calls.
    """
    decoder = json.JSONDecoder()
    calls: list = []
    kept: list[str] = []
    pos = 0
    i = content.find("{")
    while i != -1:
        try:
            obj, end = decoder.raw_decode(content, i)
        except ValueError:
            i = content.find("{", i + 1)
            continue
        arguments = obj.get("parameters", obj.get("arguments")) if isinstance(obj, dict) else None
        if isinstance(arguments, dict) and obj.get("name") == "search":
            calls.append(
                SimpleNamespace(function=SimpleNamespace(name="search", arguments=arguments))
            )
            kept.append(content[pos:i])
            pos = end
            i = content.find("{", end)
        else:
            i = content.find("{", i + 1)
    kept.append(content[pos:])
    return "".join(kept).strip(), calls


def _citation_status(answer_text: str, evidence: dict[str, dict]) -> tuple[list[str], list[str]]:
    cited = sorted(set(CITATION_PATTERN.findall(answer_text)))
    return cited, [marker for marker in cited if marker not in evidence]


def _needs_citations(answer_text: str, evidence: dict[str, dict]) -> bool:
    """True when evidence was retrieved but the answer lacks a valid, fully grounded citation."""
    if not evidence or answer_text == INSUFFICIENT_ANSWER:
        return False
    cited, unknown = _citation_status(answer_text, evidence)
    return not cited or bool(unknown)


def _log_citations(answer_text: str, evidence: dict[str, dict]) -> None:
    """Record which cited markers were actually retrieved, to expose ungrounded citations."""
    cited, unknown = _citation_status(answer_text, evidence)
    log_event(
        "agent.citations",
        cited_count=len(cited),
        ungrounded_count=len(unknown),
        ungrounded=unknown,
        missing_citations=_needs_citations(answer_text, evidence) and not cited,
    )


def _repair_citations(
    messages: list[dict], answer_text: str, evidence: dict[str, dict], step: int
) -> str:
    """Give the model one tool-free turn to add valid citations; keep the original on failure."""
    if not _needs_citations(answer_text, evidence):
        return answer_text
    markers = ", ".join(f"[{m}]" for m in evidence)
    request = (
        "Rewrite your answer so every fact is followed by the exact marker of the chunk it "
        f"came from. Allowed markers: {markers}. Use only the retrieved chunks. "
        f'If they do not support an answer, reply exactly: "{INSUFFICIENT_ANSWER}"'
    )
    try:
        with span("agent.llm", step=step, model=LLM_MODEL, tools_offered=False, repair=True):
            response = ollama_client.chat(
                model=LLM_MODEL,
                messages=[*messages, {"role": "user", "content": request}],
                tools=None,
                options={"temperature": 0},
            )
    except Exception as exc:
        log_event("agent.citations.repair", outcome="error", error=repr(exc))
        return answer_text
    repaired = (response.message.content or "").strip()
    log_event(
        "agent.llm.result",
        step=step,
        repair=True,
        tool_call_count=0,
        prompt_tokens=getattr(response, "prompt_eval_count", None),
        completion_tokens=getattr(response, "eval_count", None),
    )
    if repaired and not _needs_citations(repaired, evidence):
        log_event("agent.citations.repair", outcome="repaired")
        return repaired
    log_event("agent.citations.repair", outcome="unchanged")
    return answer_text


def agent_answer(
    question: str,
    data_folder: str,
    k: int | None = None,
    n: int | None = None,
    use_reranker: bool | None = None,
    max_steps: int | None = None,
    max_search_calls: int | None = None,
) -> dict:
    """Answer a question with a bounded tool-calling loop.

    `k` is the candidate pool per search, `n` the maximum chunks one search returns.
    If the LLM cannot run the tool loop, the request degrades to the standard pipeline.
    """
    k = _positive_limit(CONFIG["candidate_k"] if k is None else k, "k")
    n = _positive_limit(CONFIG["context_n"] if n is None else n, "n")
    max_steps = _positive_limit(
        CONFIG["agent_max_steps"] if max_steps is None else max_steps, "max_steps"
    )
    max_search_calls = _positive_limit(
        CONFIG["agent_max_search_calls"] if max_search_calls is None else max_search_calls,
        "max_search_calls",
    )
    if use_reranker is None:
        use_reranker = CONFIG["use_reranker"]

    trace_id = new_trace()
    log_event(
        "request.start",
        mode="agent",
        question_chars=len(question),
        data_folder=data_folder,
        k=k,
        n=n,
        use_reranker=use_reranker,
        max_steps=max_steps,
        max_search_calls=max_search_calls,
        embedding_model=CONFIG["embedding_model"],
        reranker_model=CONFIG["reranker_model"],
        llm_model=LLM_MODEL,
    )

    messages: list[dict] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]
    evidence: dict[str, dict] = {}
    searched: dict[str, str] = {}
    search_calls = 0

    def result(answer_text: str, steps: int, stop_reason: str) -> dict:
        log_event(
            "agent.final",
            steps=steps,
            search_calls=search_calls,
            evidence_count=len(evidence),
            stop_reason=stop_reason,
            answer_chars=len(answer_text),
        )
        return {
            "answer": answer_text,
            "context": list(evidence.values()),
            "candidate_count": len(evidence),
            "trace_id": trace_id,
            "mode": "agent",
            "steps": steps,
            "search_calls": search_calls,
            "stop_reason": stop_reason,
        }

    for step in range(1, max_steps + 1):
        # Withhold the tool on the last step or once the search budget is spent, so the
        # model must answer instead of looping.
        offer_tool = step < max_steps and search_calls < max_search_calls
        try:
            with span("agent.llm", step=step, model=LLM_MODEL, tools_offered=offer_tool):
                response = ollama_client.chat(
                    model=LLM_MODEL,
                    messages=messages,
                    tools=[SEARCH_TOOL] if offer_tool else None,
                    options={"temperature": 0},
                )
        except Exception as exc:
            logger.warning("Agent loop unavailable, using the standard pipeline: %s", exc)
            log_event("agent.degraded", step=step, error=repr(exc), fallback="standard")
            fallback = answer_within_trace(question, data_folder, k, n, use_reranker)
            return {**fallback, "trace_id": trace_id, "mode": "standard-fallback"}

        message = response.message
        content = message.content or ""
        tool_calls = message.tool_calls or []
        if not tool_calls and '"search"' in content:
            content, recovered = _extract_text_tool_calls(content)
            if recovered:
                log_event(
                    "agent.tool.text_call",
                    step=step,
                    call_count=len(recovered),
                    honored=offer_tool,
                )
                if offer_tool:
                    tool_calls = recovered
        log_event(
            "agent.llm.result",
            step=step,
            tool_call_count=len(tool_calls),
            prompt_tokens=getattr(response, "prompt_eval_count", None),
            completion_tokens=getattr(response, "eval_count", None),
        )
        if not tool_calls and search_calls == 0 and offer_tool:
            # The model answered from its own knowledge; ground it by searching the question.
            log_event("agent.forced_search", step=step)
            content = ""
            tool_calls = [
                SimpleNamespace(
                    function=SimpleNamespace(name="search", arguments={"query": question})
                )
            ]
        messages.append(_assistant_message(content, tool_calls))

        if not tool_calls:
            answer_text = content.strip() or INSUFFICIENT_ANSWER
            if not evidence:
                if answer_text != INSUFFICIENT_ANSWER:
                    log_event("agent.answer_blocked", step=step, reason="no_evidence")
                return result(INSUFFICIENT_ANSWER, step, "no_evidence")
            answer_text = _repair_citations(messages, answer_text, evidence, step)
            _log_citations(answer_text, evidence)
            return result(answer_text, step, "answered")

        for call in tool_calls:
            name = call.function.name
            query, tool_k = "", n
            try:
                args = _parse_arguments(call.function.arguments)
                query = str(args.get("query", "")).strip()
                tool_k = int(args.get("k") or n)
            except (ValueError, TypeError) as exc:
                log_event("agent.tool.invalid_arguments", step=step, error=repr(exc))

            if name != "search" or not query:
                text = json.dumps({"error": "call `search` with a non-empty `query`"})
                log_event("agent.tool.refused", step=step, tool=name, reason="invalid_call")
            elif search_calls >= max_search_calls:
                text = json.dumps({"error": "search call budget exhausted; answer now"})
                log_event(
                    "agent.tool.refused", step=step, query=query,
                    reason="search_budget_exhausted",
                )
            else:
                search_calls += 1
                if query in searched:
                    text = searched[query]
                    log_event("agent.tool.repeat", step=step, query=query)
                else:
                    try:
                        with span("agent.tool.search", step=step, query=query, k=tool_k):
                            chunks = _run_search(
                                query, tool_k, data_folder, k, n, use_reranker, question
                            )
                    except Exception as exc:
                        logger.warning("Agent search failed: %s", exc)
                        log_event("agent.tool.error", step=step, query=query, error=repr(exc))
                        text = json.dumps({"error": f"search unavailable: {exc}"})
                    else:
                        for chunk in chunks:
                            evidence.setdefault(chunk_marker(chunk), chunk)
                        text = _serialise_chunks(chunks)
                        searched[query] = text
                        log_event(
                            "agent.tool.result", step=step, query=query,
                            chunk_count=len(chunks),
                            markers=[chunk_marker(c) for c in chunks],
                            evidence_count=len(evidence),
                        )
            messages.append({"role": "tool", "tool_name": name, "content": text})

    return result(
        "I reached the step budget without finishing.", max_steps, "step_budget_exhausted"
    )
