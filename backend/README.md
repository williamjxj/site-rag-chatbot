# Backend - Site RAG Chatbot

FastAPI backend for the RAG chatbot application.

## Dependencies

This project uses **pyproject.toml** (modern Python standard) for dependency management. For convenience, we also provide `requirements.txt` files.

### Viewing Dependencies

**Option 1: pyproject.toml** (source of truth)
```bash
cat pyproject.toml
```

**Option 2: requirements.txt** (convenience file)
```bash
cat requirements.txt
```

### Installing Dependencies

**Recommended: Install from pyproject.toml**
```bash
pip install -e .
```

**Alternative: Install from requirements.txt**
```bash
pip install -r requirements.txt
```

**For development (includes test tools)**
```bash
pip install -r requirements-dev.txt
```

## Virtual Environment

**Yes, use `.venv`** (recommended Python standard).

### Setup

```bash
# Create virtual environment
python -m venv .venv

# Activate
source .venv/bin/activate

# Install dependencies
pip install -e .
```

The `.venv/` directory is already in `.gitignore`, so it won't be committed.

## Project Structure

```
backend/
├── src/                    # Source code
│   ├── app.py             # FastAPI application
│   ├── config.py          # Configuration
│   ├── db.py              # Database models
│   ├── ingest/            # Ingestion pipeline
│   ├── rag/               # RAG components
│   └── api/               # API routes
├── tests/                 # Tests
├── scripts/               # Utility scripts
├── pyproject.toml         # Dependencies (source of truth)
├── requirements.txt       # Production dependencies (convenience)
├── requirements-dev.txt   # Development dependencies (convenience)
└── docker-compose.yml     # Database setup
```

## Key Dependencies

- **FastAPI** - Web framework
- **SQLAlchemy** - ORM
- **pgvector** - Vector database extension
- **OpenAI** - Embeddings API (optional, for paid embeddings)
- **sentence-transformers** - Free local embeddings (default for POC/testing)
- **pypdf** - PDF parsing
- **beautifulsoup4** - HTML parsing

See `pyproject.toml` for complete list with versions.

## Embedding Model Configuration

The system supports two embedding providers:

### Free Local Model (Default for POC/Testing)

No API keys required. Uses `sentence-transformers` with `all-MiniLM-L6-v2` model (384 dimensions).

**Setup:**
```bash
# In your .env file
EMBEDDING_PROVIDER=local
FREE_EMBEDDING_MODEL=all-MiniLM-L6-v2  # Optional, this is the default
```

**Or simply leave API keys unset** - the system will auto-detect and use the free model.

**First-time use:** The model (~90MB) will automatically download from Hugging Face on first embedding request.

### OpenAI API (Paid)

Requires API key. Uses `text-embedding-3-small` model (1536 dimensions).

**Setup:**
```bash
# In your .env file
EMBEDDING_PROVIDER=openai
EMBEDDING_API_KEY=sk-...
EMBEDDING_MODEL=text-embedding-3-small
```

### Switching Between Models

The system automatically detects which provider to use:
- If `EMBEDDING_PROVIDER` is set, it uses that provider
- If no provider is set and API keys are available, it uses OpenAI
- If no provider is set and no API keys, it uses the free local model

**Note:** Embeddings from different models have different dimensions (384 vs 1536). The system handles this gracefully, but for best results, re-ingest content when switching models using the `force=true` parameter in the ingestion endpoint.
