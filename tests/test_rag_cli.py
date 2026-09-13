"""Tests for the root-level rag_cli CLI (argument parsing and dispatch)."""
import argparse

import pytest

import rag_cli


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


def test_build_parser_shows_help_and_reason_on_missing_mode(capsys):
    with pytest.raises(SystemExit) as exc_info:
        rag_cli.build_parser().parse_args([])

    assert exc_info.value.code == 2
    captured = capsys.readouterr()
    assert "usage:" in captured.err
    assert "Why this failed:" in captured.err


def test_build_parser_shows_help_and_reason_on_missing_path(capsys):
    with pytest.raises(SystemExit) as exc_info:
        rag_cli.build_parser().parse_args(["ingest"])

    assert exc_info.value.code == 2
    captured = capsys.readouterr()
    assert "usage:" in captured.err
    assert "Why this failed:" in captured.err


def test_main_dispatches_to_ingest_corpus(tmp_path, monkeypatch):
    file_path = tmp_path / "doc.md"
    file_path.write_text("content", encoding="utf-8")

    calls = {}
    monkeypatch.setattr(
        "src.ingest.ingest_corpus", lambda path: calls.setdefault("path", path)
    )
    monkeypatch.setattr("sys.argv", ["rag_cli", "ingest", str(file_path)])

    rag_cli.main()

    assert calls["path"] == str(file_path.resolve())


def test_main_dispatches_to_chat_mode(monkeypatch, capsys):
    calls = {}
    monkeypatch.setattr(
        rag_cli, "chat_loop", lambda max_results: calls.setdefault("max_results", max_results)
    )
    monkeypatch.setattr("sys.argv", ["rag_cli", "chat", "--results", "3"])

    rag_cli.main()

    assert calls["max_results"] == 3


def test_chat_loop_exits_without_loading_retrieval(monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda _: "exit")

    rag_cli.chat_loop()

    assert "Entering chat mode" in capsys.readouterr().out


def test_chat_loop_prints_empty_index_message_and_uses_result_limit(
    monkeypatch, capsys
):
    inputs = iter(["Where is the policy?", "exit"])
    calls = []

    def fake_answer(**kwargs):
        calls.append(kwargs)
        return {
            "answer": "No indexed references found.",
            "context": [],
            "candidate_count": 0,
        }

    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    rag_cli.chat_loop(max_results=3, answer_fn=fake_answer)

    assert len(calls) == 1
    assert calls[0]["question"] == "Where is the policy?"
    assert calls[0]["n"] == 3
    assert calls[0]["k"] >= calls[0]["n"]
    assert calls[0]["use_reranker"] is True
    captured = capsys.readouterr()
    assert "Assistant: No indexed references found." in captured.out
    assert "Context: []" in captured.out
