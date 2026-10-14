# embedder.py - Embed queries with the same model used during ingestion
from sentence_transformers import SentenceTransformer

from ..config import CONFIG

model = SentenceTransformer(CONFIG["embedding_model"])


def embed_query(text: str) -> list[float]:
    return model.encode(text).tolist()