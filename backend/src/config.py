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
    embedding_api_key: str = os.getenv(
        "EMBEDDING_API_KEY", ""
    )  # Falls back to openai_api_key if not set
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    # Free embedding model configuration
    embedding_provider: str = os.getenv(
        "EMBEDDING_PROVIDER", ""
    )  # "openai" | "local" | "" (auto-detect)
    free_embedding_model: str = os.getenv("FREE_EMBEDDING_MODEL", "all-MiniLM-L6-v2")

    # Chat LLM
    chat_model: str = os.getenv("CHAT_MODEL", "deepseek-chat")
    deepseek_api_key: str = os.getenv("DEEPSEEK_API_KEY", "")
    kimi_api_key: str = os.getenv("KIMI_API_KEY", "")
    minimax_api_key: str = os.getenv("MINIMAX_API_KEY", "")
    active_llm: str = os.getenv("ACTIVE_LLM", "kimi")  # deepseek | kimi | minimax

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
        "Always include a short Sources list at the end with URLs or file paths.",
    )

    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "dev-secret-change-in-production")

    class Config:
        """Pydantic config."""

        env_file = str(ENV_FILE) if ENV_FILE.exists() else None
        case_sensitive = False
        extra = "ignore"


settings = Settings()


def validate_api_keys() -> None:
    """Validate that at least one LLM API key is configured based on active_llm."""
    provider = settings.active_llm
    if provider == "deepseek" and not settings.deepseek_api_key:
        raise ValueError("DEEPSEEK_API_KEY must be set when ACTIVE_LLM=deepseek")
    elif provider == "kimi" and not settings.kimi_api_key:
        raise ValueError("KIMI_API_KEY must be set when ACTIVE_LLM=kimi")
    elif provider == "minimax" and not settings.minimax_api_key:
        raise ValueError("MINIMAX_API_KEY must be set when ACTIVE_LLM=minimax")
    elif provider not in ("deepseek", "kimi", "minimax"):
        raise ValueError(f"Invalid ACTIVE_LLM: {provider}. Must be one of: deepseek, kimi, minimax")


def update_embedding_provider(value: str) -> None:
    """
    Update embedding provider in .env file and in-memory settings.

    Args:
        value: Embedding provider value ("openai" or "local")

    Raises:
        ValueError: If value is not "openai" or "local"
        IOError: If .env file cannot be read or written
    """
    import logging

    logger = logging.getLogger(__name__)

    if value not in ["openai", "local"]:
        raise ValueError(f"Invalid embedding provider: {value}. Must be 'openai' or 'local'.")

    # Update in-memory settings
    settings.embedding_provider = value

    # Update .env file
    env_file = BACKEND_DIR / ".env"

    # Read current .env file if it exists
    lines = []
    if env_file.exists():
        try:
            with open(env_file, encoding="utf-8") as f:
                lines = f.readlines()
        except OSError as e:
            logger.error(f"Failed to read .env file: {e}")
            raise OSError(f"Failed to read .env file: {e}") from e

    # Update or add EMBEDDING_PROVIDER line
    updated = False
    for i, line in enumerate(lines):
        if line.strip().startswith("EMBEDDING_PROVIDER="):
            lines[i] = f"EMBEDDING_PROVIDER={value}\n"
            updated = True
            break

    if not updated:
        lines.append(f"EMBEDDING_PROVIDER={value}\n")

    # Write back to .env file
    try:
        with open(env_file, "w", encoding="utf-8") as f:
            f.writelines(lines)
        logger.info(f"Updated EMBEDDING_PROVIDER to {value} in .env file")
    except OSError as e:
        logger.error(f"Failed to write .env file: {e}")
        raise OSError(f"Failed to write .env file: {e}") from e
