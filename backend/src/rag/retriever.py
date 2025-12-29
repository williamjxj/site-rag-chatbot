"""Semantic search retrieval using vector similarity."""

import logging
from sqlalchemy import select, func, case
from sqlalchemy.exc import SQLAlchemyError

from ..db import SessionLocal, Chunk
from ..config import settings

logger = logging.getLogger(__name__)


def retrieve(query_embedding: list[float], top_k: int | None = None) -> list[Chunk]:
    """
    Retrieve top-k most similar chunks using cosine distance.
    
    Supports mixed embedding dimensions (e.g., 1536-dim from OpenAI and 384-dim from free model).
    Only retrieves chunks with embeddings that match the query embedding dimension.
    
    Note: pgvector requires matching dimensions for cosine_distance. Chunks with different
    dimensions are automatically filtered out during retrieval.

    Args:
        query_embedding: Query vector embedding (dimension must match stored embeddings)
        top_k: Number of chunks to retrieve (defaults to settings.top_k)

    Returns:
        List of Chunk objects ordered by similarity (only chunks with matching dimensions)
    """
    if top_k is None:
        top_k = settings.top_k

    query_dim = len(query_embedding)
    logger.debug(f"Retrieving chunks with query embedding dimension: {query_dim}")

    try:
        with SessionLocal() as db:
            # pgvector cosine_distance requires matching dimensions
            # Chunks with different dimensions will be filtered automatically by the database
            stmt = (
                select(Chunk)
                .where(Chunk.embedding.is_not(None))
                .order_by(Chunk.embedding.cosine_distance(query_embedding))
                .limit(top_k)
            )
            rows = db.execute(stmt).scalars().all()
            
            # Log if we got fewer results than requested (might indicate dimension mismatch)
            if len(rows) < top_k:
                logger.debug(
                    f"Retrieved {len(rows)} chunks (requested {top_k}). "
                    "This may indicate some chunks have different embedding dimensions."
                )
            
            return list(rows)
    except SQLAlchemyError as e:
        error_msg = str(e)
        # Check for dimension mismatch errors
        if "dimension" in error_msg.lower() or "vector" in error_msg.lower():
            logger.warning(
                f"Possible dimension mismatch during retrieval: {e}. "
                "Ensure query embedding dimension matches stored embeddings, "
                "or re-ingest content with the current embedding model."
            )
        logger.error(f"Database error during retrieval: {e}")
        raise ValueError(
            f"Database connection error: {str(e)}. Please check your database connection and try again."
        )
    except Exception as e:
        logger.error(f"Unexpected error during retrieval: {e}")
        raise ValueError(
            f"Error retrieving content: {str(e)}. Please try again."
        )
