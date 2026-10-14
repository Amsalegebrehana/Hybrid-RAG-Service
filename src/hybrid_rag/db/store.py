from pathlib import Path

import numpy as np
import psycopg
from pgvector.psycopg import register_vector

from hybrid_rag.core.config import settings
from hybrid_rag.ingest.chunker import Chunk

SCHEMA_PATH = Path(__file__).with_name('schema.sql')


def connect() -> psycopg.Connection:
    conn = psycopg.connect(settings.database_url)
    register_vector(conn)
    return conn


def init_db() -> None:
    # Plain connection: register_vector needs the extension, which the schema creates.
    with psycopg.connect(settings.database_url) as conn:
        conn.execute(SCHEMA_PATH.read_text())


def replace_chunks(chunks: list[Chunk], embeddings: np.ndarray) -> None:
    """Replace all rows for the given chunks' sources, so re-ingesting a shrunken file leaves no stale chunks."""
    sources = sorted({c.source for c in chunks})
    with connect() as conn, conn.cursor() as cur:
        cur.execute('DELETE FROM chunks WHERE source = ANY(%s)', (sources,))
        cur.executemany(
            'INSERT INTO chunks (source, chunk_index, content, embedding) VALUES (%s, %s, %s, %s)',
            [(c.source, c.chunk_index, c.text, e) for c, e in zip(chunks, embeddings, strict=True)],
        )
