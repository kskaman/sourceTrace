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

## Retrieval

Retrieval uses the parent-document pattern. Hybrid keyword and semantic search ranks the small chunks stored during ingestion. After reranking, each selected child chunk is expanded to include `PARENT_CHUNK_RADIUS` chunks before and after it from the same document and data folder. This setting is independent of `CHUNK_OVERLAP`, which controls ingestion-time text splitting.

Overlapping or adjacent parent windows from the same document are merged into one extended range. Every unique chunk in the merged ranges is sent to Ollama once, in document order, with its exact chunk-level citation.

`CONTEXT_N` and `chat --results` limit the number of precise child hits selected before expansion, not the final number of context chunks. The final context can be larger after expansion or smaller than the theoretical maximum after deduplication. The pipeline does not run another search to fill space created by deduplication; doing so would change the meaning of the selected child-hit limit and can add lower-relevance context.

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

Database credentials are excluded from configuration snapshots and trace output.
