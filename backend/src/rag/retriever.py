"""Semantic search retrieval using vector similarity."""

import logging
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from ..db import SessionLocal, Chunk
from ..config import settings

logger = logging.getLogger(__name__)


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

    try:
        with SessionLocal() as db:
            stmt = (
                select(Chunk)
                .where(Chunk.embedding.is_not(None))
                .order_by(Chunk.embedding.cosine_distance(query_embedding))
                .limit(top_k)
            )
            rows = db.execute(stmt).scalars().all()
            return list(rows)
    except SQLAlchemyError as e:
        logger.error(f"Database error during retrieval: {e}")
        raise ValueError(
            f"Database connection error: {str(e)}. Please check your database connection and try again."
        )
    except Exception as e:
        logger.error(f"Unexpected error during retrieval: {e}")
        raise ValueError(
            f"Error retrieving content: {str(e)}. Please try again."
        )
