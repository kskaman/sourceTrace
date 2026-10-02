"""Tests for src.database (table setup)."""
import pytest

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
        "search_vector", "data_folder",
    }
    assert expected.issubset(columns)


def test_data_folder_has_no_default_and_is_required(db_conn):
    with db_conn.cursor() as cur:
        cur.execute(
            """
            SELECT column_default, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'chunks' AND column_name = 'data_folder'
            """
        )
        column_default, is_nullable = cur.fetchone()

    assert column_default is None
    assert is_nullable == "NO"


@pytest.mark.parametrize("data_folder", [None, "", "   ", "default", "DEFAULT"])
def test_data_folder_rejects_invalid_names(db_conn, data_folder):
    with pytest.raises(Exception):
        with db_conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO chunks (
                    embedding, content, source_file, file_path, doc_type,
                    chunk_index, total_chunks, doc_hash, data_folder
                ) VALUES (
                    array_fill(0, ARRAY[384])::vector, 'content', 'source.md',
                    'source.md', 'md', 0, 1, 'hash', %s
                )
                """,
                (data_folder,),
            )
    db_conn.rollback()


def test_create_tables_is_idempotent(db_conn):
    # Calling create_tables again should not raise or duplicate anything.
    create_tables(db_conn)
    create_tables(db_conn)

    with db_conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM chunks")
        count = cur.fetchone()[0]
    assert count == 0
