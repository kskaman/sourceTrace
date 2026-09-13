# reranker.py - Cross-encoder reranking with BAAI/bge-reranker-v2-m3
from sentence_transformers import CrossEncoder

# Loaded once on import. First run downloads the model (~600 MB).
_model = CrossEncoder("BAAI/bge-reranker-v2-m3")


def rerank(query: str, candidates: list[dict], top_n: int = 5) -> list[dict]:
    """Score each (query, chunk) pair with the cross-encoder, return top_n."""
    if not candidates:
        return []

    pairs = [(query, c["content"]) for c in candidates]
    scores = _model.predict(pairs, show_progress_bar=False)

    scored = [dict(c, rerank_score=float(s)) for c, s in zip(candidates, scores)]
    scored.sort(key=lambda c: c["rerank_score"], reverse=True)
    return scored[:top_n]