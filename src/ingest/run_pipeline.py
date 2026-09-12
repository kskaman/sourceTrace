import logging
from pathlib import Path
import sys

from ..database import get_connection, create_tables

from .pipeline import ingest_file_idempotent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {".pdf", ".md", ".html", ".htm", ".docx", ".txt"}

def ingest_corpus(corpus_dir: str):
    """Ingest a supported file or all supported documents from a directory."""
    
    corpus_path = Path(corpus_dir)

    print(f"Ingesting from path: {corpus_path}")
    
    if corpus_path.is_file():
        if corpus_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            print(f"Error: Unsupported file type: {corpus_path.suffix}")
            sys.exit(1)

        files = [corpus_path]

    elif corpus_path.is_dir():
        files = [
            f for f in sorted(corpus_path.iterdir())
            if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS
        ]

    else:
        print(f"Error: {corpus_dir} is not a valid file or directory")
        sys.exit(1)

    print(f"Found {len(files)} files to process")

    conn = get_connection()
    create_tables(conn)

    results = {"success": [], "skipped": [], "failed": []}

    for file_path in files:
        try:
            result = ingest_file_idempotent(file_path, conn)

            if result["status"] == "success":
                results["success"].append(result)
            else:
                results["skipped"].append(result)

        except Exception as e:
            logger.error(f"Failed to process {file_path.name}: {e}")
            results["failed"].append({
                "file": file_path.name,
                "status": "failed",
                "error": str(e),
            })

    conn.close()

    print(f"\n{'=' * 50}")
    print("Ingestion complete:")
    print(f"  Succeeded:  {len(results['success'])}")
    print(f"  Skipped:    {len(results['skipped'])}")
    print(f"  Failed:     {len(results['failed'])}")

    if results["failed"]:
        print("\nFailed files:")
        for r in results["failed"]:
            print(f"  {r['file']}: {r['error']}")

    total_chunks = sum(
        r.get("chunks", 0)
        for r in results["success"]
    )

    print(f"\nTotal chunks indexed: {total_chunks}")
