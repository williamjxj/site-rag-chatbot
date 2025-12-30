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


class UploadResponse(BaseModel):
    """Response model for upload endpoint."""

    ok: bool = Field(..., description="Whether upload and ingestion was successful")
    message: str = Field(..., description="Status message")
    filename: str = Field(..., description="Name of uploaded file")
    chunks_ingested: int = Field(..., ge=0, description="Number of chunks ingested from the file")


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str = Field(..., description="Error type or code")
    message: str = Field(..., description="Human-readable error message")
    details: dict | None = Field(None, description="Additional error details")


class ProviderOption(BaseModel):
    """Provider option model for configuration response."""

    value: str = Field(..., enum=["openai", "local"], description="Provider identifier")
    label: str = Field(..., description="Human-readable provider name")
    description: str | None = Field(None, description="Optional description of the provider")


class ConfigResponse(BaseModel):
    """Response model for embedding provider configuration endpoints."""

    embedding_provider: str = Field(..., enum=["openai", "local", ""], description="Current embedding provider. Empty string means auto-detect.")
    embedding_model: str | None = Field(None, description="Current embedding model name (derived from provider)")
    available_providers: list[ProviderOption] = Field(..., description="List of available embedding providers with metadata")


class UpdateConfigRequest(BaseModel):
    """Request model for updating embedding provider configuration."""

    embedding_provider: str = Field(..., enum=["openai", "local"], description="Embedding provider to use. Must be either 'openai' or 'local'.")
