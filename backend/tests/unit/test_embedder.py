"""Unit tests for embedding generation."""

import os
import sys
from unittest.mock import MagicMock, patch

import pytest

from src.rag import embedder


def setup_module():
    """Reset global state before tests."""
    embedder._free_model = None


def teardown_module():
    """Clean up after tests."""
    embedder._free_model = None


def test_embed_texts_empty_list():
    """Test that empty list returns empty list."""
    result = embedder.embed_texts([])
    assert result == []


@patch("src.rag.embedder._get_embedding_provider")
@patch("src.rag.embedder._embed_with_free_model")
def test_embed_texts_uses_free_model_when_provider_is_local(mock_free, mock_provider):
    """Test that free model is used when provider is local."""
    mock_provider.return_value = "local"
    mock_free.return_value = [[0.1, 0.2, 0.3] * 128]  # 384 dims
    
    result = embedder.embed_texts(["test text"])
    
    assert result == [[0.1, 0.2, 0.3] * 128]
    mock_free.assert_called_once_with(["test text"])


@patch("src.rag.embedder._get_embedding_provider")
@patch("src.rag.embedder._embed_with_openai")
def test_embed_texts_uses_openai_when_provider_is_openai(mock_openai, mock_provider):
    """Test that OpenAI is used when provider is openai."""
    mock_provider.return_value = "openai"
    mock_openai.return_value = [[0.1, 0.2, 0.3] * 512]  # 1536 dims
    
    result = embedder.embed_texts(["test text"])
    
    assert result == [[0.1, 0.2, 0.3] * 512]
    mock_openai.assert_called_once_with(["test text"])


@patch.dict(os.environ, {"EMBEDDING_PROVIDER": "local"}, clear=False)
@patch("src.rag.embedder.settings")
def test_get_embedding_provider_explicit_local(mock_settings):
    """Test provider detection with explicit local setting."""
    mock_settings.embedding_provider = "local"
    mock_settings.embedding_api_key = ""
    mock_settings.openai_api_key = ""
    
    provider = embedder._get_embedding_provider()
    assert provider == "local"


@patch.dict(os.environ, {"EMBEDDING_PROVIDER": "openai"}, clear=False)
@patch("src.rag.embedder.settings")
def test_get_embedding_provider_explicit_openai(mock_settings):
    """Test provider detection with explicit openai setting."""
    mock_settings.embedding_provider = "openai"
    mock_settings.embedding_api_key = "sk-test"
    
    provider = embedder._get_embedding_provider()
    assert provider == "openai"


@patch("src.rag.embedder.settings")
@patch("src.rag.embedder.embedding_api_key", "")
def test_get_embedding_provider_auto_detect_no_api_key(mock_settings):
    """Test provider auto-detection falls back to local when no API key."""
    mock_settings.embedding_provider = ""
    
    provider = embedder._get_embedding_provider()
    assert provider == "local"


@patch("src.rag.embedder.settings")
@patch("src.rag.embedder.embedding_api_key", "sk-test")
def test_get_embedding_provider_auto_detect_with_api_key(mock_settings):
    """Test provider auto-detection uses openai when API key available."""
    mock_settings.embedding_provider = ""
    
    provider = embedder._get_embedding_provider()
    assert provider == "openai"


@patch("src.rag.embedder.settings")
def test_get_free_model_lazy_initialization(mock_settings):
    """Test that free model is initialized lazily on first access."""
    mock_settings.free_embedding_model = "all-MiniLM-L6-v2"
    
    # Reset global state
    embedder._free_model = None
    
    # Mock the import and class
    with patch("builtins.__import__") as mock_import:
        # Make the import return a mock module with SentenceTransformer
        mock_st_module = MagicMock()
        mock_model_instance = MagicMock()
        mock_st_module.SentenceTransformer = MagicMock(return_value=mock_model_instance)
        mock_import.return_value = mock_st_module
        
        # First call should initialize
        model1 = embedder._get_free_model()
        assert model1 == mock_model_instance
        
        # Second call should return same instance (singleton)
        model2 = embedder._get_free_model()
        assert model2 == model1
    
    # Clean up
    embedder._free_model = None


@patch("src.rag.embedder.settings")
def test_get_free_model_import_error(mock_settings):
    """Test that ImportError is raised when sentence-transformers is not installed."""
    mock_settings.free_embedding_model = "all-MiniLM-L6-v2"
    embedder._free_model = None
    
    with patch("builtins.__import__", side_effect=ImportError("No module named 'sentence_transformers'")):
        with pytest.raises(ImportError) as exc_info:
            embedder._get_free_model()
        
        assert "sentence-transformers is required" in str(exc_info.value)
        assert "pip install sentence-transformers" in str(exc_info.value)
    
    embedder._free_model = None


@patch("src.rag.embedder.settings")
def test_get_free_model_load_error(mock_settings):
    """Test that RuntimeError is raised when model fails to load."""
    mock_settings.free_embedding_model = "invalid-model"
    embedder._free_model = None
    
    # Mock the import and make SentenceTransformer raise an error
    with patch("builtins.__import__") as mock_import:
        mock_st_module = MagicMock()
        mock_st_module.SentenceTransformer = MagicMock(side_effect=Exception("Model not found"))
        mock_import.return_value = mock_st_module
        
        with pytest.raises(RuntimeError) as exc_info:
            embedder._get_free_model()
        
        assert "Failed to load free embedding model" in str(exc_info.value)
    
    embedder._free_model = None


