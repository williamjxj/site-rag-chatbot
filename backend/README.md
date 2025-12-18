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

# Activate (macOS/Linux)
source .venv/bin/activate

# Activate (Windows)
.venv\Scripts\activate

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
- **OpenAI** - Embeddings API
- **pypdf** - PDF parsing
- **beautifulsoup4** - HTML parsing

See `pyproject.toml` for complete list with versions.
