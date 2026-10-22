"""Tests for the end-to-end ingestion pipeline in src.ingest.pipeline."""
import threading

import pytest

from src.ingest import pipeline
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


def test_ingest_file_embeds_contextual_text_but_stores_raw_content(
    tmp_path, db_conn, monkeypatch
):
    file_path = tmp_path / "policy.md"
    raw_chunk = "Refunds arrive within five business days."
    file_path.write_text(raw_chunk, encoding="utf-8")
    monkeypatch.setitem(pipeline.CONFIG, "use_contextual_retrieval", True)
    monkeypatch.setattr(
        pipeline,
        "generate_context_prefixes",
        lambda document_text, chunks, metadata: ["Finance refund timing policy."],
    )
    embedded_texts = []

    def fake_embed(texts):
        embedded_texts.extend(texts)
        return [[0.0] * 384 for _ in texts]

    monkeypatch.setattr(pipeline, "embed_chunks_with_retry", fake_embed)

    ingest_file(file_path, db_conn, "policies")

    with db_conn.cursor() as cur:
        cur.execute(
            """
            SELECT content, context_prefix, index_profile
            FROM chunks WHERE source_file = %s
            """,
            (file_path.name,),
        )
        content, context_prefix, index_profile = cur.fetchone()

    assert embedded_texts == [f"Finance refund timing policy.\n\n{raw_chunk}"]
    assert content == raw_chunk
    assert context_prefix == "Finance refund timing policy."
    assert index_profile.startswith("contextual-v1:")


def test_ingest_file_skips_file_with_no_extractable_text(tmp_path, db_conn):
    empty_file = tmp_path / "empty.md"
    empty_file.write_text("   \n\n  ", encoding="utf-8")

    result = ingest_file(empty_file, db_conn, "empty-files")

    assert result["status"] == "skipped"


def test_ingest_file_rejects_missing_embeddings(tmp_path, db_conn, monkeypatch):
    file_path = tmp_path / "policy.md"
    file_path.write_text("Content that is long enough to retain.", encoding="utf-8")
    monkeypatch.setattr(pipeline, "embed_chunks_with_retry", lambda chunks: [])

    with pytest.raises(RuntimeError, match="Embedding count mismatch"):
        ingest_file(file_path, db_conn, "policies")

    db_conn.rollback()
    with db_conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM chunks")
        assert cur.fetchone()[0] == 0


def test_ingest_file_rejects_wrong_embedding_dimension(
    tmp_path, db_conn, monkeypatch
):
    file_path = tmp_path / "policy.md"
    file_path.write_text("Content that is long enough to retain.", encoding="utf-8")
    monkeypatch.setattr(
        pipeline,
        "embed_chunks_with_retry",
        lambda chunks: [[0.0] * 3 for _ in chunks],
    )

    with pytest.raises(RuntimeError, match="Embedding dimension mismatch"):
        ingest_file(file_path, db_conn, "policies")


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


def test_enabling_contextual_retrieval_marks_baseline_index_as_changed(
    corpus_dir, db_conn, monkeypatch
):
    file_path = corpus_dir / "refund_policy.md"
    doc_hash = compute_file_hash(file_path)
    ingest_file(file_path, db_conn, "policies")

    monkeypatch.setitem(pipeline.CONFIG, "use_contextual_retrieval", True)

    assert check_document_status(file_path, doc_hash, db_conn, "policies") == "changed"


def test_profile_change_replaces_baseline_chunks_without_duplicates(
    corpus_dir, db_conn, monkeypatch
):
    file_path = corpus_dir / "refund_policy.md"
    baseline = ingest_file_idempotent(file_path, db_conn, "policies")
    monkeypatch.setitem(pipeline.CONFIG, "use_contextual_retrieval", True)
    monkeypatch.setattr(
        pipeline,
        "generate_context_prefixes",
        lambda document_text, chunks, metadata: [
            f"Context for chunk {index}." for index, _ in enumerate(chunks)
        ],
    )

    contextual = ingest_file_idempotent(file_path, db_conn, "policies")

    with db_conn.cursor() as cur:
        cur.execute(
            """
            SELECT index_profile, COUNT(*)
            FROM chunks
            WHERE source_file = %s AND data_folder = %s
            GROUP BY index_profile
            """,
            (file_path.name, "policies"),
        )
        profile_counts = dict(cur.fetchall())

    assert baseline["chunks"] == contextual["chunks"]
    assert profile_counts == {
        pipeline.current_index_profile(): contextual["chunks"]
    }


