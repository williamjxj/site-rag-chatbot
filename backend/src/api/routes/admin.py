"""Admin API route handlers."""

import shutil
from pathlib import Path
from sqlalchemy import select, func, and_, text
from fastapi import APIRouter, HTTPException, status, Query, UploadFile, File
from fastapi.responses import JSONResponse

from ...db import SessionLocal, Chunk
from ...config import settings, update_embedding_provider
from ...ingest.pipeline import ingest_single_file
from ..models import (
    Document,
    DocumentListResponse,
    DeleteResponse,
    ErrorResponse,
    UploadResponse,
    ConfigResponse,
    UpdateConfigRequest,
    ProviderOption,
)

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
    Delete a document and all its chunks from the knowledge base (including pgvector embeddings).

    Args:
        document_id: URI of the document to delete (URL-decoded)

    Returns:
        Delete response with number of chunks deleted

    Raises:
        HTTPException: If document not found or deletion fails
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # URL decode the document_id in case it was encoded
    from urllib.parse import unquote
    decoded_uri = unquote(document_id)
    
    logger.info(f"Deleting document with URI: {decoded_uri}")
    
    with SessionLocal() as db:
        try:
            # Find chunks by URI (exact match)
            chunks = db.execute(
                select(Chunk).where(Chunk.uri == decoded_uri)
            ).scalars().all()

            if not chunks:
                logger.warning(f"No chunks found for URI: {decoded_uri}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "error": "NOT_FOUND",
                        "message": f"Document not found: {decoded_uri}",
                        "details": None,
                    },
                )

            chunk_count = len(chunks)
            logger.info(f"Found {chunk_count} chunks to delete for URI: {decoded_uri}")
            
            # Delete all chunks (this also deletes the embeddings from pgvector)
            for chunk in chunks:
                db.delete(chunk)
            
            # Commit the transaction
            db.commit()
            
            # Verify deletion worked
            remaining = db.execute(
                select(func.count(Chunk.id)).where(Chunk.uri == decoded_uri)
            ).scalar() or 0
            
            if remaining > 0:
                logger.error(f"Deletion verification failed: {remaining} chunks still exist for URI: {decoded_uri}")
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail={
                        "error": "DELETION_VERIFICATION_FAILED",
                        "message": f"Failed to delete all chunks. {remaining} chunks still exist.",
                        "details": None,
                    },
                )
            
            logger.info(f"Successfully deleted {chunk_count} chunks for URI: {decoded_uri}")

            return DeleteResponse(
                ok=True,
                message=f"Document deleted successfully. Removed {chunk_count} chunks from database and pgvector.",
                chunks_deleted=chunk_count,
            )
        except HTTPException:
            # Re-raise HTTP exceptions as-is
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting document {decoded_uri}: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": "DELETION_ERROR",
                    "message": f"Failed to delete document: {str(e)}",
                    "details": None,
                },
            ) from e


@router.get("/config/embedding-provider", response_model=ConfigResponse, status_code=status.HTTP_200_OK)
async def get_embedding_provider() -> ConfigResponse:
    """
    Get current embedding provider configuration.
    
    Returns:
        ConfigResponse with current provider, model, and available options
    """
    provider = settings.embedding_provider or ""
    model = (
        settings.embedding_model
        if provider == "openai"
        else settings.free_embedding_model
    )
    
    return ConfigResponse(
        embedding_provider=provider,
        embedding_model=model,
        available_providers=[
            ProviderOption(
                value="openai",
                label="OpenAI (text-embedding-3-small)",
                description="Uses OpenAI API for embeddings. Requires API key.",
            ),
            ProviderOption(
                value="local",
                label="Sentence Transformers (all-MiniLM-L6-v2)",
                description="Uses local sentence-transformers model. No API key required.",
            ),
        ],
    )


@router.put("/config/embedding-provider", response_model=ConfigResponse, status_code=status.HTTP_200_OK)
async def update_embedding_provider_config(request: UpdateConfigRequest) -> ConfigResponse:
    """
    Update embedding provider configuration.
    
    Args:
        request: UpdateConfigRequest with new provider value
    
    Returns:
        ConfigResponse with updated configuration
    
    Raises:
        HTTPException: If provider value is invalid or update fails
    """
    try:
        update_embedding_provider(request.embedding_provider)
        return await get_embedding_provider()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "INVALID_PROVIDER",
                "message": str(e),
                "details": None,
            },
        ) from e
    except IOError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "CONFIG_UPDATE_ERROR",
                "message": f"Failed to update configuration: {str(e)}",
                "details": None,
            },
        ) from e
