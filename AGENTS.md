# Repository Agent Guidelines

## Project Overview

Site RAG Chatbot - a monorepo with FastAPI backend and Next.js frontend. Multi-tenant document ingestion + RAG chat with source citations.

## Working Directories

- **Backend**: `cd backend` - Python 3.10+, FastAPI, SQLAlchemy, pgvector
- **Frontend**: `cd frontend` - Next.js 14, React, TypeScript, Tailwind v4, shadcn/ui

## Dev Commands

```bash
# Frontend (pnpm)
pnpm dev          # Next.js dev server at http://localhost:3000
pnpm build        # Production build
pnpm lint         # ESLint
pnpm test         # Jest unit tests
pnpm test:e2e     # Playwright e2e (requires dev server)
pnpm snapshots   # Generate Playwright UI snapshots

# Backend
uvicorn src.app:app --reload --port 8000  # Dev server at http://localhost:8000
pytest backend/tests                       # Run tests
```

## Database

- PostgreSQL 16 + pgvector via Docker: `cd backend && docker compose up -d`
- Initialize: `python -c "from src.db import init_db; init_db()"`

## Environment Files

- Backend: `backend/.env` (API keys, DB URL, sitemap URL)
- Frontend: `frontend/.env.local` (API base URL)

## Key Conventions

- **Frontend**: PascalCase components, camelCase utils, Tailwind + shadcn/ui
- **Backend**: snake_case modules, Black + Ruff, Pydantic settings
- **Auth**: JWT-based, user isolated via `current_user.id` in endpoints
- **Multi-tenant**: All admin/chat endpoints filter by authenticated user

## LLM & Embedding Providers

- Chat: `ACTIVE_LLM` env (deepseek, kimi, minimax)
- Embeddings: `EMBEDDING_PROVIDER` (openai or local sentence-transformers)
- Switching embedding providers may require re-ingestion (dimension mismatch)

## Testing Notes

- Backend tests: `backend/tests/unit/`, `backend/tests/integration/`
- Frontend tests: Jest in `tests/`, Playwright e2e in `tests/e2e/`
- Demo user: `tester` / `William1!` (for screenshots/tests)

## Common Issues

- `psycopg.OperationalError`: Docker DB not running → `docker compose restart`
- No answers: Verify content ingested, check backend logs for embedding/retrieval errors