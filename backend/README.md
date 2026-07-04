
# Backend - Site RAG Chatbot

Site RAG Chatbot is a modern Retrieval-Augmented Generation (RAG) platform that lets users upload, manage, and chat with their own documents and website content. It combines semantic search, multi-LLM support, and a professional web UI to deliver accurate, source-cited answers from your private knowledge base.

## Top 5 Features

1. **Semantic Chat with Source Citations:**
	Users can ask questions and receive answers grounded in their uploaded documents, with every answer citing its sources.

2. **Multi-Format Content Ingestion:**
	Supports uploading and processing PDFs, Markdown, TXT files, and crawling static websites via sitemap.

3. **Multi-LLM and Embedding Provider Support:**
	Easily switch between OpenAI, DeepSeek, Kimi, MiniMax, or local sentence-transformers for both chat and embeddings.

4. **Multi-Tenant Isolation:**
	Each user’s documents and chat history are securely isolated, supporting per-user knowledge bases.

5. **Admin & Professional UI:**
	Includes a branded admin interface for document management, embedding provider selection, and system status, plus a polished chat UI with markdown rendering.

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

**Yes, use `venv`** (recommended Python standard).

### Setup

```bash
# Create virtual environment
python -m venv venv

# Activate
source venv/bin/activate

# Install dependencies
pip install -e .
```

The `venv/` directory is already in `.gitignore`, so it won't be committed.

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


## How to Start the Service

To start the backend server (FastAPI + Uvicorn):

1. **Activate your virtual environment:**
	```bash
	cd backend
	source venv/bin/activate
	```

2. **Start the server:**
	```bash
	uvicorn src.app:app --reload --port 8000
	```

Or use the provided script:
	```bash
	./scripts/start-server.sh
	```

The backend will be available at http://localhost:8000

---

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
