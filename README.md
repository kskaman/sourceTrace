# sourceTrace

sourceTrace contains Retrieval-Augmented Generation (RAG) pipelines written in Python. The pipelines use PostgreSQL with pgvector, Sentence Transformers, and Ollama for document ingestion, embeddings, hybrid retrieval, reranking, and answer generation with citations.

The implementation is organized into separate branches. The `main` branch contains the overview, while each branch below contains a runnable version of the pipeline.

## Branches

### [`baseline`](https://github.com/kskaman/sourceTrace/tree/baseline)

The standard RAG pipeline. Documents are parsed, cleaned, split into chunks, embedded, and stored in pgvector. Retrieval combines keyword and semantic search, followed by reranking and answer generation.

### [`parent-document-retrieval`](https://github.com/kskaman/sourceTrace/tree/parent-document-retrieval)

Extends the baseline pipeline with parent-document retrieval. Search ranks small child chunks, then expands selected results with neighboring chunks from the same document. Overlapping ranges are merged and duplicate chunks are removed.

### [`contextual-retrieval`](https://github.com/kskaman/sourceTrace/tree/contextual-retrieval)

Extends the baseline pipeline with contextual retrieval. Ollama generates a document-aware context prefix for each chunk during ingestion. The prefix is used for embeddings, keyword search, and reranking, while the original chunk text is retained for answers and citations.

The parent-document and contextual-retrieval branches are separate variants built from `baseline`; they do not include each other's retrieval pattern.
