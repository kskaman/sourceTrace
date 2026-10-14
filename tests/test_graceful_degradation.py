"""Tests for graceful degradation and clean shutdown."""
import sys
import types

import pytest

import rag_cli
from src import observability
from src.ingest import run_pipeline
from src.retrieve import hybrid, pipeline


def _chunk(chunk_id, kw=None, sem=None):
    return {
        "chunk_id": chunk_id,
        "content": f"text {chunk_id}",
        "source_file": "doc.md",
        "chunk_index": chunk_id,
        "keyword_rank": kw,
        "semantic_rank": sem,
    }


def _fake_reranker(monkeypatch, rerank):
    module = types.ModuleType("src.retrieve.reranker")
    module.rerank = rerank
    monkeypatch.setitem(sys.modules, "src.retrieve.reranker", module)


def _stages():
    return {event["stage"] for event in observability.trace_events()}


def test_select_context_uses_reranker_when_it_works(monkeypatch):
    _fake_reranker(monkeypatch, lambda query, candidates, top_n: [candidates[-1]])
    candidates = [_chunk(1, kw=1), _chunk(2, sem=1)]

    assert pipeline.select_context(candidates, n=1, query="q") == [candidates[-1]]


def test_select_context_falls_back_when_reranker_fails(monkeypatch):
    def broken(query, candidates, top_n):
        raise RuntimeError("model unavailable")

    _fake_reranker(monkeypatch, broken)
    observability.new_trace()
    candidates = [_chunk(1, kw=1), _chunk(2, sem=1)]

    selected = pipeline.select_context(candidates, n=2, query="q")

    assert [c["chunk_id"] for c in selected] == [1, 2]
    assert "selection.rerank.degraded" in _stages()


def test_forced_reranker_failure_skips_the_reranker(monkeypatch):
    _fake_reranker(
        monkeypatch,
        lambda *a, **k: pytest.fail("reranker must not run when failure is forced"),
    )
    monkeypatch.setitem(pipeline.CONFIG, "force_reranker_failure", True)
    observability.new_trace()

    selected = pipeline.select_context([_chunk(1, kw=1)], n=1, query="q")

    assert [c["chunk_id"] for c in selected] == [1]
    assert "selection.rerank.degraded" in _stages()


def test_hybrid_continues_with_semantic_results_when_keyword_search_fails(monkeypatch):
    def broken(*args, **kwargs):
        raise RuntimeError("keyword down")

    monkeypatch.setattr(hybrid, "keyword_search", broken)
    monkeypatch.setattr(
        hybrid, "semantic_search", lambda q, k, filters: [_chunk(1, sem=1)]
    )
    observability.new_trace()

    candidates = hybrid.hybrid_candidates("q")

    assert [c["chunk_id"] for c in candidates] == [1]
    assert "retrieval.keyword.degraded" in _stages()


def test_hybrid_continues_with_keyword_results_when_semantic_search_is_forced_to_fail(
    monkeypatch,
):
    monkeypatch.setitem(hybrid.CONFIG, "force_semantic_failure", True)
    monkeypatch.setattr(
        hybrid, "keyword_search", lambda q, k, filters: [_chunk(1, kw=1)]
    )
    monkeypatch.setattr(
        hybrid,
        "semantic_search",
        lambda *a, **k: pytest.fail("semantic search must not run when forced to fail"),
    )
    observability.new_trace()

    assert [c["chunk_id"] for c in hybrid.hybrid_candidates("q")] == [1]
    assert "retrieval.semantic.degraded" in _stages()


def test_hybrid_raises_when_both_searches_fail(monkeypatch):
    def broken(*args, **kwargs):
        raise RuntimeError("down")

    monkeypatch.setattr(hybrid, "keyword_search", broken)
    monkeypatch.setattr(hybrid, "semantic_search", broken)

    with pytest.raises(hybrid.RetrievalUnavailableError):
        hybrid.hybrid_candidates("q")


def test_query_rewrite_failure_falls_back_to_the_original_question(monkeypatch):
    module = types.ModuleType("src.retrieve.query_transform")

    def broken(query):
        raise RuntimeError("ollama down")

    module.rewrite = broken
    monkeypatch.setitem(sys.modules, "src.retrieve.query_transform", module)
    monkeypatch.setitem(pipeline.CONFIG, "use_query_transform", True)
    observability.new_trace()

    assert pipeline._retrieval_query("original?") == "original?"
    assert "query_transform.degraded" in _stages()


