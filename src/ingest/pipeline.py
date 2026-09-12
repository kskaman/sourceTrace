# pipeline.py - End-to-end ingestion pipeline
import hashlib
import logging
import sys
from pathlib import Path
from datetime import datetime, timezone

from .document_parser import parse_document
from .text_cleaner import clean_text
from .embedder import embed_chunks_with_retry
from ..database import get_connection, create_tables


logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def recursive_split(text, chunk_size=512, overlap=50):
    """Simple recursive character splitter (from chapter 3)."""
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
            return chunks

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


def ingest_file(file_path: Path, conn) -> dict:
    """Process a single file through the full pipeline."""
    file_path = Path(file_path)
    logger.info(f"Processing: {file_path.name}")

    # Step 1: Parse
    parsed = parse_document(file_path)
    if not parsed.text.strip():
        logger.warning(f"Skipping {file_path.name}: no text extracted")
        return {"file": file_path.name, "status": "skipped", "reason": "empty"}

    # Step 2: Clean
    cleaned_text = clean_text(parsed.text)
    if not cleaned_text:
        logger.warning(f"Skipping {file_path.name}: empty after cleaning")
        return {"file": file_path.name, "status": "skipped", "reason": "empty_after_clean"}

    # Step 3: Chunk
    chunks = recursive_split(cleaned_text, chunk_size=512, overlap=50)
    if not chunks:
        logger.warning(f"Skipping {file_path.name}: no chunks produced")
        return {"file": file_path.name, "status": "skipped", "reason": "no_chunks"}

    # Step 4: Embed (batched)
    embeddings = embed_chunks_with_retry(chunks, batch_size=64)

    # Step 5: Store
    doc_hash = compute_file_hash(file_path)
    now = datetime.now(timezone.utc)

    meta = parsed.metadata
    with conn.cursor() as cur:
        for idx, (chunk_text, embedding) in enumerate(zip(chunks, embeddings)):
            cur.execute(
                """
                INSERT INTO chunks
                    (embedding, content, source_file, file_path, doc_type,
                     chunk_index, total_chunks, doc_hash,
                     title, category, last_updated, owner, classification,
                     ingested_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
                    now,
                ),
            )
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


def check_document_status(file_path: Path, doc_hash: str, conn) -> str:
    """Check if a document needs ingestion."""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT doc_hash FROM chunks WHERE source_file = %s LIMIT 1",
            (file_path.name,),
        )
        row = cur.fetchone()

    if row is None:
        return "new"
    elif row[0] == doc_hash:
        return "unchanged"
    else:
        return "changed"


def delete_document_chunks(source_file: str, conn):
    """Remove all chunks for a given source file."""
    with conn.cursor() as cur:
        cur.execute(
            "DELETE FROM chunks WHERE source_file = %s",
            (source_file,),
        )
    conn.commit()


def ingest_file_idempotent(file_path: Path, conn) -> dict:
    """Ingest a file with idempotency checks."""
    file_path = Path(file_path)
    doc_hash = compute_file_hash(file_path)

    status = check_document_status(file_path, doc_hash, conn)

    if status == "unchanged":
        logger.info(f"Skipping {file_path.name}: unchanged (hash match)")
        return {"file": file_path.name, "status": "skipped", "reason": "unchanged"}

    if status == "changed":
        logger.info(f"Re-ingesting {file_path.name}: content changed")
        delete_document_chunks(file_path.name, conn)

    return ingest_file(file_path, conn)
