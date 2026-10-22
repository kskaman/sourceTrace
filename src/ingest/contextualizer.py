"""Generate document-aware context prefixes for chunk retrieval."""

from ollama import Client

from ..config import CONFIG


DOCUMENT_SUMMARY_PROMPT = """Summarize this document for retrieval in 2-4 concise sentences.
Identify its purpose, subject, and any scope that helps distinguish isolated chunks.
Use only the document and metadata below. Return only the summary.

Source: {source}
Title: {title}
Document type: {doc_type}

Document:
{document}
"""

CHUNK_CONTEXT_PROMPT = """Write one concise sentence that situates this chunk inside its parent document.
Mention the document topic and the chunk's specific subject, qualifications, or role.
Do not summarize facts that are not present. Return only the context sentence.

Source: {source}
Title: {title}
Document summary: {document_summary}
Chunk position: {chunk_number} of {total_chunks}

Chunk:
{chunk}
"""


def _bounded_document(text: str, max_chars: int) -> str:
    if max_chars <= 0:
        raise ValueError("max_document_chars must be positive")
    if len(text) <= max_chars:
        return text
    head_size = max_chars // 2
    tail_size = max_chars - head_size
    return (
        text[:head_size]
        + "\n\n[...document truncated...]\n\n"
        + text[-tail_size:]
    )


def _chat(client, model: str, prompt: str) -> str:
    response = client.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0},
    )
    return response.message.content.strip()


def generate_context_prefixes(
    document_text: str,
    chunks: list[str],
    metadata: dict,
    *,
    model: str | None = None,
    max_document_chars: int | None = None,
    client=None,
) -> list[str]:
    """Generate one document-aware retrieval prefix for every chunk."""
    if not chunks:
        return []
    if model is None:
        model = CONFIG["contextual_model"]
    if max_document_chars is None:
        max_document_chars = CONFIG["contextual_max_document_chars"]
    if client is None:
        client = Client(host=CONFIG["ollama_host"])

    source = metadata.get("source") or "unknown"
    title = metadata.get("title") or source
    summary_prompt = DOCUMENT_SUMMARY_PROMPT.format(
        source=source,
        title=title,
        doc_type=metadata.get("doc_type") or "unknown",
        document=_bounded_document(document_text, max_document_chars),
    )
    document_summary = _chat(client, model, summary_prompt)
    if not document_summary:
        raise RuntimeError(f"Ollama returned an empty document summary for {source}")

    prefixes = []
    for index, chunk in enumerate(chunks, start=1):
        prompt = CHUNK_CONTEXT_PROMPT.format(
            source=source,
            title=title,
            document_summary=document_summary,
            chunk_number=index,
            total_chunks=len(chunks),
            chunk=chunk,
        )
        prefix = _chat(client, model, prompt)
        if not prefix:
            raise RuntimeError(
                f"Ollama returned an empty context prefix for {source} chunk {index - 1}"
            )
        prefixes.append(prefix)
    return prefixes