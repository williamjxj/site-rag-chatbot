"""Text normalization utilities."""

import re


def normalize_text(text: str) -> str:
    """
    Normalize text by removing excessive whitespace and cleaning up.

    Args:
        text: Raw text to normalize

    Returns:
        Normalized text
    """
    # Remove excessive whitespace
    text = re.sub(r"\s+", " ", text)
    # Remove excessive newlines
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Strip leading/trailing whitespace
    text = text.strip()
    return text
