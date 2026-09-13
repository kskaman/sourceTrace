# database.py - pgvector table setup with metadata
import psycopg2
from pgvector.psycopg2 import register_vector

def get_connection():
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        dbname="rag-cli",
        user="rag-cli",
        password="rag-cli",
    )
    # The vector type must exist before psycopg2 can register it.
    with conn.cursor() as cur:
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    conn.commit()
    register_vector(conn)
    return conn


def create_tables(conn):
    """Create the chunks table with metadata columns."""
    with conn.cursor() as cur:
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS chunks (
                id SERIAL PRIMARY KEY,
                embedding vector(384),
                content TEXT NOT NULL,
                source_file TEXT NOT NULL,
                file_path TEXT NOT NULL,
                doc_type TEXT NOT NULL,
                chunk_index INTEGER NOT NULL,
                total_chunks INTEGER NOT NULL,
                doc_hash TEXT NOT NULL,
                title TEXT,
                category TEXT,
                last_updated TEXT,
                owner TEXT,
                classification TEXT,
                page_number INTEGER,
                ingested_at TIMESTAMP DEFAULT NOW(),
                search_vector TSVECTOR GENERATED ALWAYS AS (
                    to_tsvector('english', content)
                ) STORED
            );
        """)
        cur.execute("""
            ALTER TABLE chunks
            ADD COLUMN IF NOT EXISTS search_vector TSVECTOR
            GENERATED ALWAYS AS (to_tsvector('english', content)) STORED;
        """)
        # Index for vector search
        cur.execute("""
            CREATE INDEX IF NOT EXISTS chunks_embedding_idx
            ON chunks USING hnsw (embedding vector_cosine_ops)
            WITH (m = 16, ef_construction = 64);
        """)
        # Indexes for metadata filtering
        cur.execute("""
            CREATE INDEX IF NOT EXISTS chunks_source_idx ON chunks (source_file);
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS chunks_doc_type_idx ON chunks (doc_type);
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS chunks_doc_hash_idx ON chunks (doc_hash);
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS chunks_category_idx ON chunks (category);
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS chunks_search_vector_idx
            ON chunks USING GIN (search_vector);
        """)
    conn.commit()