@patch("src.rag.embedder._get_free_model")
@patch("src.rag.embedder.logger")
def test_embed_with_free_model_success(mock_logger, mock_get_model):
    """Test successful embedding generation with free model."""
    mock_model = MagicMock()
    # Simulate 384-dimensional embeddings (all-MiniLM-L6-v2)
    import numpy as np
    mock_embeddings = np.array([[0.1] * 384, [0.2] * 384])
    mock_model.encode.return_value = mock_embeddings
    mock_get_model.return_value = mock_model
    
    result = embedder._embed_with_free_model(["text1", "text2"])
    
    assert len(result) == 2
    assert len(result[0]) == 384
    assert len(result[1]) == 384
    mock_model.encode.assert_called_once_with(
        ["text1", "text2"],
        convert_to_numpy=True,
        show_progress_bar=False,
        batch_size=32,
    )


@patch("src.rag.embedder._get_free_model")
@patch("src.rag.embedder.logger")
def test_embed_with_free_model_dimension_validation(mock_logger, mock_get_model):
    """Test that free model produces 384-dimensional embeddings."""
    mock_model = MagicMock()
    import numpy as np
    # all-MiniLM-L6-v2 produces 384 dimensions
    mock_embeddings = np.array([[0.1] * 384])
    mock_model.encode.return_value = mock_embeddings
    mock_get_model.return_value = mock_model
    
    result = embedder._embed_with_free_model(["test"])
    
    assert len(result) == 1
    assert len(result[0]) == 384


@patch("src.rag.embedder._get_free_model")
def test_embed_with_free_model_import_error(mock_get_model):
    """Test error handling when sentence-transformers import fails."""
    mock_get_model.side_effect = ImportError("No module named 'sentence_transformers'")
    
    with pytest.raises(ImportError) as exc_info:
        embedder._embed_with_free_model(["test"])
    
    assert "sentence-transformers is required" in str(exc_info.value)


@patch("src.rag.embedder._get_free_model")
@patch("src.rag.embedder.logger")
def test_embed_with_free_model_runtime_error(mock_logger, mock_get_model):
    """Test error handling when model encoding fails."""
    mock_model = MagicMock()
    mock_model.encode.side_effect = Exception("Encoding failed")
    mock_get_model.return_value = mock_model
    
    with pytest.raises(RuntimeError) as exc_info:
        embedder._embed_with_free_model(["test"])
    
    assert "Failed to generate embeddings" in str(exc_info.value)


@patch("src.rag.embedder.embedding_api_key", "sk-test")
@patch("src.rag.embedder.settings")
@patch("src.rag.embedder.logger")
def test_embed_with_openai_success(mock_logger, mock_settings):
    """Test successful embedding generation with OpenAI."""
    mock_settings.embedding_model = "text-embedding-3-small"
    
    # Mock the openai module in sys.modules
    mock_openai_module = MagicMock()
    mock_openai_class = MagicMock()
    mock_openai_module.OpenAI = mock_openai_class
    sys.modules['openai'] = mock_openai_module
    
    try:
        # Mock OpenAI client
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        # Simulate OpenAI response
        mock_response = MagicMock()
        mock_response.data = [
            MagicMock(embedding=[0.1] * 1536),
            MagicMock(embedding=[0.2] * 1536),
        ]
        mock_client.embeddings.create.return_value = mock_response
        
        result = embedder._embed_with_openai(["text1", "text2"])
        
        assert len(result) == 2
        assert len(result[0]) == 1536
        assert len(result[1]) == 1536
        mock_client.embeddings.create.assert_called_once_with(
            model="text-embedding-3-small",
            input=["text1", "text2"],
            timeout=30.0,
        )
    finally:
        # Clean up
        if 'openai' in sys.modules:
            del sys.modules['openai']


@patch("src.rag.embedder.embedding_api_key", "")
def test_embed_with_openai_no_api_key():
    """Test that ValueError is raised when no API key is available."""
    # This test doesn't need OpenAI import since it fails before that
    with pytest.raises(ValueError) as exc_info:
        embedder._embed_with_openai(["test"])
    
    assert "EMBEDDING_API_KEY or OPENAI_API_KEY must be set" in str(exc_info.value)
    assert "EMBEDDING_PROVIDER=local" in str(exc_info.value)


@patch("src.rag.embedder.embedding_api_key", "sk-invalid")
@patch("src.rag.embedder.settings")
@patch("src.rag.embedder.logger")
def test_embed_with_openai_invalid_api_key(mock_logger, mock_settings):
    """Test error handling for invalid API key."""
    mock_settings.embedding_model = "text-embedding-3-small"
    
    # Mock the openai module in sys.modules
    mock_openai_module = MagicMock()
    mock_openai_class = MagicMock()
    mock_openai_module.OpenAI = mock_openai_class
    
    # Store original if it exists
    original_openai = sys.modules.get('openai')
    sys.modules['openai'] = mock_openai_module
    
    try:
        # Mock OpenAI client
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        
        # Simulate 401 error (invalid API key) - the code checks for "401" in error string
        class MockError(Exception):
            def __str__(self):
                return "401 Invalid API key provided"
        
        mock_client.embeddings.create.side_effect = MockError("401 Invalid API key")
        
        # Reload the embedder module to pick up the mocked openai
        import importlib
        if 'src.rag.embedder' in sys.modules:
            importlib.reload(embedder)
        
        with pytest.raises(ValueError) as exc_info:
            embedder._embed_with_openai(["test"])
        
        assert "Invalid OpenAI API key" in str(exc_info.value)
        assert "EMBEDDING_PROVIDER=local" in str(exc_info.value)
    finally:
        # Clean up and restore
        if original_openai:
            sys.modules['openai'] = original_openai
        elif 'openai' in sys.modules:
            del sys.modules['openai']

