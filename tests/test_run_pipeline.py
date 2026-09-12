"""Tests for src.ingest.run_pipeline.ingest_corpus."""
import shutil

import pytest

from src.ingest.run_pipeline import ingest_corpus


def test_ingest_corpus_processes_all_supported_files_in_a_directory(corpus_dir, tmp_path, db_conn):
    shutil.copy(corpus_dir / "refund_policy.md", tmp_path / "refund_policy.md")
    shutil.copy(corpus_dir / "vpn_access_guide.html", tmp_path / "vpn_access_guide.html")
    (tmp_path / "notes.unsupported").write_text("ignored", encoding="utf-8")

    ingest_corpus(str(tmp_path))

    with db_conn.cursor() as cur:
        cur.execute("SELECT DISTINCT source_file FROM chunks")
        sources = {row[0] for row in cur.fetchall()}

    assert sources == {"refund_policy.md", "vpn_access_guide.html"}


def test_ingest_corpus_processes_a_single_file(corpus_dir, tmp_path, db_conn):
    file_path = tmp_path / "refund_policy.md"
    shutil.copy(corpus_dir / "refund_policy.md", file_path)

    ingest_corpus(str(file_path))

    with db_conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM chunks WHERE source_file = %s", ("refund_policy.md",))
        count = cur.fetchone()[0]
    assert count > 0


def test_ingest_corpus_exits_for_unsupported_single_file(tmp_path):
    bad_file = tmp_path / "data.xyz"
    bad_file.write_text("content", encoding="utf-8")

    with pytest.raises(SystemExit):
        ingest_corpus(str(bad_file))
