"""One-time ingestion script for testing."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.db import init_db
from src.ingest.pipeline import ingest_all

if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("Starting ingestion...")
    ingest_all()
    print("Ingestion complete.")
