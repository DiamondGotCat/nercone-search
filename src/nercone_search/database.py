# ┌─────────────────────────────────────────┐
# │ database.py on Nercone Search           │
# │ Copyright (c) 2026 DiamondGotCat        │
# │ Made by Nercone / MIT License           │
# └─────────────────────────────────────────┘

import uuid
import torch
import psycopg2
from pgvector.psycopg2 import register_vector
from contextlib import contextmanager
from .config import EmbeddingDimension, DatabaseHost, DatabasePort, DatabaseName, DatabaseTableName, DatabaseUser, DatabasePassword

@contextmanager
def get_connection():
    conn = None
    try:
        conn = psycopg2.connect(
            dbname=DatabaseName,
            host=DatabaseHost,
            port=DatabasePort,
            user=DatabaseUser,
            password=DatabasePassword
        )
        yield conn
    finally:
        if conn:
            conn.close()

def initialize(exist_ok: bool = True):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            conn.commit()

            register_vector(conn)

            cur.execute(f"SELECT to_regclass('{DatabaseTableName}');")
            table_exists = cur.fetchone()[0] is not None

            if table_exists:
                if not exist_ok:
                    raise FileExistsError(f"Table '{DatabaseTableName}' already exists.")
                else:
                    return

            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")

            cur.execute(f"""
                CREATE TABLE {DatabaseTableName} (
                    id UUID PRIMARY KEY,
                    url TEXT UNIQUE NOT NULL,
                    title TEXT,
                    description TEXT,
                    markdown TEXT,
                    keywords TEXT[],
                    embedding vector({EmbeddingDimension}),
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
            """)

            cur.execute("""
                CREATE OR REPLACE FUNCTION trigger_set_timestamp()
                RETURNS TRIGGER AS $$
                BEGIN
                  NEW.updated_at = NOW();
                  RETURN NEW;
                END;
                $$ LANGUAGE plpgsql;
            """)
            cur.execute(f"""
                DROP TRIGGER IF EXISTS set_timestamp ON {DatabaseTableName};
                CREATE TRIGGER set_timestamp
                BEFORE UPDATE ON {DatabaseTableName}
                FOR EACH ROW
                EXECUTE FUNCTION trigger_set_timestamp();
            """)

            conn.commit()

def append(url: str, title: str = "No Title", description: str = "No description.", markdown: str = "", keywords: list[str] = [], tensor: torch.Tensor | None = None):
    embedding_list = tensor.tolist() if tensor is not None else None
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(f"""
                INSERT INTO {DatabaseTableName} (id, url, title, description, markdown, keywords, embedding)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (url)
                DO UPDATE SET
                    title = EXCLUDED.title,
                    description = EXCLUDED.description,
                    markdown = EXCLUDED.markdown,
                    keywords = EXCLUDED.keywords,
                    embedding = EXCLUDED.embedding;
            """, (str(uuid.uuid4()), url, title, description, markdown, keywords, embedding_list))
            conn.commit()

def search(tensor: torch.Tensor | None = None, nums: int = 50) -> list[str]:
    if tensor is None:
        return []

    embedding_list = tensor.tolist()
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT id
                FROM {DatabaseTableName}
                ORDER BY embedding <=> %s::vector
                LIMIT %s;
                """,
                (embedding_list, nums)
            )
            results = cur.fetchall()
            return [str(row[0]) for row in results]

def get(id: str) -> dict:
    try:
        uuid.UUID(id)
    except ValueError:
        return {"id": id, "url": "", "title": "", "description": "", "markdown": "", "keywords": []}

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT url, title, description, markdown, keywords FROM {DatabaseTableName} WHERE id = %s;", (id,))
            result = cur.fetchone()
            if result:
                return {
                    "url": result[0],
                    "title": result[1],
                    "description": result[2],
                    "markdown": result[3],
                    "keywords": result[4]
                }
            else:
                return {"id": id, "url": "", "title": "", "description": "", "markdown": "", "keywords": []}
