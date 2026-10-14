"""Shared pytest fixtures for the ingestion test suite."""
import os
import sys
from pathlib import Path

import pytest
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# The app refuses to start without a complete environment. Tuning values are forced
# so tests are deterministic. Database tests always use the isolated test service.
load_dotenv(REPO_ROOT / ".env")
application_database_url = os.environ.get("DATABASE_URL")
test_database_url = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql://rag-cli:rag-cli@localhost:5433/sourceTraceTest",
)
if test_database_url == application_database_url:
    raise RuntimeError("TEST_DATABASE_URL must not point to the application database")
os.environ["DATABASE_URL"] = test_database_url
os.environ.update(
    {
        "EMBEDDING_MODEL": "all-MiniLM-L6-v2",
        "EMBEDDING_DIM": "384",
        "RERANKER_MODEL": "BAAI/bge-reranker-v2-m3",
        "OLLAMA_HOST": "http://localhost:11434",
        "OLLAMA_MODEL": "llama3.2:3b",
        "CANDIDATE_K": "20",
        "CONTEXT_N": "10",
        "USE_RERANKER": "true",
        "USE_QUERY_TRANSFORM": "false",
        "CHUNK_SIZE": "512",
        "CHUNK_OVERLAP": "50",
        "EMBED_BATCH_SIZE": "64",
        "EMBED_MAX_RETRIES": "3",
        "PRINT_TRACE": "false",
        "TRACE_DIR": "",
        "FORCE_RERANKER_FAILURE": "false",
        "FORCE_KEYWORD_FAILURE": "false",
        "FORCE_SEMANTIC_FAILURE": "false",
    }
)

CORPUS_DIR = Path(__file__).resolve().parent / "data" / "corpus"


@pytest.fixture(scope="session")
def corpus_dir() -> Path:
    """Path to the sample documents used by the tests."""
    return CORPUS_DIR


@pytest.fixture()
def db_conn():
    """A connection to the test Postgres database, with the chunks table emptied.

    Skips any test that uses this fixture if Postgres isn't reachable
    (start it with `docker compose up -d pgvector`).
    """
    from src.database import create_tables, get_connection

    try:
        conn = get_connection()
    except Exception as exc:
        pytest.skip(f"Postgres is not reachable (run `docker compose up -d pgvector`): {exc}")

    create_tables(conn)
    with conn.cursor() as cur:
        cur.execute("DELETE FROM chunks")
    conn.commit()

    yield conn

    with conn.cursor() as cur:
        cur.execute("DELETE FROM chunks")
    conn.commit()
    conn.close()
