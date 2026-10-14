import json
import logging
from pathlib import Path
import sys

from ..config import CONFIG
from ..database import get_connection, initialize_database
from ..observability import log_event, new_trace, span, trace_summary, write_trace

from .pipeline import ingest_file_idempotent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {".pdf", ".md", ".html", ".htm", ".docx", ".txt"}

def ingest_corpus(corpus_dir: str, data_folder: str):
    """Ingest a supported file or all supported documents from a directory."""
    
    corpus_path = Path(corpus_dir)

    print(f"Ingesting from path: {corpus_path}")
    print(f"Data folder: {data_folder}")
    
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
    results = {"success": [], "skipped": [], "failed": []}
    interrupted = False

    try:
        initialize_database(conn)

        for file_path in files:
            new_trace()
            try:
                with span("ingest.file", file=file_path.name, data_folder=data_folder):
                    result = ingest_file_idempotent(file_path, conn, data_folder)
                log_event(
                    "ingest.result",
                    status=result["status"],
                    reason=result.get("reason"),
                    chunks=result.get("chunks", 0),
                )

                if result["status"] == "success":
                    results["success"].append(result)
                else:
                    results["skipped"].append(result)

            except KeyboardInterrupt:
                interrupted = True
                conn.rollback()
                break
            except Exception as e:
                logger.error(f"Failed to process {file_path.name}: {e}")
                conn.rollback()
                results["failed"].append({
                    "file": file_path.name,
                    "status": "failed",
                    "error": str(e),
                })
            finally:
                if CONFIG["print_trace"]:
                    print(json.dumps(trace_summary()))
                if CONFIG["trace_dir"]:
                    write_trace(CONFIG["trace_dir"], label=file_path.stem)
    finally:
        conn.close()

    print(f"\n{'=' * 50}")
    print("Ingestion interrupted:" if interrupted else "Ingestion complete:")
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

    if interrupted:
        raise KeyboardInterrupt