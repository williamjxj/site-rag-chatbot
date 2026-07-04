"""Admin API route handlers."""

import shutil
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy import func, select, text

from ...auth import decode_token
from ...config import settings, update_embedding_provider
from ...db import Chunk, SessionLocal, User
from ...ingest.pipeline import ingest_single_file
from ..models import (
    BatchUploadItemResponse,
    BatchUploadResponse,
    ConfigResponse,
    DeleteResponse,
    Document,
    DocumentListResponse,
    ProviderOption,
    UpdateConfigRequest,
    UploadResponse,
)
from .auth import get_current_user

router = APIRouter(prefix="/admin", tags=["Admin"])


def _normalize_relative_path(file_name: str | None, relative_path: str | None = None) -> str:
    candidate = (relative_path or file_name or "uploaded_file").replace("\\", "/")
    path = Path(candidate)

    if path.is_absolute() or any(part == ".." for part in path.parts):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "INVALID_FILE_PATH",
                "message": "Relative paths must stay inside the selected folder",
                "details": None,
            },
        )

    safe_parts = [part for part in path.parts if part not in ("", ".")]
    if not safe_parts:
        return file_name or "uploaded_file"

    return Path(*safe_parts).as_posix()


def _allowed_file_extension(file_name: str | None) -> bool:
    allowed_extensions = {
        ".pdf",
        ".md",
        ".mdx",
        ".txt",
        ".doc",
        ".docx",
        ".xlsx",
        ".xls",
        ".ppt",
        ".pptx",
        ".html",
        ".htm",
        ".csv",
    }
    file_ext = Path(file_name).suffix.lower() if file_name else ""
    return file_ext in allowed_extensions


def _save_and_ingest_uploaded_file(
    file: UploadFile,
    current_user: User,
    relative_path: str | None = None,
) -> tuple[str, int]:
    if not _allowed_file_extension(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "INVALID_FILE_TYPE",
                "message": "File type not supported. Allowed types: .csv, .doc, .docx, .htm, .html, .md, .mdx, .pdf, .ppt, .pptx, .txt, .xls, .xlsx",
                "details": None,
            },
        )

    docs_path = Path(settings.docs_dir).resolve()
    docs_path.mkdir(parents=True, exist_ok=True)

    safe_relative_path = _normalize_relative_path(file.filename, relative_path)
    file_path = docs_path / safe_relative_path
    file_path.parent.mkdir(parents=True, exist_ok=True)

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

    try:
        chunks_ingested = ingest_single_file(file_path, current_user.id)
        return safe_relative_path, chunks_ingested
    except Exception as e:
        try:
            file_path.unlink()
        except OSError:
            pass
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "INGESTION_ERROR",
                "message": f"Failed to ingest uploaded file: {str(e)}",
                "details": None,
            },
        ) from e
@router.get("/documents", response_model=DocumentListResponse, status_code=status.HTTP_200_OK)
async def list_documents(
    source: str | None = Query(None, enum=["web", "file"], description="Filter by source type"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of documents"),
    offset: int = Query(0, ge=0, description="Number of documents to skip"),
    current_user: User = Depends(get_current_user),
) -> DocumentListResponse:
    with SessionLocal() as db:
        query = select(
            Chunk.uri,
            Chunk.source,
            func.max(Chunk.title).label("title"),
            func.count(Chunk.id).label("chunk_count"),
            func.min(Chunk.created_at).label("first_ingested_at"),
            func.max(Chunk.updated_at).label("last_updated_at"),
        ).where(Chunk.user_id == current_user.id).group_by(Chunk.uri, Chunk.source)

        if source:
            query = query.where(Chunk.source == source)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
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
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
) -> UploadResponse:
    """
    Upload a document file and immediately ingest it.

    Args:
        file: Uploaded file (PDF, MD, MDX, TXT, DOCX, XLSX, XLS, PPTX, HTML, CSV)

    Returns:
        Upload response with status and ingestion results

    Raises:
        HTTPException: If upload or ingestion fails
    """
    safe_relative_path, chunks_ingested = _save_and_ingest_uploaded_file(file, current_user)
    return UploadResponse(
        ok=True,
        message="File uploaded and ingested successfully",
        filename=safe_relative_path,
        chunks_ingested=chunks_ingested,
    )


