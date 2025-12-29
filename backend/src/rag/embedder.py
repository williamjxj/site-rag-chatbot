"""Vector embedding generation using OpenAI API or free local models."""

import logging
from typing import TYPE_CHECKING

from ..config import settings

logger = logging.getLogger(__name__)

# Lazy import for sentence-transformers (only loaded if free model is used)
if TYPE_CHECKING:
    from sentence_transformers import SentenceTransformer

# Global model instance for lazy singleton pattern
_free_model: "SentenceTransformer | None" = None

# For embeddings, use OpenAI API if API keys are available, otherwise use free model
embedding_api_key = settings.embedding_api_key or settings.openai_api_key
embedding_base_url = None  # Always use default OpenAI API for embeddings

# Determine embedding provider
def _get_embedding_provider() -> str:
    """
    Determine which embedding provider to use.
    
    Returns:
        "openai" if API keys are available and provider is set to openai
        "local" if no API keys or provider is explicitly set to local
    """
    # Explicit provider setting takes precedence
    if settings.embedding_provider:
        return settings.embedding_provider.lower()
    
    # Auto-detect: use local if no API keys available
    if not embedding_api_key:
        return "local"
    
    # Default to openai if API key is available
    return "openai"


def _get_free_model() -> "SentenceTransformer":
    """
    Get or initialize the free embedding model (lazy singleton pattern).
    
    Returns:
        SentenceTransformer instance
        
    Raises:
        ImportError: If sentence-transformers is not installed
        Exception: If model fails to load or download
    """
    global _free_model
    
    if _free_model is None:
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as e:
            raise ImportError(
                "sentence-transformers is required for free embedding model. "
                "Install it with: pip install sentence-transformers>=2.2.0"
            ) from e
        
        model_name = settings.free_embedding_model
        logger.info(f"Loading free embedding model: {model_name}")
        
        try:
            _free_model = SentenceTransformer(model_name)
            logger.info(f"Successfully loaded free embedding model: {model_name}")
        except Exception as e:
            error_msg = (
                f"Failed to load free embedding model '{model_name}'. "
                f"Ensure you have internet connectivity for first-time download. "
                f"Error: {str(e)}"
            )
            logger.error(error_msg)
            raise RuntimeError(error_msg) from e
    
    return _free_model


