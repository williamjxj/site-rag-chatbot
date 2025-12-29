"""Chat response generation using RAG and Deepseek API."""

import logging
import requests
from requests.exceptions import Timeout, RequestException

from ..config import settings
from .embedder import embed_texts
from .retriever import retrieve
from .prompt import SYSTEM_PROMPT, build_prompt

logger = logging.getLogger(__name__)


def answer(question: str) -> dict[str, str | list[str]]:
    """
    Generate answer to user question using RAG.

    Implements the complete RAG pipeline:
    1. Embeds the question using the configured embedding model
    2. Retrieves top-k most similar chunks from vector database
    3. Builds context from retrieved chunks (respecting max_context_chars limit)
    4. Generates answer using chat LLM with retrieved context
    5. Returns answer with deduplicated source citations

    Error handling:
    - Embedding failures: Returns user-friendly error message
    - Retrieval failures: Returns user-friendly error message
    - LLM API failures: Handles rate limits, timeouts, network errors, and malformed responses
    - All errors are logged for debugging

    Args:
        question: User's question (must be non-empty and <= 1000 characters)

    Returns:
        Dictionary with 'answer' (str) and 'sources' (list[str]) keys.
        Sources are deduplicated URIs of documents used in the answer.

    Raises:
        ValueError: If embedding generation fails, retrieval fails, or LLM API call fails.
                    Error messages are user-friendly and actionable.
    """
    # Embed the question with error handling
    logger.info("Starting RAG pipeline: embedding question")
    try:
        q_emb = embed_texts([question])[0]
        logger.info(f"Question embedded successfully (dimension: {len(q_emb)})")
    except Exception as e:
        logger.error(f"Error generating embedding: {e}")
        raise ValueError(
            f"Failed to generate embedding for your question: {str(e)}. Please try again."
        )

    # Retrieve relevant chunks
    logger.info(f"Retrieving top-{settings.top_k} chunks from vector database")
    chunks = retrieve(q_emb, settings.top_k)
    logger.info(f"Retrieved {len(chunks)} chunks")

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
        # Format: Source URI, Title (if available), and Content
        block = f"Source: {chunk.uri}\nTitle: {chunk.title or 'N/A'}\nContent:\n{chunk.text}\n"
        if total_chars + len(block) > settings.max_context_chars:
            break
        context_blocks.append(block)
        sources.append(chunk.uri)
        total_chars += len(block)

    # Build prompt
    logger.info(f"Building prompt with {len(context_blocks)} context blocks ({total_chars} chars)")
    user_prompt = build_prompt(question, context_blocks)

    # Use DeepSeek API key, fallback to OpenAI API key if not set
    logger.info("Calling chat LLM API to generate answer")
    api_key = settings.deepseek_api_key or settings.openai_api_key
    if not api_key:
        raise ValueError("Either DEEPSEEK_API_KEY or OPENAI_API_KEY must be set")

    # Determine API endpoint from configuration
    base_url = settings.openai_base_url or "https://api.openai.com/v1"
    api_url = f"{base_url}/chat/completions"

    # Call chat LLM API with error handling
    try:
        response = requests.post(
            api_url,
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

        # Handle rate limit errors (429)
        if response.status_code == 429:
            logger.warning("Rate limit exceeded for chat LLM API")
            raise ValueError(
                "API rate limit exceeded. Please try again later."
            )

        # Handle other HTTP errors
        response.raise_for_status()
        result = response.json()

        # Validate response structure
        if not result.get("choices") or len(result["choices"]) == 0:
            logger.error("Empty or invalid response from chat LLM API")
            raise ValueError(
                "Received an invalid response from the chat service. Please try again."
            )

        answer_text = result["choices"][0]["message"].get("content")
        if not answer_text:
            logger.error("Empty content in chat LLM response")
            raise ValueError(
                "Received an empty response from the chat service. Please try again."
            )

    except Timeout:
        logger.error("Timeout calling chat LLM API")
        raise ValueError(
            "Request timed out while calling the chat service. Please try again."
        )
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error calling chat LLM API: {e}")
        if e.response and e.response.status_code == 429:
            raise ValueError(
                "API rate limit exceeded. Please try again later."
            )
        raise ValueError(
            f"Error calling chat service: {str(e)}. Please try again."
        )
    except RequestException as e:
        logger.error(f"Network error calling chat LLM API: {e}")
        raise ValueError(
            "Network error while calling the chat service. Please check your connection and try again."
        )
    except (KeyError, IndexError, TypeError) as e:
        logger.error(f"Malformed response from chat LLM API: {e}")
        raise ValueError(
            "Received a malformed response from the chat service. Please try again."
        )

    # Deduplicate sources
    unique_sources = list(dict.fromkeys(sources))
    logger.info(f"RAG pipeline completed successfully. Answer generated with {len(unique_sources)} unique sources")

    return {
        "answer": answer_text,
        "sources": unique_sources,
    }
