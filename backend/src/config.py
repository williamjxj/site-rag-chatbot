"""Configuration and settings management."""

import os
from pathlib import Path
from pydantic_settings import BaseSettings

# Get backend directory (parent of src/)
BACKEND_DIR = Path(__file__).parent.parent
ENV_FILE = BACKEND_DIR / ".env"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    database_url: str = os.getenv("DATABASE_URL", "postgresql+psycopg://rag:rag@localhost:5432/rag")

    # Website + docs
    sitemap_url: str = os.getenv("SITEMAP_URL", "")
    docs_dir: str = os.getenv("DOCS_DIR", "./docs")

    # OpenAI-compatible provider (DeepSeek or OpenAI)
    llm_provider: str = os.getenv("LLM_PROVIDER", "openai")
    openai_base_url: str = os.getenv("OPENAI_BASE_URL", "")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    # Embedding API key (use OpenAI key for embeddings, separate from chat)
    embedding_api_key: str = os.getenv("EMBEDDING_API_KEY", "")  # Falls back to openai_api_key if not set
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    # Free embedding model configuration
    embedding_provider: str = os.getenv("EMBEDDING_PROVIDER", "")  # "openai" | "local" | "" (auto-detect)
    free_embedding_model: str = os.getenv("FREE_EMBEDDING_MODEL", "all-MiniLM-L6-v2")

    # Chat LLM
    chat_model: str = os.getenv("CHAT_MODEL", "deepseek-chat")
    deepseek_api_key: str = os.getenv("DEEPSEEK_API_KEY", "")

    # Vector store
    vector_store: str = os.getenv("VECTOR_STORE", "memory")

    # Retrieval
    top_k: int = int(os.getenv("TOP_K", "6"))
    max_context_chars: int = int(os.getenv("MAX_CONTEXT_CHARS", "12000"))

    # System prompt for chat LLM (can be customized via SYSTEM_PROMPT environment variable)
    system_prompt: str = os.getenv(
        "SYSTEM_PROMPT",
        "You are a helpful website assistant.\n"
        "Answer questions ONLY using the provided context from the website and documents.\n"
        "If the answer is not in the context, say you don't know and suggest where the user might look.\n"
        "Always include a short Sources list at the end with URLs or file paths."
    )

    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    class Config:
        """Pydantic config."""

        env_file = str(ENV_FILE) if ENV_FILE.exists() else None
        case_sensitive = False


settings = Settings()


def validate_api_keys() -> None:
    """
    Validate that at least one API key is configured.
    
    Raises:
        ValueError: If neither OPENAI_API_KEY nor DEEPSEEK_API_KEY is set
    """
    if not settings.openai_api_key and not settings.deepseek_api_key:
        raise ValueError(
            "At least one API key must be configured. "
            "Please set either OPENAI_API_KEY or DEEPSEEK_API_KEY in your environment variables."
        )
