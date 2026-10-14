# hybrid.py - Hybrid candidate retrieval with graceful degradation
import logging

from src.config import CONFIG
from src.database import get_connection
from src.observability import log_event, span

logger = logging.getLogger(__name__)


class RetrievalUnavailableError(RuntimeError):
    """Both keyword and semantic retrieval failed."""


def _require_positive_k(k: int) -> None:
    if k <= 0:
        raise ValueError("k must be a positive integer")


def _fetch_rows(sql: str, params: list) -> list:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()
    finally:
        conn.close()


def _build_filter_sql(filters: dict | None) -> tuple[str, list]:
    if not filters:
        return "", []
    clauses = [f"{col} = %s" for col in filters]
    return " AND ".join(clauses), list(filters.values())


def keyword_search(query: str, k: int = 20, filters: dict | None = None) -> list[dict]:
    _require_positive_k(k)
    filter_sql, filter_params = _build_filter_sql(filters)
    where = "search_vector @@ websearch_to_tsquery('english', %s)"
    if filter_sql:
        where += " AND " + filter_sql

    sql = f"""
        SELECT id, content, source_file, doc_type, category, chunk_index, page_number,
               ts_rank_cd(search_vector, websearch_to_tsquery('english', %s)) AS score
        FROM chunks
        WHERE {where}
        ORDER BY score DESC
        LIMIT %s
    """
    params = [query, query, *filter_params, k]

    rows = _fetch_rows(sql, params)

    return [
        {
            "chunk_id": row[0],
            "content": row[1],
            "source_file": row[2],
            "doc_type": row[3],
            "category": row[4],
            "chunk_index": row[5],
            "page_number": row[6],
            "keyword_rank": rank + 1,
            "keyword_score": float(row[7]),
            "semantic_rank": None,
            "semantic_score": None,
            "matched_by": "keyword",
        }
        for rank, row in enumerate(rows)
    ]


def semantic_search(query: str, k: int = 20, filters: dict | None = None) -> list[dict]:
    _require_positive_k(k)
    from .embedder import embed_query

    embedding = embed_query(query)
    filter_sql, filter_params = _build_filter_sql(filters)
    where = ("WHERE " + filter_sql) if filter_sql else ""

    sql = f"""
        SELECT id, content, source_file, doc_type, category, chunk_index, page_number,
               1 - (embedding <=> %s::vector) AS score
        FROM chunks
        {where}
        ORDER BY embedding <=> %s::vector
        LIMIT %s
    """
    params = [embedding, *filter_params, embedding, k]

    rows = _fetch_rows(sql, params)

    return [
        {
            "chunk_id": row[0],
            "content": row[1],
            "source_file": row[2],
            "doc_type": row[3],
            "category": row[4],
            "chunk_index": row[5],
            "page_number": row[6],
            "keyword_rank": None,
            "keyword_score": None,
            "semantic_rank": rank + 1,
            "semantic_score": float(row[7]),
            "matched_by": "semantic",
        }
        for rank, row in enumerate(rows)
    ]


def _guarded_search(stage, search, forced_failure, query, k, filters):
    """Run one search leg; return (results, None) or (None, error) instead of raising."""
    try:
        if forced_failure:
            raise RuntimeError(f"Simulated {stage} search outage")
        with span(f"retrieval.{stage}", k=k):
            return search(query, k=k, filters=filters), None
    except Exception as exc:
        logger.warning("%s search failed, continuing without it: %s", stage, exc)
        log_event(f"retrieval.{stage}.degraded", error=repr(exc))
        return None, exc


def hybrid_candidates(query: str, k: int = 20, filters: dict | None = None) -> list[dict]:
    _require_positive_k(k)
    kw, kw_error = _guarded_search(
        "keyword", keyword_search, CONFIG["force_keyword_failure"], query, k, filters
    )
    sem, sem_error = _guarded_search(
        "semantic", semantic_search, CONFIG["force_semantic_failure"], query, k, filters
    )
    if kw_error and sem_error:
        raise RetrievalUnavailableError(
            f"Keyword search failed ({kw_error}) and semantic search failed ({sem_error})"
        ) from sem_error
    kw = kw or []
    sem = sem or []

    by_id: dict[int, dict] = {c["chunk_id"]: dict(c) for c in kw}
    for c in sem:
        if c["chunk_id"] in by_id:
            existing = by_id[c["chunk_id"]]
            existing["semantic_rank"] = c["semantic_rank"]
            existing["semantic_score"] = c["semantic_score"]
            existing["matched_by"] = "both"
        else:
            by_id[c["chunk_id"]] = dict(c)

    log_event(
        "retrieval.merge",
        keyword_count=len(kw),
        semantic_count=len(sem),
        merged_count=len(by_id),
        overlap_count=len(kw) + len(sem) - len(by_id),
    )
    return list(by_id.values())