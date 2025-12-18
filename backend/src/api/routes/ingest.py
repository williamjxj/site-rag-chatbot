"""Ingestion API route handler."""

from fastapi import APIRouter, HTTPException, status

from ...ingest.pipeline import ingest_all
from ..models import IngestRequest, IngestResponse, ErrorResponse

router = APIRouter(prefix="/ingest", tags=["Ingestion"])


@router.post("", response_model=IngestResponse, status_code=status.HTTP_200_OK)
async def ingest_endpoint(request: IngestRequest | None = None) -> IngestResponse:
    """
    Trigger content ingestion.

    Args:
        request: Optional ingest request with source and force flags

    Returns:
        Ingest response with status

    Raises:
        HTTPException: If ingestion fails
    """
    try:
        source = request.source if request else "all"
        stats = ingest_all(source=source)
        return IngestResponse(
            ok=True,
            message=f"Ingestion completed. Web chunks: {stats['web_chunks']}, File chunks: {stats['file_chunks']}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "INGESTION_ERROR",
                "message": f"Failed to ingest content: {str(e)}",
                "details": None,
            },
        ) from e
