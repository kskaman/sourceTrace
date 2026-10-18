# config.py - Strict, environment-driven configuration.
#
# Every setting must be defined in the environment (or a .env file) and be in the
# required format. Importing this module validates all of them, so the application
# refuses to start with a clear message when one is missing or malformed.
import os
from typing import Callable, Mapping
from urllib.parse import urlparse

from dotenv import load_dotenv

load_dotenv()


class ConfigError(RuntimeError):
    """A required environment variable is missing or malformed."""


_TRUE = {"1", "true", "yes", "on"}
_FALSE = {"0", "false", "no", "off"}


def _text(raw: str) -> str:
    return raw


def _positive_int(raw: str) -> int:
    value = int(raw)
    if value <= 0:
        raise ValueError(raw)
    return value


def _non_negative_int(raw: str) -> int:
    value = int(raw)
    if value < 0:
        raise ValueError(raw)
    return value


def _bool(raw: str) -> bool:
    lowered = raw.lower()
    if lowered in _TRUE:
        return True
    if lowered in _FALSE:
        return False
    raise ValueError(raw)


def _url_with_schemes(*schemes: str) -> Callable[[str], str]:
    def parse(raw: str) -> str:
        parsed = urlparse(raw)
        if parsed.scheme not in schemes or not parsed.netloc:
            raise ValueError(raw)
        return raw

    return parse


_postgres_url = _url_with_schemes("postgresql", "postgres")
_http_url = _url_with_schemes("http", "https")

_EXPECT_TEXT = "a non-empty string"
_EXPECT_POSITIVE_INT = "a positive integer"
_EXPECT_NON_NEGATIVE_INT = "a non-negative integer"
_EXPECT_BOOL = "one of true/false, yes/no, on/off, 1/0"


def get_or_throw(
    name: str,
    parser: Callable[[str], object] = _text,
    expected: str = _EXPECT_TEXT,
    allow_empty: bool = False,
    env: Mapping[str, str] | None = None,
):
    """Return the parsed value of an environment variable or raise ConfigError.

    The variable must be defined. It must also be non-empty unless allow_empty is
    set, and `parser` must accept it (parsers signal bad input with ValueError).
    """
    source = os.environ if env is None else env
    raw = source.get(name)
    if raw is None:
        raise ConfigError(f"Missing required environment variable {name} (expected {expected})")
    raw = raw.strip()
    if not raw:
        if allow_empty:
            return ""
        raise ConfigError(f"Environment variable {name} is empty (expected {expected})")
    try:
        return parser(raw)
    except ValueError:
        raise ConfigError(f"Invalid value for {name}: {raw!r} (expected {expected})") from None


def build_config(env: Mapping[str, str] | None = None) -> dict:
    """Read and validate every setting from `env` (the process environment by default)."""

    def get(name, parser=_text, expected=_EXPECT_TEXT, allow_empty=False):
        return get_or_throw(name, parser, expected, allow_empty, env)

    config = {
        "database_url": get(
            "DATABASE_URL", _postgres_url, "a URL like postgresql://user:password@host:5432/dbname"
        ),
        "embedding_model": get("EMBEDDING_MODEL"),
        "embedding_dim": get("EMBEDDING_DIM", _positive_int, _EXPECT_POSITIVE_INT),
        "reranker_model": get("RERANKER_MODEL"),
        "ollama_host": get("OLLAMA_HOST", _http_url, "an http(s) URL like http://localhost:11434"),
        "llm_model": get("OLLAMA_MODEL"),
        "candidate_k": get("CANDIDATE_K", _positive_int, _EXPECT_POSITIVE_INT),
        "context_n": get("CONTEXT_N", _positive_int, _EXPECT_POSITIVE_INT),
        "parent_chunk_radius": get(
            "PARENT_CHUNK_RADIUS", _non_negative_int, _EXPECT_NON_NEGATIVE_INT
        ),
        "chunk_size": get("CHUNK_SIZE", _positive_int, _EXPECT_POSITIVE_INT),
        "chunk_overlap": get("CHUNK_OVERLAP", _non_negative_int, _EXPECT_NON_NEGATIVE_INT),
        "embed_batch_size": get("EMBED_BATCH_SIZE", _positive_int, _EXPECT_POSITIVE_INT),
        "embed_max_retries": get("EMBED_MAX_RETRIES", _non_negative_int, _EXPECT_NON_NEGATIVE_INT),
        "use_reranker": get("USE_RERANKER", _bool, _EXPECT_BOOL),
        "use_query_transform": get("USE_QUERY_TRANSFORM", _bool, _EXPECT_BOOL),
        "print_trace": get("PRINT_TRACE", _bool, _EXPECT_BOOL),
        "trace_dir": get("TRACE_DIR", expected="a directory path (may be empty)", allow_empty=True),
        "force_reranker_failure": get("FORCE_RERANKER_FAILURE", _bool, _EXPECT_BOOL),
        "force_keyword_failure": get("FORCE_KEYWORD_FAILURE", _bool, _EXPECT_BOOL),
        "force_semantic_failure": get("FORCE_SEMANTIC_FAILURE", _bool, _EXPECT_BOOL),
    }

    if config["chunk_overlap"] >= config["chunk_size"]:
        raise ConfigError(
            f"CHUNK_OVERLAP ({config['chunk_overlap']}) must be smaller than "
            f"CHUNK_SIZE ({config['chunk_size']})"
        )
    return config


CONFIG: dict = build_config()


def snapshot() -> dict:
    """Return the effective settings without secrets. Intended for run-start logging."""
    return {key: value for key, value in CONFIG.items() if key != "database_url"}
