"""Tests for index-time contextual chunk generation."""
from types import SimpleNamespace

import pytest

from src.ingest.contextualizer import generate_context_prefixes


class FakeOllamaClient:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.calls = []

    def chat(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(
            message=SimpleNamespace(content=next(self.responses))
        )


def test_generate_context_prefixes_uses_document_summary_for_each_chunk():
    client = FakeOllamaClient(
        [
            "A company refund policy for customer purchases.",
            "  Eligibility rules in the Refund Policy.  ",
            "Refund timing and payment methods in the Refund Policy.",
        ]
    )

    prefixes = generate_context_prefixes(
        document_text="Customers may request refunds. Refunds arrive in five days.",
        chunks=["Customers may request refunds.", "Refunds arrive in five days."],
        metadata={"source": "refund.md", "title": "Refund Policy"},
        model="llama3.2:3b",
        max_document_chars=12000,
        client=client,
    )

    assert prefixes == [
        "Eligibility rules in the Refund Policy.",
        "Refund timing and payment methods in the Refund Policy.",
    ]
    assert len(client.calls) == 3
    assert all(call["model"] == "llama3.2:3b" for call in client.calls)
    second_prompt = client.calls[1]["messages"][0]["content"]
    assert "A company refund policy" in second_prompt
    assert "Chunk position: 1 of 2" in second_prompt
    assert "Customers may request refunds." in second_prompt


def test_generate_context_prefixes_uses_head_and_tail_for_long_documents():
    client = FakeOllamaClient(["Summary", "Prefix"])

    generate_context_prefixes(
        document_text="A" * 20 + "MIDDLE" + "Z" * 20,
        chunks=["MIDDLE"],
        metadata={"source": "long.md"},
        model="model",
        max_document_chars=20,
        client=client,
    )

    summary_prompt = client.calls[0]["messages"][0]["content"]
    assert "A" * 10 in summary_prompt
    assert "Z" * 10 in summary_prompt
    assert "[...document truncated...]" in summary_prompt


def test_generate_context_prefixes_rejects_empty_model_output():
    client = FakeOllamaClient(["Summary", "   "])

    with pytest.raises(RuntimeError, match="empty context prefix"):
        generate_context_prefixes(
            document_text="Document",
            chunks=["Chunk"],
            metadata={"source": "doc.md"},
            model="model",
            max_document_chars=100,
            client=client,
        )


def test_generate_context_prefixes_skips_model_for_no_chunks():
    client = FakeOllamaClient([])

    assert generate_context_prefixes(
        document_text="Document",
        chunks=[],
        metadata={"source": "doc.md"},
        model="model",
        max_document_chars=100,
        client=client,
    ) == []
    assert client.calls == []