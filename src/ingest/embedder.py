# embedder.py - Batch embedding with retry
from sentence_transformers import SentenceTransformer
import time
import random

from ..config import CONFIG

model = SentenceTransformer(CONFIG["embedding_model"])


def embed_chunks(texts: list[str], batch_size: int | None = None) -> list[list[float]]:
    """Embed a list of texts in batches. Returns list of vectors."""
    if batch_size is None:
        batch_size = CONFIG["embed_batch_size"]
    if batch_size <= 0:
        raise ValueError("batch_size must be a positive integer")
    all_embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        embeddings = model.encode(batch, show_progress_bar=False)
        all_embeddings.extend(embeddings.tolist())
    return all_embeddings


def embed_chunks_with_retry(
    texts: list[str],
    batch_size: int | None = None,
    max_retries: int | None = None,
) -> list[list[float]]:
    """Embed texts in batches with exponential backoff on failure."""
    if batch_size is None:
        batch_size = CONFIG["embed_batch_size"]
    if batch_size <= 0:
        raise ValueError("batch_size must be a positive integer")
    if max_retries is None:
        max_retries = CONFIG["embed_max_retries"]
    if max_retries < 0:
        raise ValueError("max_retries must be non-negative")
    all_embeddings = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        retries = 0

        while retries <= max_retries:
            try:
                embeddings = model.encode(batch, show_progress_bar=False)
                all_embeddings.extend(embeddings.tolist())
                break
            except Exception as e:
                retries += 1
                if retries > max_retries:
                    raise RuntimeError(
                        f"Failed to embed batch {i // batch_size} "
                        f"after {max_retries} retries: {e}"
                    )
                wait = (2 ** retries) + random.uniform(0, 1)
                print(
                    f"Batch {i // batch_size} failed (attempt {retries}), "
                    f"retrying in {wait:.1f}s: {e}"
                )
                time.sleep(wait)

    return all_embeddings