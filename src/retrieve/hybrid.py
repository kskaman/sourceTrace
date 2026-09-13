# hybrid.py - Hybrid candidate retrieval (copied from ch06; chapters are self-contained)
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.database import get_connection


def _build_filter_sql(filters: dict | None) -> tuple[str, list]:
    if not filters:
        return "", []
    clauses = [f"{col} = %s" for col in filters]
    return " AND ".join(clauses), list(filters.values())


def keyword_search(query: str, k: int = 20, filters: dict | None = None) -> list[dict]:
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

    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(sql, params)
        rows = cur.fetchall()
    conn.close()

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

    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute(sql, params)
        rows = cur.fetchall()
    conn.close()

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


def hybrid_candidates(query: str, k: int = 20, filters: dict | None = None) -> list[dict]:
    kw = keyword_search(query, k=k, filters=filters)
    sem = semantic_search(query, k=k, filters=filters)

    by_id: dict[int, dict] = {c["chunk_id"]: dict(c) for c in kw}
    for c in sem:
        if c["chunk_id"] in by_id:
            existing = by_id[c["chunk_id"]]
            existing["semantic_rank"] = c["semantic_rank"]
            existing["semantic_score"] = c["semantic_score"]
            existing["matched_by"] = "both"
        else:
            by_id[c["chunk_id"]] = dict(c)

    return list(by_id.values())