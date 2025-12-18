"""Chat API route handler."""

from fastapi import APIRouter, HTTPException, status

from ...rag.chat import answer
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
