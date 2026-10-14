from collections import defaultdict
from dataclasses import dataclass

import numpy as np
import psycopg

from hybrid_rag.core.config import settings
from hybrid_rag.db.store import connect
from hybrid_rag.embed.embedder import embedder


@dataclass
class RetrievedChunk:
    id: int
    source: str
    chunk_index: int
    content: str
    score: float


def vector_search(conn: psycopg.Connection, query_embedding: np.ndarray, limit: int) -> list[int]:
    rows = conn.execute(
        'SELECT id FROM chunks ORDER BY embedding <=> %s LIMIT %s',
        (query_embedding, limit),
    ).fetchall()
    return [r[0] for r in rows]


def keyword_search(conn: psycopg.Connection, query: str, limit: int) -> list[int]:
    # websearch_to_tsquery ANDs every term; swap to OR so natural-language questions match
    # any term, and let ts_rank_cd rank chunks that match more terms higher.
    rows = conn.execute(
        """
        SELECT id FROM chunks,
            (SELECT replace(websearch_to_tsquery('english', %s)::text, ' & ', ' | ')::tsquery AS q) AS query
        WHERE tsv @@ q
        ORDER BY ts_rank_cd(tsv, q) DESC
        LIMIT %s
        """,
        (query, limit),
    ).fetchall()
    return [r[0] for r in rows]


def reciprocal_rank_fusion(rankings: list[list[int]], k: int) -> list[tuple[int, float]]:
    scores: dict[int, float] = defaultdict(float)
    for ranking in rankings:
        for rank, chunk_id in enumerate(ranking, start=1):
            scores[chunk_id] += 1 / (k + rank)
    return sorted(scores.items(), key=lambda item: item[1], reverse=True)


def hybrid_search(query: str, top_k: int = 5) -> list[RetrievedChunk]:
    query_embedding = embedder.embed_query(query)
    with connect() as conn:
        fused = reciprocal_rank_fusion(
            [
                vector_search(conn, query_embedding, settings.candidate_k),
                keyword_search(conn, query, settings.candidate_k),
            ],
            settings.rrf_k,
        )[:top_k]
        if not fused:
            return []
        rows = conn.execute(
            'SELECT id, source, chunk_index, content FROM chunks WHERE id = ANY(%s)',
            ([chunk_id for chunk_id, _ in fused],),
        ).fetchall()

    by_id = {row[0]: row for row in rows}
    return [RetrievedChunk(*by_id[chunk_id], score=score) for chunk_id, score in fused]
