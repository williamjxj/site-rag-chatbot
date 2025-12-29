"""Semantic search retrieval using vector similarity."""

from sqlalchemy import select

from ..db import SessionLocal, Chunk
from ..config import settings


def retrieve(query_embedding: list[float], top_k: int | None = None) -> list[Chunk]:
    """
    Retrieve top-k most similar chunks using cosine distance.

    Args:
        query_embedding: Query vector embedding
        top_k: Number of chunks to retrieve (defaults to settings.top_k)

    Returns:
        List of Chunk objects ordered by similarity
    """
    if top_k is None:
        top_k = settings.top_k

    with SessionLocal() as db:
        stmt = (
            select(Chunk)
            .where(Chunk.embedding.is_not(None))
            .order_by(Chunk.embedding.cosine_distance(query_embedding))
            .limit(top_k)
        )
        rows = db.execute(stmt).scalars().all()
        return list(rows)
