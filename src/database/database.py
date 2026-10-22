# database.py - pgvector table setup with metadata
import psycopg2
from pgvector.psycopg2 import register_vector

from ..config import CONFIG


def get_connection():
    conn = psycopg2.connect(CONFIG["database_url"])
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'vector')"
            )
            vector_is_available = cur.fetchone()[0]
        if vector_is_available:
            register_vector(conn)
    except Exception:
        conn.close()
        raise
    return conn


def create_tables(conn):
    """Create the clean database schema for a new index."""
    with conn.cursor() as cur:
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS chunks (
                id SERIAL PRIMARY KEY,
                embedding vector({CONFIG["embedding_dim"]}),
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
                context_prefix TEXT,
                index_profile TEXT NOT NULL DEFAULT 'baseline',
                ingested_at TIMESTAMP DEFAULT NOW(),
                search_vector TSVECTOR GENERATED ALWAYS AS (
                    to_tsvector(
                        'english', coalesce(context_prefix, '') || ' ' || content
                    )
                ) STORED
            );
        """)
        cur.execute("""
            ALTER TABLE chunks
                ADD COLUMN IF NOT EXISTS context_prefix TEXT,
                ADD COLUMN IF NOT EXISTS index_profile TEXT NOT NULL DEFAULT 'baseline';
        """)
        cur.execute("""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1
                    FROM pg_attribute attribute
                    JOIN pg_class relation ON relation.oid = attribute.attrelid
                    JOIN pg_attrdef definition
                      ON definition.adrelid = relation.oid
                     AND definition.adnum = attribute.attnum
                    WHERE relation.relname = 'chunks'
                      AND attribute.attname = 'search_vector'
                      AND pg_get_expr(definition.adbin, definition.adrelid)
                          LIKE '%context_prefix%'
                ) THEN
                    DROP INDEX IF EXISTS chunks_search_vector_idx;
                    ALTER TABLE chunks DROP COLUMN IF EXISTS search_vector;
                    ALTER TABLE chunks ADD COLUMN search_vector TSVECTOR
                        GENERATED ALWAYS AS (
                            to_tsvector(
                                'english', coalesce(context_prefix, '') || ' ' || content
                            )
                        ) STORED;
                END IF;
            END
            $$;
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
    """Create or migrate the schema and report whether it was newly created."""
    already_initialized = database_is_initialized(conn)
    create_tables(conn)
    return not already_initialized


def data_folder_exists(data_folder: str, conn) -> bool:
    """Return whether an initialized database contains chunks for a folder."""
    if not database_is_initialized(conn):
        return False
    with conn.cursor() as cur:
        cur.execute(
            "SELECT EXISTS(SELECT 1 FROM chunks WHERE data_folder = %s)",
            (data_folder,),
        )
        return cur.fetchone()[0]


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