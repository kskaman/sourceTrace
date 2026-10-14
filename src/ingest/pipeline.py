# pipeline.py - End-to-end ingestion pipeline
import hashlib
import logging
import sys
from pathlib import Path
from datetime import datetime, timezone

from .document_parser import parse_document
from .text_cleaner import clean_text
from .embedder import embed_chunks_with_retry
from ..config import CONFIG
from ..observability import span
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def recursive_split(text, chunk_size=None, overlap=None):
    """Simple recursive character splitter (from chapter 3)."""
    if chunk_size is None:
        chunk_size = CONFIG["chunk_size"]
    if overlap is None:
        overlap = CONFIG["chunk_overlap"]
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if overlap < 0:
        raise ValueError("overlap must be non-negative")
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")
    separators = ["\n\n", "\n", ". ", " "]

    if len(text) <= chunk_size:
        return [text] if text.strip() else []

    for sep in separators:
        parts = text.split(sep)
        if len(parts) <= 1:
            continue

        chunks = []
        current = parts[0]
        for part in parts[1:]:
            candidate = current + sep + part
            if len(candidate) <= chunk_size:
                current = candidate
            else:
                if current.strip():
                    chunks.append(current.strip())
                current = part
        if current.strip():
            chunks.append(current.strip())

        if chunks:
            bounded_chunks = []
            for chunk in chunks:
                if len(chunk) > chunk_size:
                    bounded_chunks.extend(recursive_split(chunk, chunk_size, overlap))
                else:
                    bounded_chunks.append(chunk)
            return bounded_chunks

    # Fallback: hard split
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


def compute_file_hash(file_path: Path) -> str:
    """Compute SHA-256 hash of a file's contents."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for block in iter(lambda: f.read(8192), b""):
            sha256.update(block)
    return sha256.hexdigest()


def ingest_file(
    file_path: Path,
    conn,
    data_folder: str,
    *,
    commit: bool = True,
    doc_hash: str | None = None,
) -> dict:
    """Process a single file through the full pipeline."""
    file_path = Path(file_path)
    logger.info(f"Processing: {file_path.name}")

    # Step 1: Parse
    with span("ingest.parse", file=file_path.name):
        parsed = parse_document(file_path)
    if not parsed.text.strip():
        logger.warning(f"Skipping {file_path.name}: no text extracted")
        return {"file": file_path.name, "status": "skipped", "reason": "empty"}

    # Step 2: Clean
    with span("ingest.clean", input_chars=len(parsed.text)):
        cleaned_text = clean_text(parsed.text)
    if not cleaned_text:
        logger.warning(f"Skipping {file_path.name}: empty after cleaning")
        return {"file": file_path.name, "status": "skipped", "reason": "empty_after_clean"}

    # Step 3: Chunk
    with span("ingest.chunk", input_chars=len(cleaned_text)):
        chunks = recursive_split(cleaned_text)
    if not chunks:
        logger.warning(f"Skipping {file_path.name}: no chunks produced")
        return {"file": file_path.name, "status": "skipped", "reason": "no_chunks"}

    # Step 4: Embed (batched)
    with span("ingest.embed", chunk_count=len(chunks), batch_size=CONFIG["embed_batch_size"]):
        embeddings = embed_chunks_with_retry(chunks)
    if len(embeddings) != len(chunks):
        raise RuntimeError(
            f"Embedding count mismatch: expected {len(chunks)}, got {len(embeddings)}"
        )
    for index, embedding in enumerate(embeddings):
        if len(embedding) != CONFIG["embedding_dim"]:
            raise RuntimeError(
                f"Embedding dimension mismatch for chunk {index}: "
                f"expected {CONFIG['embedding_dim']}, got {len(embedding)}"
            )

    # Step 5: Store
    doc_hash = doc_hash or compute_file_hash(file_path)
    now = datetime.now(timezone.utc)

    meta = parsed.metadata
    with span("ingest.store", chunk_count=len(chunks)):
        with conn.cursor() as cur:
            for idx, (chunk_text, embedding) in enumerate(zip(chunks, embeddings)):
                cur.execute(
                    """
                    INSERT INTO chunks
                        (embedding, content, source_file, file_path, doc_type,
                         chunk_index, total_chunks, doc_hash,
                         title, category, last_updated, owner, classification,
                         data_folder, ingested_at)
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        embedding,
                        chunk_text,
                        meta["source"],
                        meta["file_path"],
                        meta["doc_type"],
                        idx,
                        len(chunks),
                        doc_hash,
                        meta.get("title"),
                        meta.get("category"),
                        meta.get("last_updated"),
                        meta.get("owner"),
                        meta.get("classification"),
                        data_folder,
                        now,
                    ),
                )
        if commit:
            conn.commit()

    logger.info(
        f"Ingested {file_path.name}: {len(chunks)} chunks, "
        f"type={parsed.metadata['doc_type']}"
    )
    return {
        "file": file_path.name,
        "status": "success",
        "chunks": len(chunks),
        "doc_type": parsed.metadata["doc_type"],
    }


def check_document_status(
    file_path: Path, doc_hash: str, conn, data_folder: str
) -> str:
    """Check if a document needs ingestion."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT doc_hash FROM chunks
            WHERE source_file = %s AND data_folder = %s
            LIMIT 1
            """,
            (file_path.name, data_folder),
        )
        row = cur.fetchone()

    if row is None:
        return "new"
    elif row[0] == doc_hash:
        return "unchanged"
    else:
        return "changed"


def delete_document_chunks(source_file: str, conn, data_folder: str):
    """Remove all chunks for a given source file."""
    with conn.cursor() as cur:
        cur.execute(
            "DELETE FROM chunks WHERE source_file = %s AND data_folder = %s",
            (source_file, data_folder),
        )
    conn.commit()


def ingest_file_idempotent(file_path: Path, conn, data_folder: str) -> dict:
    """Ingest a file with idempotency checks."""
    file_path = Path(file_path)
    doc_hash = compute_file_hash(file_path)

    status = check_document_status(file_path, doc_hash, conn, data_folder)

    if status == "unchanged":
        logger.info(f"Skipping {file_path.name}: unchanged (hash match)")
        return {"file": file_path.name, "status": "skipped", "reason": "unchanged"}

    if status == "changed":
        logger.info(f"Re-ingesting {file_path.name}: content changed")
        try:
            result = ingest_file(
                file_path,
                conn,
                data_folder,
                commit=False,
                doc_hash=doc_hash,
            )
            if result["status"] != "success":
                conn.rollback()
                return result
            with conn.cursor() as cur:
                cur.execute(
                    """
                    DELETE FROM chunks
                    WHERE source_file = %s AND data_folder = %s AND doc_hash <> %s
                    """,
                    (file_path.name, data_folder, doc_hash),
                )
            conn.commit()
            return result
        except Exception:
            conn.rollback()
            raise

    return ingest_file(file_path, conn, data_folder)
