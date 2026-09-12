"""Tests for src.database (table setup)."""
from src.database import create_tables


def test_create_tables_creates_chunks_table_with_expected_columns(db_conn):
    with db_conn.cursor() as cur:
        cur.execute(
            "SELECT column_name FROM information_schema.columns WHERE table_name = %s",
            ("chunks",),
        )
        columns = {row[0] for row in cur.fetchall()}

    expected = {
        "id", "embedding", "content", "source_file", "file_path", "doc_type",
        "chunk_index", "total_chunks", "doc_hash", "title", "category",
        "last_updated", "owner", "classification", "page_number", "ingested_at",
    }
    assert expected.issubset(columns)


def test_create_tables_is_idempotent(db_conn):
    # Calling create_tables again should not raise or duplicate anything.
    create_tables(db_conn)
    create_tables(db_conn)

    with db_conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM chunks")
        count = cur.fetchone()[0]
    assert count == 0
