# pipeline.py - End-to-end RAG with optional reranking and graceful degradation
import logging

from ollama import Client

from .hybrid import hybrid_candidates
from ..config import CONFIG
from ..observability import log_event, new_trace, span

logger = logging.getLogger(__name__)

ollama_client = Client(host=CONFIG["ollama_host"])

LLM_MODEL = CONFIG["llm_model"]
NO_INDEXED_REFERENCES_MESSAGE = (
    "No indexed references found. Ingest documents before asking questions."
)

PROMPT_TEMPLATE = """You are an internal assistant. Answer the question using only the context below.

Rules:
- Use only the information in the numbered context blocks. Do not rely on outside knowledge.
- Cite each fact with the exact source marker shown in brackets, including the chunk identifier, e.g. [hipaa_compliance_overview.md#chunk-6].
- Only cite markers that appear in the context below. Do not cite a document at file level; the chunk identifier is required.
- If the context does not contain enough information to answer the question, reply exactly: "I don't know."

Context:
{context}

Question: {question}

Answer:"""


def _positive_limit(value: int, name: str) -> int:
    if value <= 0:
        raise ValueError(f"{name} must be a positive integer")
    return value


def _interleave(candidates: list[dict], n: int) -> list[dict]:
    kw = sorted(
        [c for c in candidates if c["keyword_rank"] is not None],
        key=lambda c: c["keyword_rank"],
    )
    sem = sorted(
        [c for c in candidates if c["semantic_rank"] is not None],
        key=lambda c: c["semantic_rank"],
    )
    selected: list[dict] = []
    seen: set[int] = set()
    for kw_c, sem_c in zip(kw, sem):
        for c in (kw_c, sem_c):
            if c["chunk_id"] not in seen:
                selected.append(c)
                seen.add(c["chunk_id"])
            if len(selected) >= n:
                return selected
    for c in kw + sem:
        if c["chunk_id"] not in seen:
            selected.append(c)
            seen.add(c["chunk_id"])
        if len(selected) >= n:
            break
    return selected


def select_context(
    candidates: list[dict],
    n: int | None = None,
    use_reranker: bool = True,
    query: str = "",
) -> list[dict]:
    """Pick top-N chunks, reranking with a cross-encoder when enabled.

    If the reranker is unavailable or fails, fall back to rank interleaving so the
    request still succeeds.
    """
    if n is None:
        n = CONFIG["context_n"]
    n = _positive_limit(n, "n")
    if use_reranker:
        try:
            if CONFIG["force_reranker_failure"]:
                raise RuntimeError("Simulated reranker outage")
            from .reranker import rerank

            return rerank(query, candidates, top_n=n)
        except Exception as exc:
            logger.warning("Reranker unavailable, falling back to interleaving: %s", exc)
            log_event("selection.rerank.degraded", error=repr(exc), fallback="interleave")
    return _interleave(candidates, n)


def build_prompt(question: str, chunks: list[dict]) -> str:
    blocks = [
        f"{i}. [{c['source_file']}#chunk-{c['chunk_index']}] {c['content']}"
        for i, c in enumerate(chunks, start=1)
    ]
    return PROMPT_TEMPLATE.format(context="\n\n".join(blocks), question=question)


def _retrieval_query(question: str) -> str:
    """Optionally rewrite the question for retrieval; fall back to the original on failure."""
    if not CONFIG["use_query_transform"]:
        return question
    try:
        from .query_transform import rewrite

        with span("query_transform.rewrite"):
            rewritten = rewrite(question)
        return rewritten or question
    except Exception as exc:
        logger.warning("Query rewrite failed, using the original question: %s", exc)
        log_event("query_transform.degraded", error=repr(exc))
        return question


def answer(
    question: str,
    data_folder: str,
    k: int | None = None,
    n: int | None = None,
    use_reranker: bool | None = None,
) -> dict:
    if k is None:
        k = CONFIG["candidate_k"]
    if n is None:
        n = CONFIG["context_n"]
    k = _positive_limit(k, "k")
    n = _positive_limit(n, "n")
    if use_reranker is None:
        use_reranker = CONFIG["use_reranker"]

    new_trace()
    log_event(
        "request.start",
        mode="standard",
        question_chars=len(question),
        data_folder=data_folder,
        k=k,
        n=n,
        use_reranker=use_reranker,
        embedding_model=CONFIG["embedding_model"],
        reranker_model=CONFIG["reranker_model"],
        llm_model=LLM_MODEL,
    )
    return answer_within_trace(question, data_folder, k, n, use_reranker)


def answer_within_trace(
    question: str, data_folder: str, k: int, n: int, use_reranker: bool
) -> dict:
    """Run the single-pass pipeline inside the caller's trace (no new trace is started)."""
    retrieval_query = _retrieval_query(question)
    with span("retrieval.hybrid", k=k):
        candidates = hybrid_candidates(
            retrieval_query, k=k, filters={"data_folder": data_folder}
        )
    log_event("retrieval.candidates", candidate_count=len(candidates))
    if not candidates:
        log_event("request.empty_index")
        return {
            "answer": NO_INDEXED_REFERENCES_MESSAGE,
            "context": [],
            "candidate_count": 0,
        }

    with span(
        "selection.context",
        method="rerank" if use_reranker else "interleave",
        input_count=len(candidates),
        top_n=n,
    ):
        chunks = select_context(
            candidates, n=n, use_reranker=use_reranker, query=retrieval_query
        )
    prompt = build_prompt(question, chunks)
    # response = client.chat.completions.create(
    #     model=JUDGE_MODEL,
    #     messages=[{"role": "user", "content": prompt}],
    #     temperature=0,
    # )
    with span("generation.llm", model=LLM_MODEL, context_count=len(chunks)):
        response = ollama_client.chat(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0},
        )

    answer_text = response.message.content.strip()
    log_event(
        "generation.complete",
        prompt_chars=len(prompt),
        answer_chars=len(answer_text),
    )

    return {
        #"answer": response.choices[0].message.content.strip(),
        "answer": answer_text,
        "context": chunks,
        "candidate_count": len(candidates),
    }