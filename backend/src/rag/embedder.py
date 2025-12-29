"""Vector embedding generation using OpenAI API."""

from openai import OpenAI

from ..config import settings

# For embeddings, always use OpenAI API (DeepSeek doesn't support embeddings)
# Use embedding_api_key if set, otherwise fall back to openai_api_key
# Never use DeepSeek base_url for embeddings
embedding_api_key = settings.embedding_api_key or settings.openai_api_key
embedding_base_url = None  # Always use default OpenAI API for embeddings

client = OpenAI(
    api_key=embedding_api_key,
    base_url=embedding_base_url,  # None means use default OpenAI API (https://api.openai.com/v1)
)


def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Generate embeddings for a list of texts using OpenAI API.

    Note: DeepSeek does not support embeddings. You must use an OpenAI API key.
    Set EMBEDDING_API_KEY in your .env file with a valid OpenAI API key.

    Uses 30-second timeout for API calls to prevent hanging requests.

    Args:
        texts: List of text strings to embed. Empty list returns empty list.

    Returns:
        List of embedding vectors, where each vector is a list of 1536 floats
        (for text-embedding-3-small model). The order matches the input texts.

    Raises:
        Exception: If the embedding API call fails (timeout, network error, etc.).
                   Errors should be caught and handled by the caller with user-friendly messages.
    """
    if not texts:
        return []

    # Validate that we have an API key
    if not embedding_api_key:
        raise ValueError(
            "EMBEDDING_API_KEY or OPENAI_API_KEY must be set with a valid OpenAI API key. "
            "DeepSeek API keys do not work for embeddings. "
            "Get your OpenAI API key from https://platform.openai.com/account/api-keys"
        )

    try:
        response = client.embeddings.create(
            model=settings.embedding_model,
            input=texts,
            timeout=30.0,
        )
        return [item.embedding for item in response.data]
    except Exception as e:
        # Provide helpful error message for authentication errors
        error_str = str(e)
        if "401" in error_str or "invalid_api_key" in error_str or "Incorrect API key" in error_str:
            raise ValueError(
                "Invalid OpenAI API key for embeddings. "
                "Please set EMBEDDING_API_KEY in your .env file with a valid OpenAI API key. "
                "DeepSeek API keys cannot be used for embeddings. "
                "Get your OpenAI API key from https://platform.openai.com/account/api-keys"
            ) from e
        raise
