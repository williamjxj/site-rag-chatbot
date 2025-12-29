"""Admin API route handlers."""

import shutil
from pathlib import Path
from sqlalchemy import select, func, and_, text
from fastapi import APIRouter, HTTPException, status, Query, UploadFile, File
from fastapi.responses import JSONResponse

from ...db import SessionLocal, Chunk
from ...config import settings
from ...ingest.pipeline import ingest_single_file
from ..models import Document, DocumentListResponse, DeleteResponse, ErrorResponse, UploadResponse

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


@router.post("/upload", response_model=UploadResponse, status_code=status.HTTP_200_OK)
async def upload_document(file: UploadFile = File(...)) -> UploadResponse:
    """
    Upload a document file and immediately ingest it.
    
    Args:
        file: Uploaded file (PDF, MD, MDX, TXT, DOCX, XLSX, XLS, PPTX, HTML, CSV)
    
    Returns:
        Upload response with status and ingestion results
    
    Raises:
        HTTPException: If upload or ingestion fails
    """
    # Validate file type
    allowed_extensions = {
        ".pdf", ".md", ".mdx", ".txt",
        ".doc", ".docx", ".xlsx", ".xls", ".ppt", ".pptx",
        ".html", ".htm", ".csv"
    }
    file_ext = Path(file.filename).suffix.lower() if file.filename else ""
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "INVALID_FILE_TYPE",
                "message": f"File type not supported. Allowed types: {', '.join(allowed_extensions)}",
                "details": None,
            },
        )
    
    # Ensure uploads directory exists (resolve to absolute path)
    docs_path = Path(settings.docs_dir).resolve()
    docs_path.mkdir(parents=True, exist_ok=True)
    
    # Save file (use filename from upload, sanitize if needed)
    safe_filename = file.filename or "uploaded_file"
    # Prevent directory traversal
    if ".." in safe_filename or "/" in safe_filename or "\\" in safe_filename:
        safe_filename = Path(safe_filename).name
    file_path = docs_path / safe_filename
    try:
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "UPLOAD_ERROR",
                "message": f"Failed to save file: {str(e)}",
                "details": None,
            },
        ) from e
    
    # Ingest the uploaded file
    try:
        chunks_ingested = ingest_single_file(file_path)
        return UploadResponse(
            ok=True,
            message=f"File uploaded and ingested successfully",
            filename=file.filename,
            chunks_ingested=chunks_ingested,
        )
    except Exception as e:
        # Clean up file if ingestion fails
        try:
            file_path.unlink()
        except:
            pass
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "INGESTION_ERROR",
                "message": f"Failed to ingest uploaded file: {str(e)}",
                "details": None,
            },
        ) from e


@router.delete("/documents", response_model=DeleteResponse, status_code=status.HTTP_200_OK)
async def delete_all_documents() -> DeleteResponse:
    """
    Delete all documents and chunks from the knowledge base.
    
    Returns:
        Delete response with number of chunks deleted
    
    Raises:
        HTTPException: If deletion fails
    """
    with SessionLocal() as db:
        try:
            # Get count before deletion
            from sqlalchemy import select, func
            chunk_count = db.execute(select(func.count(Chunk.id))).scalar() or 0
            
            # Delete all chunks
            db.execute(text("DELETE FROM chunks;"))
            db.commit()
            
            return DeleteResponse(
                ok=True,
                message=f"All documents deleted successfully",
                chunks_deleted=chunk_count,
            )
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": "DELETION_ERROR",
                    "message": f"Failed to delete all documents: {str(e)}",
                    "details": None,
                },
            ) from e


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
