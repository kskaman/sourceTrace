"""Tests for the end-to-end ingestion pipeline in src.ingest.pipeline."""
from src.ingest.pipeline import (
    check_document_status,
    compute_file_hash,
    delete_document_chunks,
    ingest_file,
    ingest_file_idempotent,
)


def test_compute_file_hash_is_stable_for_same_content(tmp_path):
    file_path = tmp_path / "a.md"
    file_path.write_text("same content", encoding="utf-8")

    assert compute_file_hash(file_path) == compute_file_hash(file_path)


def test_compute_file_hash_differs_for_different_content(tmp_path):
    file_a = tmp_path / "a.md"
    file_b = tmp_path / "b.md"
    file_a.write_text("content one", encoding="utf-8")
    file_b.write_text("content two", encoding="utf-8")

    assert compute_file_hash(file_a) != compute_file_hash(file_b)


def test_ingest_file_stores_chunks_with_metadata(corpus_dir, db_conn):
    file_path = corpus_dir / "refund_policy.md"

    result = ingest_file(file_path, db_conn, "policies")

    assert result["status"] == "success"
    assert result["chunks"] > 0

    with db_conn.cursor() as cur:
        cur.execute(
            "SELECT chunk_index, title, category, owner, classification, embedding "
            "FROM chunks WHERE source_file = %s AND data_folder = %s ORDER BY chunk_index",
            ("refund_policy.md", "policies"),
        )
        rows = cur.fetchall()

    assert len(rows) == result["chunks"]
    assert [r[0] for r in rows] == list(range(len(rows)))
    assert rows[0][1] == "Refund Policy"
    assert rows[0][2] == "Operations"
    assert rows[0][3] == "Finance"
    assert rows[0][4] == "Public"
    assert len(rows[0][5].to_list()) == 384


def test_ingest_file_skips_file_with_no_extractable_text(tmp_path, db_conn):
    empty_file = tmp_path / "empty.md"
    empty_file.write_text("   \n\n  ", encoding="utf-8")

    result = ingest_file(empty_file, db_conn, "empty-files")

    assert result["status"] == "skipped"


def test_check_document_status_reports_new_unchanged_and_changed(corpus_dir, db_conn):
    file_path = corpus_dir / "refund_policy.md"
    doc_hash = compute_file_hash(file_path)

    assert check_document_status(file_path, doc_hash, db_conn, "policies") == "new"

    ingest_file(file_path, db_conn, "policies")
    assert check_document_status(file_path, doc_hash, db_conn, "policies") == "unchanged"

    assert check_document_status(
        file_path, "a-different-hash", db_conn, "policies"
    ) == "changed"
    assert check_document_status(file_path, doc_hash, db_conn, "other") == "new"


def test_delete_document_chunks_removes_all_rows_for_file(corpus_dir, db_conn):
    file_path = corpus_dir / "refund_policy.md"
    ingest_file(file_path, db_conn, "policies")
    ingest_file(file_path, db_conn, "archive")

    delete_document_chunks(file_path.name, db_conn, "policies")

    with db_conn.cursor() as cur:
        cur.execute(
            """
            SELECT data_folder, COUNT(*) FROM chunks
            WHERE source_file = %s GROUP BY data_folder
            """,
            (file_path.name,),
        )
        counts = dict(cur.fetchall())
    assert "policies" not in counts
    assert counts["archive"] > 0


def test_ingest_file_idempotent_skips_unchanged_file(corpus_dir, db_conn):
    file_path = corpus_dir / "refund_policy.md"

    first = ingest_file_idempotent(file_path, db_conn, "policies")
    second = ingest_file_idempotent(file_path, db_conn, "policies")
    other_folder = ingest_file_idempotent(file_path, db_conn, "archive")

    assert first["status"] == "success"
    assert second["status"] == "skipped"
    assert second["reason"] == "unchanged"
    assert other_folder["status"] == "success"

    with db_conn.cursor() as cur:
        cur.execute(
            """
            SELECT data_folder, COUNT(*) FROM chunks
            WHERE source_file = %s GROUP BY data_folder
            """,
            (file_path.name,),
        )
        counts = dict(cur.fetchall())
    assert counts["policies"] == first["chunks"]
    assert counts["archive"] == other_folder["chunks"]


def test_ingest_file_idempotent_reingests_changed_file(tmp_path, db_conn):
    file_path = tmp_path / "policy.md"
    file_path.write_text("Original content that is long enough to keep.", encoding="utf-8")

    first = ingest_file_idempotent(file_path, db_conn, "policies")
    assert first["status"] == "success"

    file_path.write_text("Updated content that is also long enough to keep.", encoding="utf-8")
    second = ingest_file_idempotent(file_path, db_conn, "policies")
    assert second["status"] == "success"

    with db_conn.cursor() as cur:
        cur.execute(
            "SELECT content FROM chunks WHERE source_file = %s", (file_path.name,)
        )
        rows = cur.fetchall()

    assert len(rows) == second["chunks"]
    assert any("Updated content" in r[0] for r in rows)
