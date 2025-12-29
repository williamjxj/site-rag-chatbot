# Prompt Configuration Guide

## Overview

The RAG chatbot uses a two-part prompt system:
1. **System Prompt**: Instructions for the LLM's behavior
2. **User Prompt**: The actual question and retrieved context

## Current Prompt Structure

### System Prompt

Located in `backend/src/rag/prompt.py`, the system prompt is now configurable via the `SYSTEM_PROMPT` environment variable.

**Default System Prompt:**
```
You are a helpful website assistant.
Answer questions ONLY using the provided context from the website and documents.
If the answer is not in the context, say you don't know and suggest where the user might look.
Always include a short Sources list at the end with URLs or file paths.
```

### User Prompt

The user prompt is built by `build_prompt()` function and includes:

1. **Question**: The user's question
2. **Context Blocks**: Retrieved chunks formatted as:
   ```
   Source: {uri}
   Title: {title or 'N/A'}
   Content:
   {chunk text}
   ```

**Example User Prompt:**
```
Question: What is artificial intelligence?

Context:
Source: https://example.com/ai-intro
Title: Introduction to AI
Content:
Artificial intelligence (AI) is the simulation of human intelligence...

---
Source: https://example.com/ml-basics
Title: Machine Learning Basics
Content:
Machine learning is a subset of AI that enables systems...
```

## Customizing the System Prompt

### Method 1: Environment Variable (Recommended)

Add to your `.env` file in the `backend/` directory:

```bash
SYSTEM_PROMPT="You are an expert technical assistant specializing in software documentation. Answer questions based ONLY on the provided context. If information is not available, clearly state that and suggest relevant documentation sections. Format your answers with clear sections and always cite sources."
```

### Method 2: Direct Code Modification

Edit `backend/src/config.py` and modify the default value:

```python
system_prompt: str = os.getenv(
    "SYSTEM_PROMPT",
    "Your custom prompt here..."
)
```

## What Gets Appended to User Prompts?

The user prompt is automatically built from:

1. **User's Question**: The exact question submitted via the `/chat` endpoint
2. **Retrieved Context**: Top-k most similar chunks (default: 6) formatted as:
   - Source URI
   - Document title (if available)
   - Chunk content text

Context blocks are separated by `\n---\n` and limited by `MAX_CONTEXT_CHARS` (default: 12,000 characters).

## Troubleshooting: "I don't have any information available"

This message appears when **no chunks are retrieved** from the vector database. This typically means:

1. **No content has been ingested** - Run ingestion first:
   ```bash
   POST /ingest
   ```

2. **Check if content exists**:
   ```bash
   GET /admin/documents
   ```

3. **Verify database connection** - Ensure `DATABASE_URL` is correct in `.env`

4. **Check embedding model compatibility** - If you switched embedding models, you may need to re-ingest content

## Example Custom System Prompts

### Technical Documentation Assistant
```bash
SYSTEM_PROMPT="You are a technical documentation assistant. Provide clear, accurate answers based on the provided documentation. Use code examples when relevant. Always cite your sources with URLs."
```

### Customer Support Bot
```bash
SYSTEM_PROMPT="You are a friendly customer support assistant. Answer questions using only the provided knowledge base. Be concise and helpful. If you don't know the answer, suggest contacting support."
```

### Research Assistant
```bash
SYSTEM_PROMPT="You are a research assistant. Analyze the provided context and provide comprehensive answers. Include relevant details and always cite sources. If information is incomplete, note what's missing."
```

## Configuration Files

- **System Prompt**: `backend/src/rag/prompt.py`
- **User Prompt Builder**: `backend/src/rag/prompt.py` → `build_prompt()`
- **Settings**: `backend/src/config.py`
- **Chat Logic**: `backend/src/rag/chat.py`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SYSTEM_PROMPT` | (see default above) | Custom system prompt for the LLM |
| `TOP_K` | `6` | Number of chunks to retrieve |
| `MAX_CONTEXT_CHARS` | `12000` | Maximum characters in context |

