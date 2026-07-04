"""One-time ingestion script for testing."""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import settings
from src.db import init_db
from src.ingest.pipeline import ingest_all

if __name__ == "__main__":
    # Ensure HF_TOKEN is in environment for Hugging Face model downloads
    if settings.hf_token and not os.environ.get("HF_TOKEN"):
        os.environ["HF_TOKEN"] = settings.hf_token

    print("Initializing database...")
    init_db()
    print("Starting ingestion...")
    ingest_all()
    print("Ingestion complete.")
