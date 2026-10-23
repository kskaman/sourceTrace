# sourceTrace

sourceTrace is a local Retrieval-Augmented Generation (RAG) CLI. It parses documents, cleans and chunks their text, creates embeddings, stores them in PostgreSQL with pgvector, retrieves relevant context, and generates answers with Ollama.

## Requirements

- Python 3.10 or newer
- Docker Desktop with Docker Compose
- Ollama

## Setup

Create and activate a virtual environment, then install the dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Copy the environment template and update its values. In particular, set `DATABASE_URL` to the password used by your PostgreSQL instance.

```powershell
Copy-Item .env.example .env
```

Start the application database:

```powershell
docker compose up -d pgvector
```

Start Ollama and ensure the configured model is installed:

```powershell
ollama serve
ollama pull llama3.2:3b
```

The defaults use `http://localhost:11434` for Ollama. All application settings in `.env` are validated at startup. `TRACE_DIR` must be defined but may be empty to disable trace files.

## Ingestion

```powershell
python rag_cli.py ingest <path> --folder <name>
```

Supported document types are Markdown, HTML, DOCX, PDF, and plain text. Ingestion performs these stages:

1. Parse document text and metadata.
2. Normalize text and remove common boilerplate.
3. Split text into chunks no larger than `CHUNK_SIZE`.
4. Create one embedding per chunk and validate its configured dimension.
5. Store chunks, embeddings, and metadata in PostgreSQL.

The database schema is created automatically on first ingestion. Reingestion is idempotent: unchanged files are skipped, while changed files are replaced atomically. New chunks are stored and old chunks are removed in one transaction; if replacement fails, the previous indexed document remains available.

Data folders are logical namespaces in PostgreSQL. Source files are not copied or renamed, and the reserved folder name `default` is rejected.

## Usage

```powershell
python rag_cli.py ingest tests/data/corpus --folder policies
python rag_cli.py ingest tests/data/corpus/refund_policy.md --folder finance
python rag_cli.py chat --folder policies
python rag_cli.py chat --folder policies --results 5
python rag_cli.py list-folders
python rag_cli.py rename-folder --folder policies --new-name handbook
python rag_cli.py delete-folder --folder policies
```

Chat requires an existing folder containing indexed data. Missing or empty folders fail with a clear error instead of starting an unusable chat session.

### Agentic RAG

With `USE_AGENT=true` (the default in `.env.example`), `chat` runs a bounded tool-calling loop (`src/retrieve/agent.py`) instead of a single retrieve-then-generate pass. The LLM decides whether to call the `search` tool, with what query, and how many times; each search is hybrid retrieval scoped to the chosen folder followed by reranking. The model needs tool-calling support in Ollama (for example `llama3.2:3b`).

- `AGENT_MAX_STEPS` caps LLM turns; the tool is withheld on the last turn so the model must answer.
- `AGENT_MAX_SEARCH_CALLS` caps searches; excess calls are refused and repeated queries reuse earlier results.
- `--results` is the maximum chunks a single search returns.
- `MIN_RERANK_SCORE` (0-1, default 0.05; 0 disables) drops chunks the reranker scores as irrelevant, so out-of-scope questions get no evidence. If a search finds nothing relevant and the question is compound, it is retried as separate sub-questions.
- If the model answers without searching, the question is searched for it. If no relevant evidence is found, the answer is always `I don't know.` rather than the model's own knowledge.
- If the answer lacks valid chunk citations, the model gets one tool-free turn to add them.
- If the agent loop fails (for example the model has no tool support), the request degrades to the standard pipeline.
- `USE_AGENT=false` always uses the standard single-pass pipeline.

`list-folders` shows each folder with its document and chunk counts. `rename-folder` refuses to merge into an existing folder. `delete-folder` asks for the exact folder name before deleting data; use `--yes` only when confirmation is intentionally unnecessary:

```powershell
python rag_cli.py delete-folder --folder policies --yes
```

## Testing

Tests use a dedicated `sourceTraceTest` PostgreSQL database on host port `5433`. They do not use or clear the application database on port `5432`.

```powershell
docker compose up -d pgvector-test
python -m pytest -q
```

The test URL defaults to:

```text
postgresql://rag-cli:rag-cli@localhost:5433/sourceTraceTest
```

Set `TEST_DATABASE_URL` only when another isolated test database is required. It must not point to the application database because database tests clear their own `chunks` table between cases.

Parser and ingestion tests use four small synthetic fixtures in `tests/data/corpus/`: one Markdown, HTML, DOCX, and PDF document.

## Observability

- `PRINT_TRACE=true` prints per-request stage and latency summaries.
- Set `TRACE_DIR` to a directory to write JSON traces.
- Leave `TRACE_DIR=` empty to disable trace files.
- Every event carries `span_id` and `parent_id`, so nested stages (for example retrieval inside an agent search) can be reconstructed as a tree.
- Agent traces include `agent.llm` (latency per step), `agent.llm.result` (tool-call count, prompt/completion tokens), `agent.tool.search`/`agent.tool.result` (query, returned markers), `agent.tool.refused`/`repeat`/`error`, `agent.citations` (cited markers that were never retrieved, or missing citations), `agent.citations.repair`, `agent.forced_search`, `agent.answer_blocked`, `selection.relevance_filter`, `agent.search.decomposed`, `agent.degraded`, and `agent.final` (steps, searches, stop reason).
- The trace summary aggregates repeated stages (`count`, summed latency), reports `total_latency_ms` from top-level spans only, and totals tokens.

Database credentials are excluded from configuration snapshots and trace output.
