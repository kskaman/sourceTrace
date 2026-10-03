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
                data_folder TEXT NOT NULL,
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
        cur.execute("""
            ALTER TABLE chunks
            ADD COLUMN IF NOT EXISTS data_folder TEXT;
        """)
        cur.execute("""
            ALTER TABLE chunks
            ALTER COLUMN data_folder DROP DEFAULT;
        """)
    conn.commit()

    with conn.cursor() as cur:
        cur.execute("""
            SELECT COUNT(*) FROM chunks
            WHERE data_folder IS NULL
               OR btrim(data_folder) = ''
               OR lower(data_folder) = 'default';
        """)
        invalid_folder_count = cur.fetchone()[0]
        if invalid_folder_count:
            raise RuntimeError(
                "Existing chunks need a named data folder. Update data_folder for "
                "rows where it is null, blank, or 'default', then retry."
            )

        cur.execute("""
            ALTER TABLE chunks
            ALTER COLUMN data_folder SET NOT NULL;
        """)
        cur.execute("""
            ALTER TABLE chunks
            DROP CONSTRAINT IF EXISTS chunks_data_folder_valid;
        """)
        cur.execute("""
            ALTER TABLE chunks
            ADD CONSTRAINT chunks_data_folder_valid CHECK (
                btrim(data_folder) <> '' AND lower(data_folder) <> 'default'
            );
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
            CREATE INDEX IF NOT EXISTS chunks_folder_source_idx
            ON chunks (data_folder, source_file);
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS chunks_search_vector_idx
            ON chunks USING GIN (search_vector);
        """)
    conn.commit()


def delete_data_folder(data_folder: str, conn) -> int:
    """Delete all chunks in a data folder and return the number removed."""
    with conn.cursor() as cur:
        cur.execute(
            "DELETE FROM chunks WHERE data_folder = %s",
            (data_folder,),
        )
        deleted_count = cur.rowcount
    conn.commit()
    return deleted_count