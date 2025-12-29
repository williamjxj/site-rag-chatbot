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
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

    # Chat LLM
    chat_model: str = os.getenv("CHAT_MODEL", "deepseek-chat")
    deepseek_api_key: str = os.getenv("DEEPSEEK_API_KEY", "")

    # Vector store
    vector_store: str = os.getenv("VECTOR_STORE", "memory")

    # Retrieval
    top_k: int = int(os.getenv("TOP_K", "6"))
    max_context_chars: int = int(os.getenv("MAX_CONTEXT_CHARS", "12000"))

    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    class Config:
        """Pydantic config."""

        env_file = str(ENV_FILE) if ENV_FILE.exists() else None
        case_sensitive = False


settings = Settings()