def test_chat_loop_survives_a_failing_question(monkeypatch, capsys):
    inputs = iter(["first", "second", "exit"])
    monkeypatch.setattr(rag_cli, "require_data_folder", lambda _: None)
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    answers = []

    def flaky_answer(**kwargs):
        answers.append(kwargs["question"])
        if kwargs["question"] == "first":
            raise RuntimeError("llm down")
        return {"answer": "fine", "context": [], "candidate_count": 0}

    rag_cli.chat_loop("policies", answer_fn=flaky_answer)

    captured = capsys.readouterr()
    assert answers == ["first", "second"]
    assert "Error answering question: llm down" in captured.err
    assert "Assistant: fine" in captured.out


@pytest.mark.parametrize("exc", [EOFError, KeyboardInterrupt])
def test_chat_loop_exits_cleanly_on_eof_or_ctrl_c(monkeypatch, capsys, exc):
    def interrupted(_):
        raise exc

    monkeypatch.setattr(rag_cli, "require_data_folder", lambda _: None)
    monkeypatch.setattr("builtins.input", interrupted)

    rag_cli.chat_loop("policies")

    assert "Goodbye." in capsys.readouterr().out


def test_main_exits_130_on_keyboard_interrupt(monkeypatch, capsys):
    def interrupted(*args, **kwargs):
        raise KeyboardInterrupt

    monkeypatch.setattr(rag_cli, "list_folders", interrupted)
    monkeypatch.setattr("sys.argv", ["rag_cli", "list-folders"])

    with pytest.raises(SystemExit) as exit_info:
        rag_cli.main()

    assert exit_info.value.code == 130
    assert "Interrupted." in capsys.readouterr().err


class FakeConnection:
    def __init__(self):
        self.closed = False
        self.rollbacks = 0

    def rollback(self):
        self.rollbacks += 1

    def close(self):
        self.closed = True


def _patch_ingest(monkeypatch, conn, ingest):
    monkeypatch.setattr(run_pipeline, "get_connection", lambda: conn)
    monkeypatch.setattr(run_pipeline, "initialize_database", lambda c: False)
    monkeypatch.setattr(run_pipeline, "ingest_file_idempotent", ingest)


def test_ingest_stops_on_ctrl_c_prints_summary_and_closes_connection(
    monkeypatch, tmp_path, capsys
):
    for name in ("a.md", "b.md", "c.md"):
        (tmp_path / name).write_text("text", encoding="utf-8")
    conn = FakeConnection()
    processed = []

    def ingest(file_path, conn_, data_folder):
        processed.append(file_path.name)
        if file_path.name == "b.md":
            raise KeyboardInterrupt
        return {"file": file_path.name, "status": "success", "chunks": 2}

    _patch_ingest(monkeypatch, conn, ingest)

    with pytest.raises(KeyboardInterrupt):
        run_pipeline.ingest_corpus(str(tmp_path), "docs")

    assert processed == ["a.md", "b.md"]
    assert conn.closed
    out = capsys.readouterr().out
    assert "Ingestion interrupted:" in out
    assert "Succeeded:  1" in out


def test_ingest_rolls_back_a_failed_file_and_keeps_going(monkeypatch, tmp_path, capsys):
    for name in ("a.md", "b.md"):
        (tmp_path / name).write_text("text", encoding="utf-8")
    conn = FakeConnection()

    def ingest(file_path, conn_, data_folder):
        if file_path.name == "a.md":
            raise RuntimeError("bad file")
        return {"file": file_path.name, "status": "success", "chunks": 1}

    _patch_ingest(monkeypatch, conn, ingest)

    run_pipeline.ingest_corpus(str(tmp_path), "docs")

    assert conn.rollbacks == 1
    assert conn.closed
    out = capsys.readouterr().out
    assert "Failed:     1" in out
    assert "Succeeded:  1" in out


def test_ingest_closes_connection_when_database_setup_fails(monkeypatch, tmp_path):
    (tmp_path / "a.md").write_text("text", encoding="utf-8")
    conn = FakeConnection()
    _patch_ingest(monkeypatch, conn, lambda *a: None)

    def broken(_):
        raise RuntimeError("schema error")

    monkeypatch.setattr(run_pipeline, "initialize_database", broken)

    with pytest.raises(RuntimeError, match="schema error"):
        run_pipeline.ingest_corpus(str(tmp_path), "docs")

    assert conn.closed
