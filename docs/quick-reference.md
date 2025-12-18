# Quick Reference: Site RAG Chatbot

## Quick Commands

### Setup

```bash
# Start database
cd backend && docker compose up -d

# Create virtual environment (use .venv)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
# Option 1: From pyproject.toml (recommended)
pip install -e .

# Option 2: From requirements.txt
pip install -r requirements.txt

# For development (includes test tools)
pip install -r requirements-dev.txt

# Initialize database
python -c "from src.db import init_db; init_db()"

# Frontend
cd ../frontend
npm install
```

### Running

```bash
# Backend (Terminal 1)
cd backend
uvicorn src.app:app --reload --port 8000

# Frontend (Terminal 2)
cd frontend
npm run dev
```

### Ingestion

```bash
# Via script
cd backend
python scripts/ingest_once.py

# Via API
curl -X POST http://localhost:8000/ingest
```

## API Quick Reference

### Chat

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question":"What services do you offer?"}'
```

### Ingestion

```bash
# Ingest all
curl -X POST http://localhost:8000/ingest

# Ingest website only
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"source":"web"}'
```

### Admin

```bash
# List documents
curl http://localhost:8000/admin/documents

# List with filter
curl "http://localhost:8000/admin/documents?source=web&limit=10"

# Delete document
curl -X DELETE http://localhost:8000/admin/documents/URL_OR_PATH
```

## Environment Variables

### Backend (.env)

```bash
DATABASE_URL=postgresql+psycopg://rag:rag@localhost:5432/rag
SITEMAP_URL=https://example.com/sitemap.xml
DOCS_DIR=./docs
OPENAI_API_KEY=your_key
DEEPSEEK_API_KEY=your_key
EMBEDDING_MODEL=text-embedding-3-small
CHAT_MODEL=deepseek-chat
TOP_K=6
MAX_CONTEXT_CHARS=12000
```

### Frontend (.env.local)

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## File Formats Supported

- **Web**: HTML pages via sitemap.xml
- **Documents**: `.md`, `.mdx`, `.txt`, `.pdf`

## Key URLs

- **Chat Interface**: http://localhost:3000
- **Admin Interface**: http://localhost:3000/admin
- **API Docs**: http://localhost:8000/docs (FastAPI auto-generated)
- **Health Check**: http://localhost:8000/health

## Common Issues

| Issue | Solution |
|-------|----------|
| Database connection refused | `docker compose up -d` in backend/ |
| No answers returned | Check if content ingested via `/admin/documents` |
| Embedding errors | Verify `OPENAI_API_KEY` in `.env` |
| Chat errors | Verify `DEEPSEEK_API_KEY` in `.env` |
| Frontend can't connect | Check `NEXT_PUBLIC_API_URL` in `.env.local` |

## Project Structure Quick View

```
backend/src/
├── app.py              # FastAPI app
├── config.py           # Settings
├── db.py               # Database
├── ingest/             # Ingestion
└── rag/                # RAG pipeline

frontend/
├── app/                # Pages
├── components/         # React components
└── lib/                # Utilities
```

## Testing Checklist

- [ ] Database running (`docker compose ps`)
- [ ] Backend running (`curl http://localhost:8000/health`)
- [ ] Frontend running (http://localhost:3000 loads)
- [ ] Content ingested (`curl http://localhost:8000/admin/documents`)
- [ ] Chat works (ask a question)
- [ ] Admin works (view/delete documents)
