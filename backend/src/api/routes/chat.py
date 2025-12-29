"""Chat API route handler."""

from fastapi import APIRouter, HTTPException, status

from ...rag.chat import answer
from ...config import validate_api_keys
from ..models import ChatRequest, ChatResponse, ErrorResponse

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat_endpoint(request: ChatRequest) -> ChatResponse:
    """
    Handle chat requests and return answers with source citations.

    Args:
        request: Chat request with user question

    Returns:
        Chat response with answer and sources

    Raises:
        HTTPException: If chat processing fails
    """
    # Validate question is not empty or whitespace-only
    if not request.question or not request.question.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "VALIDATION_ERROR",
                "message": "Question cannot be empty",
                "details": None,
            },
        )

    # Validate question length (max 1000 characters)
    if len(request.question) > 1000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "VALIDATION_ERROR",
                "message": "Question exceeds maximum length of 1000 characters",
                "details": None,
            },
        )

    # Validate API keys are configured
    try:
        validate_api_keys()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "CONFIGURATION_ERROR",
                "message": str(e),
                "details": None,
            },
        ) from e

    try:
        result = answer(request.question)
        return ChatResponse(
            answer=result["answer"],
            sources=result["sources"],
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "CHAT_ERROR",
                "message": f"Failed to process chat request: {str(e)}",
                "details": None,
            },
        ) from e
