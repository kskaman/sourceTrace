"""Tests for strict environment configuration."""
import pytest

import rag_cli
from src import config
from src.config import ConfigError, build_config, get_or_throw

VALID_ENV = {
    "DATABASE_URL": "postgresql://user:pw@localhost:5432/db",
    "EMBEDDING_MODEL": "all-MiniLM-L6-v2",
    "EMBEDDING_DIM": "384",
    "RERANKER_MODEL": "BAAI/bge-reranker-v2-m3",
    "OLLAMA_HOST": "http://localhost:11434",
    "OLLAMA_MODEL": "llama3.2:3b",
    "CANDIDATE_K": "50",
    "CONTEXT_N": "10",
    "USE_RERANKER": "true",
    "USE_QUERY_TRANSFORM": "no",
    "CHUNK_SIZE": "512",
    "CHUNK_OVERLAP": "50",
    "EMBED_BATCH_SIZE": "64",
    "EMBED_MAX_RETRIES": "0",
    "PRINT_TRACE": "1",
    "TRACE_DIR": "",
    "FORCE_RERANKER_FAILURE": "false",
    "FORCE_KEYWORD_FAILURE": "false",
    "FORCE_SEMANTIC_FAILURE": "off",
}


def test_build_config_parses_every_value():
    cfg = build_config(VALID_ENV)

    assert cfg["candidate_k"] == 50
    assert cfg["embed_max_retries"] == 0
    assert cfg["use_reranker"] is True
    assert cfg["use_query_transform"] is False
    assert cfg["print_trace"] is True
    assert cfg["force_semantic_failure"] is False
    assert cfg["trace_dir"] == ""
    assert cfg["ollama_host"] == "http://localhost:11434"


@pytest.mark.parametrize("name", sorted(VALID_ENV))
def test_every_variable_is_required(name):
    env = {k: v for k, v in VALID_ENV.items() if k != name}

    with pytest.raises(ConfigError, match=name):
        build_config(env)


@pytest.mark.parametrize(
    "name, value",
    [
        ("DATABASE_URL", ""),
        ("DATABASE_URL", "mysql://user@localhost/db"),
        ("DATABASE_URL", "not a url"),
        ("OLLAMA_HOST", "localhost:11434"),
        ("EMBEDDING_DIM", "0"),
        ("CANDIDATE_K", "ten"),
        ("CONTEXT_N", "-1"),
        ("CHUNK_OVERLAP", "-5"),
        ("EMBED_MAX_RETRIES", "1.5"),
        ("USE_RERANKER", "maybe"),
        ("PRINT_TRACE", ""),
        ("OLLAMA_MODEL", "   "),
    ],
)
def test_malformed_values_are_rejected(name, value):
    with pytest.raises(ConfigError, match=name):
        build_config({**VALID_ENV, name: value})


def test_chunk_overlap_must_be_smaller_than_chunk_size():
    with pytest.raises(ConfigError, match="CHUNK_OVERLAP"):
        build_config({**VALID_ENV, "CHUNK_SIZE": "50", "CHUNK_OVERLAP": "50"})


def test_get_or_throw_reports_expected_format():
    with pytest.raises(ConfigError, match="a positive integer"):
        get_or_throw("N", int, "a positive integer", env={"N": "x"})
    assert get_or_throw("N", int, env={"N": " 7 "}) == 7


def test_snapshot_never_includes_the_database_url():
    assert "database_url" not in config.snapshot()
    assert "llm_model" in config.snapshot()


def test_cli_refuses_to_start_on_configuration_error(monkeypatch, capsys):
    def broken():
        raise ConfigError("Missing required environment variable CANDIDATE_K")

    monkeypatch.setattr(rag_cli, "load_config", broken)
    monkeypatch.setattr("sys.argv", ["rag_cli", "list-folders"])

    with pytest.raises(SystemExit) as exit_info:
        rag_cli.main()

    assert exit_info.value.code == 1
    assert "Configuration error: Missing required environment variable CANDIDATE_K" in (
        capsys.readouterr().err
    )
