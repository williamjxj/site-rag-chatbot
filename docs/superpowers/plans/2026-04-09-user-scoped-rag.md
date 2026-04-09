# User-Scoped RAG Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Each authenticated user sees only their own ingested content in chat responses

**Architecture:** Add user_id filtering to the RAG retrieval pipeline. The chat endpoint will require authentication, extract the user_id, and pass it to retrieve() to filter chunks by user.

**Tech Stack:** FastAPI, SQLAlchemy, pgvector, JWT auth

---

### Task 1: Update retrieve() to accept user_id parameter

**Files:**
- Modify: `backend/src/rag/retriever.py:14-56`

- [ ] **Step 1: Modify retrieve function signature to accept optional user_id**

```python
def retrieve(query_embedding: list[float], top_k: int | None = None, user_id: int | None = None) -> list[Chunk]:
```

- [ ] **Step 2: Add user_id filtering to the query**

Find this section (lines 41-46):
```python
            stmt = (
                select(Chunk)
                .where(Chunk.embedding.is_not(None))
                .order_by(Chunk.embedding.cosine_distance(query_embedding))
                .limit(top_k)
            )
```

Replace with:
```python
            conditions = [Chunk.embedding.is_not(None)]
            if user_id is not None:
                conditions.append(Chunk.user_id == user_id)
            
            stmt = (
                select(Chunk)
                .where(*conditions)
                .order_by(Chunk.embedding.cosine_distance(query_embedding))
                .limit(top_k)
            )
```

- [ ] **Step 3: Run a quick test**

Run: `cd backend && python -c "from src.rag.retriever import retrieve; print('retrieve accepts user_id param:', 'user_id' in retrieve.__code__.co_varnames)"`
Expected: True

- [ ] **Step 4: Commit**

```bash
cd /Users/william.jiang/my-apps/site-rag-chatbot
git add backend/src/rag/retriever.py
git commit -m "feat: add user_id filter to retrieve function"
```

---

### Task 2: Update answer() to accept user_id parameter

**Files:**
- Modify: `backend/src/rag/chat.py:16-57`

- [ ] **Step 1: Modify answer function signature**

Find: `def answer(question: str) -> dict[str, str | list[str]]:`

Replace with:
```python
def answer(question: str, user_id: int | None = None) -> dict[str, str | list[str]]:
```

- [ ] **Step 2: Pass user_id to retrieve call**

Find (around line 57):
```python
    chunks = retrieve(q_emb, settings.top_k)
```

Replace with:
```python
    chunks = retrieve(q_emb, settings.top_k, user_id)
```

- [ ] **Step 3: Run test**

Run: `cd backend && python -c "from src.rag.chat import answer; print('answer accepts user_id param:', 'user_id' in answer.__code__.co_varnames)"`
Expected: True

- [ ] **Step 4: Commit**

```bash
git add backend/src/rag/chat.py
git commit -m "feat: pass user_id to retrieve in answer function"
```

---

### Task 3: Update chat endpoint to require auth and pass user_id

**Files:**
- Modify: `backend/src/api/routes/chat.py`

- [ ] **Step 1: Import auth dependency**

Find (line 3-7):
```python
from fastapi import APIRouter, HTTPException, status

from ...config import validate_api_keys
from ...rag.chat import answer
from ..models import ChatRequest, ChatResponse
```

Replace with:
```python
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ...auth import decode_token
from ...config import validate_api_keys
from ...rag.chat import answer
from ..models import ChatRequest, ChatResponse
from ...db import SessionLocal
from sqlalchemy.orm import Session

router = APIRouter(prefix="/chat", tags=["Chat"])
security = HTTPBearer()


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)
) -> int | None:
    """Extract user_id from JWT token."""
    token = credentials.credentials
    payload = decode_token(token)
    if payload is None:
        return None
    user_id = payload.get("sub")
    return int(user_id) if user_id else None
```

- [ ] **Step 2: Add user_id to chat endpoint**

Find the endpoint function (line 12-13):
```python
async def chat_endpoint(request: ChatRequest) -> ChatResponse:
```

Replace with:
```python
async def chat_endpoint(request: ChatRequest, user_id: int | None = Depends(get_current_user_id)) -> ChatResponse:
```

- [ ] **Step 3: Pass user_id to answer()**

Find (line 62):
```python
        result = answer(request.question)
```

Replace with:
```python
        result = answer(request.question, user_id)
```

- [ ] **Step 4: Commit**

```bash
git add backend/src/api/routes/chat.py
git commit -m "feat: require auth for chat endpoint, pass user_id to RAG"
```

---

### Task 4: Test end-to-end flow

**Files:**
- Test: Manual curl testing

- [ ] **Step 1: Start backend**

Run: `cd backend && /Users/william.jiang/my-apps/site-rag-chatbot/.venv/bin/python -m uvicorn src.app:app --reload --port 8000 &`
Background it and wait 3 seconds

- [ ] **Step 2: Register and login to get token**

```bash
# Register a new user
curl -s -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user1@test.com","username":"user1","password":"password123"}'

# Login to get token
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"user1","password":"password123"}' | jq -r '.access_token')
echo "Token: $TOKEN"
```

- [ ] **Step 3: Test chat with auth**

```bash
# Test chat with auth (should work)
curl -s -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"question":"What is this about?"}'
```

- [ ] **Step 4: Test chat without auth (should fail)**

```bash
# Test chat without auth (should fail with 403)
curl -s -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question":"What is this about?"}'
```

- [ ] **Step 5: Commit test results**

```bash
git commit --allow-empty -m "test: verified user-scoped RAG works"
```

---

### Task 5: Update frontend API client to send auth header

**Files:**
- Modify: `frontend/lib/api/chat.ts`

- [ ] **Step 1: Check current chat API client**

Run: `cat frontend/lib/api/chat.ts`

- [ ] **Step 2: Add auth header to chat request**

Find the chat function (should have fetch call). Add authorization header similar to how auth.ts does it.

- [ ] **Step 3: Commit**

```bash
git add frontend/lib/api/chat.ts
git commit -m "feat: send auth token with chat requests"
```

---

## Execution

**Plan complete and saved. Two execution options:**

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

**Which approach?**