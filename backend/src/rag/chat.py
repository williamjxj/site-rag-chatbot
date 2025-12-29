"""Chat response generation using RAG and Deepseek API."""

import requests

from ..config import settings
from .embedder import embed_texts
from .retriever import retrieve
from .prompt import SYSTEM_PROMPT, build_prompt


def answer(question: str) -> dict[str, str | list[str]]:
    """
    Generate answer to user question using RAG.

    Args:
        question: User's question

    Returns:
        Dictionary with 'answer' and 'sources' keys
    """
    # Embed the question
    q_emb = embed_texts([question])[0]

    # Retrieve relevant chunks
    chunks = retrieve(q_emb, settings.top_k)

    if not chunks:
        return {
            "answer": "I don't have any information available to answer your question. Please ensure content has been ingested.",
            "sources": [],
        }

    # Build context from chunks
    context_blocks = []
    sources = []
    total_chars = 0

    for chunk in chunks:
        block = f"Source: {chunk.uri}\nTitle: {chunk.title or ''}\nContent:\n{chunk.text}\n"
        if total_chars + len(block) > settings.max_context_chars:
            break
        context_blocks.append(block)
        sources.append(chunk.uri)
        total_chars += len(block)

    # Build prompt
    user_prompt = build_prompt(question, context_blocks)

    # Use DeepSeek API key, fallback to OpenAI API key if not set
    api_key = settings.deepseek_api_key or settings.openai_api_key
    if not api_key:
        raise ValueError("Either DEEPSEEK_API_KEY or OPENAI_API_KEY must be set")

    # Call Deepseek API
    response = requests.post(
        "https://api.deepseek.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": settings.chat_model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.2,
        },
        timeout=30,
    )

    response.raise_for_status()
    result = response.json()

    answer_text = result["choices"][0]["message"]["content"]

    # Deduplicate sources
    unique_sources = list(dict.fromkeys(sources))

    return {
        "answer": answer_text,
        "sources": unique_sources,
    }
