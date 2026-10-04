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
    with conn.cursor() as cur:
        cur.execute(
            "SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'vector')"
        )
        vector_is_available = cur.fetchone()[0]
    if vector_is_available:
        register_vector(conn)
    return conn


def create_tables(conn):
    """Create the clean database schema for a new index."""
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
                data_folder TEXT NOT NULL CONSTRAINT chunks_data_folder_valid
                    CHECK (btrim(data_folder) <> '' AND lower(data_folder) <> 'default'),
                page_number INTEGER,
                ingested_at TIMESTAMP DEFAULT NOW(),
                search_vector TSVECTOR GENERATED ALWAYS AS (
                    to_tsvector('english', content)
                ) STORED
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
    register_vector(conn)


def database_is_initialized(conn) -> bool:
    """Return whether the chunks table already exists."""
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass('public.chunks') IS NOT NULL")
        return cur.fetchone()[0]


def initialize_database(conn) -> bool:
    """Create the schema on first ingestion and report whether it was created."""
    if database_is_initialized(conn):
        return False
    create_tables(conn)
    return True


def delete_data_folder(data_folder: str, conn) -> int:
    """Delete all chunks in a data folder and return the number removed."""
    if not database_is_initialized(conn):
        return 0
    with conn.cursor() as cur:
        cur.execute(
            "DELETE FROM chunks WHERE data_folder = %s",
            (data_folder,),
        )
        deleted_count = cur.rowcount
    conn.commit()
    return deleted_count


def list_data_folders(conn) -> list[dict]:
    """Return named data folders with their document and chunk counts."""
    if not database_is_initialized(conn):
        return []
    with conn.cursor() as cur:
        cur.execute("""
            SELECT data_folder,
                   COUNT(DISTINCT source_file) AS document_count,
                   COUNT(*) AS chunk_count
            FROM chunks
            GROUP BY data_folder
            ORDER BY data_folder;
        """)
        rows = cur.fetchall()

    return [
        {
            "name": row[0],
            "document_count": row[1],
            "chunk_count": row[2],
        }
        for row in rows
    ]


def rename_data_folder(data_folder: str, new_name: str, conn) -> int:
    """Rename a data folder and return the number of chunks updated."""
    if data_folder == new_name:
        raise ValueError("new folder name must differ from the current name")
    if not database_is_initialized(conn):
        return 0

    with conn.cursor() as cur:
        cur.execute(
            "SELECT EXISTS(SELECT 1 FROM chunks WHERE data_folder = %s)",
            (new_name,),
        )
        if cur.fetchone()[0]:
            raise ValueError(f"folder '{new_name}' already exists")

        cur.execute(
            "UPDATE chunks SET data_folder = %s WHERE data_folder = %s",
            (new_name, data_folder),
        )
        renamed_count = cur.rowcount

    conn.commit()
    return renamed_count