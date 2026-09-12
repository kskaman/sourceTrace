"""Shared pytest fixtures for the ingestion test suite."""
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

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
