# embedder.py - Embed queries with the same model used during ingestion
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")


def embed_query(text: str) -> list[float]:
    return model.encode(text).tolist()