def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Generate embeddings for a list of texts using OpenAI API or free local model.
    
    Provider selection:
    - Uses OpenAI API if EMBEDDING_PROVIDER=openai and API keys are available
    - Uses free local model if EMBEDDING_PROVIDER=local or no API keys are available
    - Auto-detects based on API key availability if provider not explicitly set
    
    Uses 30-second timeout for API calls to prevent hanging requests.
    
    Args:
        texts: List of text strings to embed. Empty list returns empty list.
    
    Returns:
        List of embedding vectors, where each vector is a list of floats.
        Dimensions: 1536 for OpenAI text-embedding-3-small, 384 for all-MiniLM-L6-v2.
        The order matches the input texts.
    
    Raises:
        ValueError: If OpenAI API key is required but not available, or if model fails to initialize
        RuntimeError: If free model fails to load
        Exception: If the embedding API call fails (timeout, network error, etc.).
                   Errors should be caught and handled by the caller with user-friendly messages.
    """
    if not texts:
        return []
    
    provider = _get_embedding_provider()
    
    if provider == "openai":
        return _embed_with_openai(texts)
    else:
        return _embed_with_free_model(texts)


def _embed_with_openai(texts: list[str]) -> list[list[float]]:
    """
    Generate embeddings using OpenAI API.
    
    Args:
        texts: List of text strings to embed.
    
    Returns:
        List of embedding vectors (1536 dimensions).
    
    Raises:
        ValueError: If API key is not available
        Exception: If API call fails
    """
    import time
    
    # Validate that we have an API key (check before importing OpenAI)
    if not embedding_api_key:
        raise ValueError(
            "EMBEDDING_API_KEY or OPENAI_API_KEY must be set to use OpenAI embeddings. "
            "Alternatively, set EMBEDDING_PROVIDER=local to use free local model. "
            "Get your OpenAI API key from https://platform.openai.com/account/api-keys"
        )
    
    from openai import OpenAI
    
    client = OpenAI(
        api_key=embedding_api_key,
        base_url=embedding_base_url,  # None means use default OpenAI API
    )
    
    num_texts = len(texts)
    start_time = time.time()
    
    try:
        response = client.embeddings.create(
            model=settings.embedding_model,
            input=texts,
            timeout=30.0,
        )
        result = [item.embedding for item in response.data]
        
        # Performance logging
        elapsed_time = time.time() - start_time
        texts_per_sec = num_texts / elapsed_time if elapsed_time > 0 else 0
        logger.info(
            f"Generated {num_texts} embeddings via OpenAI API in {elapsed_time:.2f}s "
            f"({texts_per_sec:.1f} texts/sec, dimension: {len(result[0]) if result else 0})"
        )
        
        return result
    except Exception as e:
        # Provide helpful error message for authentication errors
        error_str = str(e)
        if "401" in error_str or "invalid_api_key" in error_str or "Incorrect API key" in error_str:
            raise ValueError(
                "Invalid OpenAI API key for embeddings. "
                "Please set EMBEDDING_API_KEY in your .env file with a valid OpenAI API key, "
                "or set EMBEDDING_PROVIDER=local to use free local model. "
                "Get your OpenAI API key from https://platform.openai.com/account/api-keys"
            ) from e
        raise


def _embed_with_free_model(texts: list[str]) -> list[list[float]]:
    """
    Generate embeddings using free local model (sentence-transformers).
    
    Args:
        texts: List of text strings to embed.
    
    Returns:
        List of embedding vectors (384 dimensions for all-MiniLM-L6-v2).
    
    Raises:
        RuntimeError: If model fails to load or initialize
        ImportError: If sentence-transformers is not installed
    """
    import time
    
    try:
        model = _get_free_model()
        num_texts = len(texts)
        logger.debug(f"Generating embeddings for {num_texts} texts using free model")
        
        # Performance monitoring
        start_time = time.time()
        
        # Memory monitoring (approximate)
        try:
            import psutil
            process = psutil.Process()
            mem_before = process.memory_info().rss / 1024 / 1024  # MB
        except ImportError:
            mem_before = None
            psutil = None
        
        # Batch processing optimization: sentence-transformers handles batching internally,
        # but we can optimize for very large batches by processing in chunks if needed
        # Default batch size in sentence-transformers is typically 32, which works well
        # For extremely large batches (>1000), we could add explicit chunking here if needed
        embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=False, batch_size=32)
        
        # Convert to list of lists
        result = embeddings.tolist()
        
        # Performance logging
        elapsed_time = time.time() - start_time
        texts_per_sec = num_texts / elapsed_time if elapsed_time > 0 else 0
        
        logger.info(
            f"Generated {num_texts} embeddings in {elapsed_time:.2f}s "
            f"({texts_per_sec:.1f} texts/sec, dimension: {len(result[0]) if result else 0})"
        )
        
        # Memory usage logging
        if psutil:
            try:
                mem_after = process.memory_info().rss / 1024 / 1024  # MB
                mem_delta = mem_after - mem_before
                logger.debug(f"Memory usage: {mem_before:.1f}MB → {mem_after:.1f}MB (Δ{mem_delta:+.1f}MB)")
            except Exception:
                pass  # Memory monitoring is optional
        
        logger.debug(f"Generated {len(result)} embeddings with dimension {len(result[0]) if result else 0}")
        return result
        
    except ImportError as e:
        raise ImportError(
            "sentence-transformers is required for free embedding model. "
            "Install it with: pip install sentence-transformers>=2.2.0"
        ) from e
    except Exception as e:
        error_msg = (
            f"Failed to generate embeddings with free model '{settings.free_embedding_model}'. "
            f"Error: {str(e)}. "
            f"Ensure the model is properly downloaded and you have sufficient memory."
        )
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e
