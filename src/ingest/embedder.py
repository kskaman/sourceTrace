# embedder.py - Batch embedding with retry
from sentence_transformers import SentenceTransformer
import time
import random

model = SentenceTransformer("all-MiniLM-L6-v2")


def embed_chunks(texts: list[str], batch_size: int = 64) -> list[list[float]]:
    """Embed a list of texts in batches. Returns list of vectors."""
    all_embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        embeddings = model.encode(batch, show_progress_bar=False)
        all_embeddings.extend(embeddings.tolist())
    return all_embeddings


def embed_chunks_with_retry(
    texts: list[str],
    batch_size: int = 64,
    max_retries: int = 3,
) -> list[list[float]]:
    """Embed texts in batches with exponential backoff on failure."""
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