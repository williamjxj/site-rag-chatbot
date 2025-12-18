"""Database models and connection."""

from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, JSON, create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector

from .config import settings

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
    embedding = Column(Vector(1536), nullable=True)  # 1536 for text-embedding-3-small
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self) -> str:
        """String representation."""
        return f"<Chunk(id={self.id[:8]}..., uri={self.uri}, source={self.source})>"


def init_db() -> None:
    """Initialize database schema and pgvector extension."""
    Base.metadata.create_all(bind=engine)
    # Ensure pgvector extension exists
    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        # Create indexes for performance
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
