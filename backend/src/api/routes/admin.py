"""Admin API route handlers."""

from sqlalchemy import select, func, and_
from fastapi import APIRouter, HTTPException, status, Query

from ...db import SessionLocal, Chunk
from ..models import Document, DocumentListResponse, DeleteResponse, ErrorResponse

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/documents", response_model=DocumentListResponse, status_code=status.HTTP_200_OK)
async def list_documents(
    source: str | None = Query(None, enum=["web", "file"], description="Filter by source type"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of documents"),
    offset: int = Query(0, ge=0, description="Number of documents to skip"),
) -> DocumentListResponse:
    """
    List all ingested documents with metadata.

    Args:
        source: Optional filter by source type
        limit: Maximum number of documents to return
        offset: Number of documents to skip

    Returns:
        Document list response with documents and pagination info
    """
    with SessionLocal() as db:
        # Build query
        query = select(
            Chunk.uri,
            Chunk.source,
            func.max(Chunk.title).label("title"),
            func.count(Chunk.id).label("chunk_count"),
            func.min(Chunk.created_at).label("first_ingested_at"),
            func.max(Chunk.updated_at).label("last_updated_at"),
        ).group_by(Chunk.uri, Chunk.source)

        if source:
            query = query.where(Chunk.source == source)

        # Get total count
        count_query = select(func.count()).select_from(
            query.subquery()
        )
        total = db.execute(count_query).scalar() or 0

        # Apply pagination
        query = query.limit(limit).offset(offset)

        # Execute query
        results = db.execute(query).all()

        documents = [
            Document(
                uri=row.uri,
                source=row.source,
                title=row.title,
                chunk_count=row.chunk_count,
                first_ingested_at=row.first_ingested_at,
                last_updated_at=row.last_updated_at,
            )
            for row in results
        ]

        return DocumentListResponse(
            documents=documents,
            total=total,
            limit=limit,
            offset=offset,
        )


@router.delete("/documents/{document_id:path}", response_model=DeleteResponse, status_code=status.HTTP_200_OK)
async def delete_document(document_id: str) -> DeleteResponse:
    """
    Delete a document and all its chunks from the knowledge base.

    Args:
        document_id: URI of the document to delete

    Returns:
        Delete response with number of chunks deleted

    Raises:
        HTTPException: If document not found or deletion fails
    """
    with SessionLocal() as db:
        # Find chunks by URI
        chunks = db.execute(
            select(Chunk).where(Chunk.uri == document_id)
        ).scalars().all()

        if not chunks:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": "NOT_FOUND",
                    "message": f"Document not found: {document_id}",
                    "details": None,
                },
            )

        chunk_count = len(chunks)
        # Delete all chunks
        for chunk in chunks:
            db.delete(chunk)
        db.commit()

        return DeleteResponse(
            ok=True,
            message=f"Document deleted successfully",
            chunks_deleted=chunk_count,
        )
