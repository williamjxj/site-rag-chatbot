"""Chat API route handler."""

from fastapi import APIRouter, Depends, HTTPException, status

from ...config import validate_api_keys
from ...db import User
from ...rag.chat import answer
from ..models import ChatRequest, ChatResponse
from .auth import get_current_user

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat_endpoint(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
) -> ChatResponse:
    if not request.question or not request.question.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "VALIDATION_ERROR",
                "message": "Question cannot be empty",
                "details": None,
            },
        )

    if len(request.question) > 1000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "VALIDATION_ERROR",
                "message": "Question exceeds maximum length of 1000 characters",
                "details": None,
            },
        )

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
        result = answer(request.question, current_user.id)
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