def test_contextualizer_failure_during_profile_change_preserves_baseline(
    corpus_dir, db_conn, monkeypatch
):
    file_path = corpus_dir / "refund_policy.md"
    baseline = ingest_file_idempotent(file_path, db_conn, "policies")
    monkeypatch.setitem(pipeline.CONFIG, "use_contextual_retrieval", True)
    monkeypatch.setattr(
        pipeline,
        "generate_context_prefixes",
        lambda *args: (_ for _ in ()).throw(RuntimeError("contextualizer failed")),
    )

    with pytest.raises(RuntimeError, match="contextualizer failed"):
        ingest_file_idempotent(file_path, db_conn, "policies")

    with db_conn.cursor() as cur:
        cur.execute(
            """
            SELECT index_profile, COUNT(*)
            FROM chunks
            WHERE source_file = %s AND data_folder = %s
            GROUP BY index_profile
            """,
            (file_path.name, "policies"),
        )
        profile_counts = dict(cur.fetchall())

    assert profile_counts == {"baseline": baseline["chunks"]}


def test_check_document_status_detects_mixed_index_versions(
    corpus_dir, db_conn
):
    file_path = corpus_dir / "refund_policy.md"
    ingest_file(file_path, db_conn, "policies")
    with db_conn.cursor() as cur:
        cur.execute(
            """
            UPDATE chunks SET index_profile = 'unexpected-profile'
            WHERE id = (
                SELECT id FROM chunks
                WHERE source_file = %s AND data_folder = %s
                LIMIT 1
            )
            """,
            (file_path.name, "policies"),
        )
    db_conn.commit()

    assert check_document_status(
        file_path,
        compute_file_hash(file_path),
        db_conn,
        "policies",
    ) == "changed"


def test_concurrent_ingestion_serializes_same_document(
    corpus_dir, db_conn, monkeypatch
):
    from src.database import get_connection

    file_path = corpus_dir / "refund_policy.md"
    first_conn = get_connection()
    second_conn = get_connection()
    first_holds_lock = threading.Event()
    release_first = threading.Event()
    second_started = threading.Event()
    original_status = pipeline.check_document_status
    original_hash = pipeline.compute_file_hash
    results = []
    errors = []

    def controlled_status(path, doc_hash, conn, data_folder):
        if conn is first_conn:
            first_holds_lock.set()
            assert release_first.wait(timeout=10)
        return original_status(path, doc_hash, conn, data_folder)

    def controlled_hash(path):
        if threading.current_thread().name == "second-ingest":
            second_started.set()
        return original_hash(path)

    def ingest(conn):
        try:
            results.append(ingest_file_idempotent(file_path, conn, "policies"))
        except Exception as exc:
            errors.append(exc)

    monkeypatch.setattr(pipeline, "check_document_status", controlled_status)
    monkeypatch.setattr(pipeline, "compute_file_hash", controlled_hash)
    first = threading.Thread(target=ingest, args=(first_conn,), name="first-ingest")
    second = threading.Thread(target=ingest, args=(second_conn,), name="second-ingest")

    try:
        first.start()
        assert first_holds_lock.wait(timeout=10)
        second.start()
        assert second_started.wait(timeout=10)
        release_first.set()
        first.join(timeout=30)
        second.join(timeout=30)

        assert not first.is_alive() and not second.is_alive()
        assert errors == []
        assert sorted(result["status"] for result in results) == ["skipped", "success"]
        with db_conn.cursor() as cur:
            cur.execute(
                """
                SELECT COUNT(*) FROM chunks
                WHERE source_file = %s AND data_folder = %s
                """,
                (file_path.name, "policies"),
            )
            stored_count = cur.fetchone()[0]
        success = next(result for result in results if result["status"] == "success")
        assert stored_count == success["chunks"]
    finally:
        release_first.set()
        first.join(timeout=5)
        second.join(timeout=5)
        first_conn.close()
        second_conn.close()


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


def test_failed_reingestion_preserves_previous_chunks(tmp_path, db_conn, monkeypatch):
    file_path = tmp_path / "policy.md"
    original = "Original content that is long enough to keep."
    file_path.write_text(original, encoding="utf-8")
    ingest_file_idempotent(file_path, db_conn, "policies")

    file_path.write_text("Updated content that fails embedding.", encoding="utf-8")
    monkeypatch.setattr(
        pipeline,
        "embed_chunks_with_retry",
        lambda chunks: (_ for _ in ()).throw(RuntimeError("embedding failed")),
    )

    with pytest.raises(RuntimeError, match="embedding failed"):
        ingest_file_idempotent(file_path, db_conn, "policies")

    with db_conn.cursor() as cur:
        cur.execute(
            "SELECT content FROM chunks WHERE source_file = %s AND data_folder = %s",
            (file_path.name, "policies"),
        )
        rows = cur.fetchall()

    assert rows
    assert all(original in row[0] for row in rows)
