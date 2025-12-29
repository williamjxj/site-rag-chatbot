"""Pydantic models for API requests and responses."""

from datetime import datetime

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""

    question: str = Field(..., min_length=1, max_length=1000, description="The user's question")


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""

    answer: str = Field(..., description="The chatbot's answer to the question")
    sources: list[str] = Field(..., description="List of source URIs cited in the answer")


class IngestRequest(BaseModel):
    """Request model for ingest endpoint."""

    source: str = Field(default="all", enum=["web", "file", "all"], description="Which source to ingest")
    force: bool = Field(default=False, description="Force re-ingestion even if content hasn't changed")


class IngestResponse(BaseModel):
    """Response model for ingest endpoint."""

    ok: bool = Field(..., description="Whether ingestion started successfully")
    message: str = Field(..., description="Status message")
    job_id: str | None = Field(None, description="Optional job identifier for tracking progress")


class Document(BaseModel):
    """Document model for admin endpoints."""

    uri: str = Field(..., description="Document URI (URL or file path)")
    source: str = Field(..., enum=["web", "file"], description="Source type")
    title: str | None = Field(None, description="Document title")
    chunk_count: int = Field(..., ge=0, description="Number of chunks from this document")
    first_ingested_at: datetime | None = Field(None, description="When this document was first ingested")
    last_updated_at: datetime | None = Field(None, description="When this document was last updated")


class DocumentListResponse(BaseModel):
    """Response model for document list endpoint."""

    documents: list[Document] = Field(..., description="List of documents")
    total: int = Field(..., ge=0, description="Total number of documents")
    limit: int = Field(..., description="Maximum number returned")
    offset: int = Field(..., description="Number skipped")


class DeleteResponse(BaseModel):
    """Response model for delete endpoint."""

    ok: bool = Field(..., description="Whether deletion was successful")
    message: str = Field(..., description="Status message")
    chunks_deleted: int = Field(..., ge=0, description="Number of chunks deleted")


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str = Field(..., description="Error type or code")
    message: str = Field(..., description="Human-readable error message")
    details: dict | None = Field(None, description="Additional error details")