@router.post("/upload/batch", response_model=BatchUploadResponse, status_code=status.HTTP_200_OK)
async def upload_documents_batch(
    files: list[UploadFile] = File(...),
    relative_paths: list[str] = Form(default=[]),
    current_user: User = Depends(get_current_user),
) -> BatchUploadResponse:
    results: list[BatchUploadItemResponse] = []
    chunks_ingested = 0
    succeeded_files = 0
    failed_files = 0

    for index, file in enumerate(files):
        submitted_relative_path = relative_paths[index] if index < len(relative_paths) else None
        try:
            saved_relative_path, file_chunks = _save_and_ingest_uploaded_file(
                file, current_user, submitted_relative_path
            )
            succeeded_files += 1
            chunks_ingested += file_chunks
            results.append(
                BatchUploadItemResponse(
                    ok=True,
                    filename=file.filename or saved_relative_path,
                    relative_path=saved_relative_path,
                    uri=saved_relative_path,
                    chunks_ingested=file_chunks,
                    message="Uploaded and ingested successfully",
                )
            )
        except HTTPException as e:
            failed_files += 1
            fallback_uri = (submitted_relative_path or file.filename or "uploaded_file").replace(
                "\\", "/"
            )
            error_message = (
                e.detail.get("message") if isinstance(e.detail, dict) else str(e.detail)
            ) or "Upload failed"
            results.append(
                BatchUploadItemResponse(
                    ok=False,
                    filename=file.filename or "uploaded_file",
                    relative_path=submitted_relative_path or (file.filename or "uploaded_file"),
                    uri=fallback_uri,
                    chunks_ingested=0,
                    message=error_message,
                )
            )
        except Exception as e:
            failed_files += 1
            fallback_uri = (submitted_relative_path or file.filename or "uploaded_file").replace(
                "\\", "/"
            )
            results.append(
                BatchUploadItemResponse(
                    ok=False,
                    filename=file.filename or "uploaded_file",
                    relative_path=submitted_relative_path or (file.filename or "uploaded_file"),
                    uri=fallback_uri,
                    chunks_ingested=0,
                    message=f"Failed to process file: {e}",
                )
            )

    return BatchUploadResponse(
        ok=succeeded_files > 0,
        message=(
            "Batch upload completed"
            if failed_files == 0
            else "Batch upload completed with some failures"
        ),
        total_files=len(files),
        succeeded_files=succeeded_files,
        failed_files=failed_files,
        chunks_ingested=chunks_ingested,
        results=results,
    )


@router.delete("/documents", response_model=DeleteResponse, status_code=status.HTTP_200_OK)
async def delete_all_documents(current_user: User = Depends(get_current_user)) -> DeleteResponse:
    with SessionLocal() as db:
        try:
            chunk_count = db.execute(
                select(func.count(Chunk.id)).where(Chunk.user_id == current_user.id)
            ).scalar() or 0

            db.execute(text("DELETE FROM chunks WHERE user_id = :user_id;"), {"user_id": current_user.id})
            db.commit()

            return DeleteResponse(
                ok=True,
                message="All your documents deleted successfully",
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


@router.delete(
    "/documents/{document_id:path}", response_model=DeleteResponse, status_code=status.HTTP_200_OK
)
async def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
) -> DeleteResponse:
    import logging

    logger = logging.getLogger(__name__)

    from urllib.parse import unquote

    decoded_uri = unquote(document_id)

    logger.info(f"Deleting document with URI: {decoded_uri}")

    with SessionLocal() as db:
        try:
            # Find chunks by URI (exact match) AND user_id
            chunks = db.execute(
                select(Chunk).where(Chunk.uri == decoded_uri, Chunk.user_id == current_user.id)
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
            remaining = (
                db.execute(
                    select(func.count(Chunk.id)).where(
                        Chunk.uri == decoded_uri, Chunk.user_id == current_user.id
                    )
                ).scalar()
                or 0
            )

            if remaining > 0:
                logger.error(
                    f"Deletion verification failed: {remaining} chunks still exist for URI: {decoded_uri}"
                )
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


@router.get(
    "/config/embedding-provider", response_model=ConfigResponse, status_code=status.HTTP_200_OK
)
async def get_embedding_provider() -> ConfigResponse:
    """
    Get current embedding provider configuration.

    Returns:
        ConfigResponse with current provider, model, and available options
    """
    provider = settings.embedding_provider or ""
    model = settings.embedding_model if provider == "openai" else settings.free_embedding_model

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


@router.put(
    "/config/embedding-provider", response_model=ConfigResponse, status_code=status.HTTP_200_OK
)
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
    except OSError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "CONFIG_UPDATE_ERROR",
                "message": f"Failed to update configuration: {str(e)}",
                "details": None,
            },
        ) from e
