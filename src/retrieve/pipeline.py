# rag.py - End-to-end RAG with optional reranking
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
# from openai import OpenAI
from ollama import Client

from .hybrid import hybrid_candidates

load_dotenv()
# client = OpenAI()
ollama_client = Client()

LLM_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
NO_INDEXED_REFERENCES_MESSAGE = (
    "No indexed references found. Ingest documents before asking questions."
)

PROMPT_TEMPLATE = """You are an internal assistant. Answer the question using only the context below.

Rules:
- Use only the information in the numbered context blocks. Do not rely on outside knowledge.
- Cite each fact with the exact source marker shown in brackets, including the chunk identifier, e.g. [hipaa_compliance_overview.md#chunk-6].
- Only cite markers that appear in the context below. Do not cite a document at file level; the chunk identifier is required.
- If the context does not contain enough information to answer the question, reply exactly: "I don't know."

Context:
{context}

Question: {question}

Answer:"""


def _interleave(candidates: list[dict], n: int) -> list[dict]:
    kw = sorted(
        [c for c in candidates if c["keyword_rank"] is not None],
        key=lambda c: c["keyword_rank"],
    )
    sem = sorted(
        [c for c in candidates if c["semantic_rank"] is not None],
        key=lambda c: c["semantic_rank"],
    )
    selected: list[dict] = []
    seen: set[int] = set()
    for kw_c, sem_c in zip(kw, sem):
        for c in (kw_c, sem_c):
            if c["chunk_id"] not in seen:
                selected.append(c)
                seen.add(c["chunk_id"])
            if len(selected) >= n:
                return selected
    for c in kw + sem:
        if c["chunk_id"] not in seen:
            selected.append(c)
            seen.add(c["chunk_id"])
        if len(selected) >= n:
            break
    return selected


def select_context(
    candidates: list[dict], n: int = 5, use_reranker: bool = True, query: str = ""
) -> list[dict]:
    """Pick top-N chunks. With use_reranker=True, score query-chunk pairs with a cross-encoder."""
    if use_reranker:
        from .reranker import rerank

        return rerank(query, candidates, top_n=n)
    return _interleave(candidates, n)


def build_prompt(question: str, chunks: list[dict]) -> str:
    blocks = [
        f"{i}. [{c['source_file']}#chunk-{c['chunk_index']}] {c['content']}"
        for i, c in enumerate(chunks, start=1)
    ]
    return PROMPT_TEMPLATE.format(context="\n\n".join(blocks), question=question)


def answer(
    question: str, k: int = 20, n: int = 5, use_reranker: bool = True
) -> dict:
    candidates = hybrid_candidates(question, k=k)
    if not candidates:
        return {
            "answer": NO_INDEXED_REFERENCES_MESSAGE,
            "context": [],
            "candidate_count": 0,
        }

    chunks = select_context(candidates, n=n, use_reranker=use_reranker, query=question)
    prompt = build_prompt(question, chunks)
    # response = client.chat.completions.create(
    #     model=JUDGE_MODEL,
    #     messages=[{"role": "user", "content": prompt}],
    #     temperature=0,
    # )
    response = ollama_client.chat(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0},
    )

    return {
        #"answer": response.choices[0].message.content.strip(),
        "answer": response.message.content.strip(),
        "context": chunks,
        "candidate_count": len(candidates),
    }