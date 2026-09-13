# query_transform.py - LLM-based query rewriting, HyDE, multi-query, decomposition
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
#from openai import OpenAI
from ollama import Client

load_dotenv()
#client = OpenAI()
ollama_client = Client()

#LLM_MODEL = "gpt-4o-mini"
LLM_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

def _chat(prompt: str) -> str:
    # response = client.chat.completions.create(
    #     model=LLM_MODEL,
    #     messages=[{"role": "user", "content": prompt}],
    #     temperature=0,
    # )

    response = ollama_client.chat(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0},
    )

    #return response.choices[0].message.content.strip()
    return response.message.content.strip()

REWRITE_PROMPT = """Rewrite the following user question into a single search query 
    that uses the formal, document-style vocabulary an internal 
    corporate policy document would use. Preserve the user's intent. 
    Return only the rewritten query, no preamble, no explanation, no quotes.

Original: {query}
Rewritten:"""


HYDE_PROMPT = """Write a brief, plausible passage that would directly 
    answer the following question as if it appeared in an 
    internal corporate policy document. Use formal language. 
    Two or three sentences. Do not say "I don't know" or hedge. 
    Return only the passage, no preamble.

Question: {query}
Passage:"""


MULTI_QUERY_PROMPT = """The following search query may be ambiguous. 
    It could plausibly be asking about several distinct things 
    in an internal corporate knowledge base. Generate {n} 
    alternative queries that each cover a different plausible 
    interpretation of what the user might actually be asking. 
    Each variation should be a complete, specific question 
    that uses formal corporate vocabulary. Return them as a numbered 
    list, one per line, with no preamble.

Original: {query}
Variations:"""


DECOMPOSE_PROMPT = """If the following question contains multiple 
    independent sub-questions, decompose it into a numbered list 
    of sub-questions, one per line, with no preamble. If the question 
    is already a single question, return only the original on one line.

Question: {query}
Sub-questions:"""


def rewrite(query: str) -> str:
    return _chat(REWRITE_PROMPT.format(query=query))


def hyde(query: str) -> str:
    return _chat(HYDE_PROMPT.format(query=query))


def multi_query(query: str, n: int = 3) -> list[str]:
    raw = _chat(MULTI_QUERY_PROMPT.format(query=query, n=n))
    lines = [line.strip() for line in raw.splitlines() if line.strip()]
    # Strip leading numbering like "1. " or "1) "
    cleaned = []
    for line in lines:
        for prefix_len in range(1, 4):
            if (
                len(line) > prefix_len + 1
                and line[:prefix_len].isdigit()
                and line[prefix_len] in ".):- "
            ):
                line = line[prefix_len + 1 :].lstrip()
                break
        cleaned.append(line)
    return cleaned[:n]


def decompose(query: str) -> list[str]:
    raw = _chat(DECOMPOSE_PROMPT.format(query=query))
    lines = [line.strip() for line in raw.splitlines() if line.strip()]
    if len(lines) == 1:
        return lines
    cleaned = []
    for line in lines:
        for prefix_len in range(1, 4):
            if (
                len(line) > prefix_len + 1
                and line[:prefix_len].isdigit()
                and line[prefix_len] in ".):- "
            ):
                line = line[prefix_len + 1 :].lstrip()
                break
        cleaned.append(line)
    return cleaned