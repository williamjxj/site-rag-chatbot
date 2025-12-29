"""Database models and connection."""

import logging
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, JSON, create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector

from .config import settings

logger = logging.getLogger(__name__)

# Create engine and session
engine = create_engine(settings.database_url, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()


class Chunk(Base):
    """Chunk model representing processed content segments."""

    __tablename__ = "chunks"

    id = Column(String, primary_key=True)
    source = Column(String, nullable=False)  # "web" | "file"
    uri = Column(String, nullable=False)  # url or file path
    title = Column(String, nullable=True)
    heading_path = Column(JSON, nullable=True)
    text = Column(Text, nullable=False)
    text_hash = Column(String(64), nullable=False)
    embedding = Column(Vector, nullable=True)  # Variable dimensions: 1536 (OpenAI) or 384 (free model)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self) -> str:
        """String representation."""
        return f"<Chunk(id={self.id[:8]}..., uri={self.uri}, source={self.source})>"


def init_db() -> None:
    """
    Initialize database schema and pgvector extension.
    
    Raises:
        ValueError: If database connection fails
    """
    # Validate database connection
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection validated successfully")
    except SQLAlchemyError as e:
        error_msg = (
            f"Failed to connect to database at {settings.database_url}. "
            f"Please check your DATABASE_URL environment variable and ensure the database is running. "
            f"Error: {str(e)}"
        )
        logger.error(error_msg)
        raise ValueError(error_msg) from e
    
    # Create pgvector extension FIRST (before creating tables with VECTOR type)
    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
    
    # Now create tables (which use the VECTOR type)
    Base.metadata.create_all(bind=engine)
    
    # Create indexes for performance
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                CREATE INDEX IF NOT EXISTS idx_chunks_source ON chunks(source);
                CREATE INDEX IF NOT EXISTS idx_chunks_uri ON chunks(uri);
                CREATE INDEX IF NOT EXISTS idx_chunks_text_hash ON chunks(text_hash);
                """
            )
        )
        # Create vector index if it doesn't exist
        try:
            conn.execute(
                text(
                    """
                    CREATE INDEX IF NOT EXISTS idx_chunks_embedding 
                    ON chunks USING ivfflat (embedding vector_cosine_ops);
                    """
                )
            )
        except Exception:
            # Index creation might fail if no embeddings exist yet
            pass
        
        # Migrate existing Vector(1536) column to flexible Vector type if needed
        try:
            # Check if column exists and has size constraint
            result = conn.execute(
                text(
                    """
                    SELECT data_type, udt_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'chunks' AND column_name = 'embedding';
                    """
                )
            ).fetchone()
            
            if result and result[1] == 'vector':
                # Column exists, try to alter if it has size constraint
                # Note: PostgreSQL pgvector doesn't enforce size in type, but SQLAlchemy might
                # This is a no-op if already flexible, safe to run
                try:
                    conn.execute(text("ALTER TABLE chunks ALTER COLUMN embedding TYPE vector;"))
                    logger.info("Updated embedding column to support variable dimensions")
                except Exception as e:
                    # Column might already be flexible or migration not needed
                    logger.debug(f"Vector column migration check: {e}")
        except Exception as e:
            # Table might not exist yet, or migration not applicable
            logger.debug(f"Vector dimension migration check: {e}")
