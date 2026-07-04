# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Full-stack RAG (Retrieval-Augmented Generation) chatbot. Users ingest websites/documents, then ask questions answered via vector search + LLM. Multi-tenant: each user's embeddings are isolated by `user_id`.

## Development Commands

### Backend (run from `backend/`)

```bash
# Start PostgreSQL + pgvector
docker compose up -d

# Install dependencies
pip install -e .

# Initialize database (first run)
python -c "from src.db import init_db; init_db()"

# Run dev server
uvicorn src.app:app --reload --port 8000
# or
./scripts/start-server.sh

# Tests and linting
pytest
ruff check .
black .
mypy src/
```

### Frontend (run from `frontend/`)

```bash
pnpm dev          # Dev server on :3000
pnpm build        # Production build
pnpm lint         # ESLint
pnpm test         # Jest unit tests
pnpm test:watch   # Jest watch mode
pnpm test:e2e     # Playwright e2e tests
pnpm snapshots    # Regenerate screenshot fixtures
```

## Environment Setup

**Backend** — create `backend/.env`:
```
DATABASE_URL=postgresql+psycopg://rag:rag@localhost:5432/rag
ACTIVE_LLM=minimax            # deepseek | kimi | minimax
DEEPSEEK_API_KEY=...
KIMI_API_KEY=...
MINIMAX_API_KEY=...
EMBEDDING_PROVIDER=local      # local (free) | openai (paid)
EMBEDDING_API_KEY=...         # only needed when EMBEDDING_PROVIDER=openai
JWT_SECRET_KEY=...
SITEMAP_URL=...               # URL to crawl on ingest
DOCS_DIR=../resources         # local docs path
```

**Frontend** — create `frontend/.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Architecture

### Backend (`backend/src/`)

- **`app.py`** — FastAPI entry point; mounts routers, global exception handlers
- **`config.py`** — `Settings` class (pydantic-settings); single source of truth for all env vars
- **`db.py`** — SQLAlchemy 2.0 models (`User`, `Chunk`), pgvector column, `init_db()`
- **`auth.py`** — JWT creation/verification, `get_current_user()` FastAPI dependency
- **`api/routes/`** — Route handlers: `chat.py`, `ingest.py`, `admin.py`, `auth.py`
- **`ingest/`** — Document ingestion pipeline: fetches URLs/files, chunks text, embeds, stores
- **`rag/`** — `embedder.py` (OpenAI or local sentence-transformers), `retriever.py` (pgvector similarity search), `chat.py` (calls active LLM with retrieved context)

**Key data flow**: `POST /chat` → `retriever.py` finds top-k chunks by cosine similarity → chunks injected as context → LLM API call → streamed response.

**LLM switching**: controlled by `ACTIVE_LLM` env var; each provider has its own client in `rag/chat.py`.

### Frontend (`frontend/`)

- **`app/`** — Next.js 14 App Router pages: `/` (chat), `/admin` (document management), `/auth/signin|signup`, `/profile`
- **`components/chat/`** — Chat UI; streams responses from backend SSE
- **`components/admin/`** — Document upload, ingest trigger, document list/delete
- **`lib/api/`** — Typed API clients (`auth.ts`, `chat.ts`, `ingest.ts`, `admin.ts`); all attach JWT from `localStorage` in `Authorization: Bearer` header
- **`lib/utils/`** — Shared types and utilities

**Auth flow**: Login → JWT stored in `localStorage` → injected into every API call → backend validates via `get_current_user()` dependency.

### Database Schema

- **`users`**: `id`, `email`, `hashed_password`, `created_at`
- **`chunks`**: `id`, `user_id` (FK), `content`, `embedding` (vector(1536)), `uri`, `title`, `metadata`

All vector queries filter by `user_id` to enforce tenant isolation.
