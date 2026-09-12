"""Tests for src.rag_cli (argument parsing and dispatch)."""
import argparse

import pytest

from src import rag_cli


def test_valid_source_path_accepts_existing_file(tmp_path):
    file_path = tmp_path / "doc.md"
    file_path.write_text("content", encoding="utf-8")

    result = rag_cli.valid_source_path(str(file_path))

    assert result == file_path.resolve()


def test_valid_source_path_rejects_missing_path(tmp_path):
    missing = tmp_path / "does_not_exist.md"

    with pytest.raises(argparse.ArgumentTypeError):
        rag_cli.valid_source_path(str(missing))


def test_build_parser_parses_ingest_mode(tmp_path):
    file_path = tmp_path / "doc.md"
    file_path.write_text("content", encoding="utf-8")

    args = rag_cli.build_parser().parse_args(["ingest", str(file_path)])

    assert args.mode == "ingest"
    assert args.path == file_path.resolve()


def test_build_parser_parses_chat_mode_with_default_results():
    args = rag_cli.build_parser().parse_args(["chat"])

    assert args.mode == "chat"
    assert args.results == 10


def test_build_parser_parses_chat_mode_with_custom_results():
    args = rag_cli.build_parser().parse_args(["chat", "--results", "5"])

    assert args.results == 5


def test_build_parser_requires_a_mode():
    with pytest.raises(SystemExit):
        rag_cli.build_parser().parse_args([])


def test_main_dispatches_to_ingest_corpus(tmp_path, monkeypatch):
    file_path = tmp_path / "doc.md"
    file_path.write_text("content", encoding="utf-8")

    calls = {}
    monkeypatch.setattr(
        rag_cli, "ingest_corpus", lambda path: calls.setdefault("path", path)
    )
    monkeypatch.setattr("sys.argv", ["rag_cli", "ingest", str(file_path)])

    rag_cli.main()

    assert calls["path"] == str(file_path.resolve())


def test_main_dispatches_to_chat_mode(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["rag_cli", "chat", "--results", "3"])

    rag_cli.main()

    captured = capsys.readouterr()
    assert "3" in captured.out
