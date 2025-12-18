"""Text chunking logic."""

import re
import hashlib


def chunk_text(text: str, max_chars: int = 1800, overlap: int = 200) -> list[str]:
    """
    Chunk text into segments with overlap.

    Args:
        text: Text to chunk
        max_chars: Maximum characters per chunk
        overlap: Number of characters to overlap between chunks

    Returns:
        List of text chunks (minimum 50 characters)
    """
    # Normalize whitespace
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    if not text:
        return []

    chunks = []
    i = 0
    while i < len(text):
        j = min(len(text), i + max_chars)
        chunk = text[i:j].strip()
        if len(chunk) > 50:  # Filter out very short chunks
            chunks.append(chunk)
        i = max(0, j - overlap)
        if j == len(text):
            break

    return chunks


def hash_text(s: str) -> str:
    """
    Generate SHA-256 hash of text.

    Args:
        s: Text to hash

    Returns:
        Hexadecimal hash string (64 characters)
    """
    return hashlib.sha256(s.encode("utf-8")).hexdigest()
