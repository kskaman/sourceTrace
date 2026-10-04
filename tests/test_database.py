"""Tests for src.database (table setup)."""
import pytest

from src.database import (
    create_tables,
    initialize_database,
    delete_data_folder,
    list_data_folders,
    rename_data_folder,
)


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


def test_initialize_database_skips_creation_when_schema_exists(
    monkeypatch, db_conn
):
    create_calls = []
    monkeypatch.setattr(
        "src.database.database.create_tables",
        lambda conn: create_calls.append(conn),
    )

    was_created = initialize_database(db_conn)

    assert was_created is False
    assert create_calls == []


def test_delete_data_folder_removes_only_selected_folder(corpus_dir, db_conn):
    from src.ingest.pipeline import ingest_file

    file_path = corpus_dir / "refund_policy.md"
    policies = ingest_file(file_path, db_conn, "policies")
    ingest_file(file_path, db_conn, "archive")

    deleted_count = delete_data_folder("policies", db_conn)

    with db_conn.cursor() as cur:
        cur.execute(
            "SELECT data_folder, COUNT(*) FROM chunks GROUP BY data_folder"
        )
        remaining = dict(cur.fetchall())

    assert deleted_count == policies["chunks"]
    assert "policies" not in remaining
    assert remaining["archive"] > 0


def test_list_data_folders_returns_sorted_counts(corpus_dir, db_conn):
    from src.ingest.pipeline import ingest_file

    file_path = corpus_dir / "refund_policy.md"
    archive = ingest_file(file_path, db_conn, "archive")
    policies = ingest_file(file_path, db_conn, "policies")

    folders = list_data_folders(db_conn)

    assert folders == [
        {
            "name": "archive",
            "document_count": 1,
            "chunk_count": archive["chunks"],
        },
        {
            "name": "policies",
            "document_count": 1,
            "chunk_count": policies["chunks"],
        },
    ]


def test_rename_data_folder_updates_only_selected_folder(corpus_dir, db_conn):
    from src.ingest.pipeline import ingest_file

    file_path = corpus_dir / "refund_policy.md"
    policies = ingest_file(file_path, db_conn, "policies")
    ingest_file(file_path, db_conn, "archive")

    renamed_count = rename_data_folder("policies", "handbook", db_conn)

    assert renamed_count == policies["chunks"]
    assert [folder["name"] for folder in list_data_folders(db_conn)] == [
        "archive",
        "handbook",
    ]


def test_rename_data_folder_rejects_existing_destination(corpus_dir, db_conn):
    from src.ingest.pipeline import ingest_file

    file_path = corpus_dir / "refund_policy.md"
    ingest_file(file_path, db_conn, "policies")
    ingest_file(file_path, db_conn, "archive")

    with pytest.raises(ValueError, match="already exists"):
        rename_data_folder("policies", "archive", db_conn)


def test_rename_data_folder_returns_zero_for_missing_source(db_conn):
    assert rename_data_folder("missing", "new-name", db_conn) == 0
