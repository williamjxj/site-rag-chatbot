"""Deduplication logic for chunks."""

from typing import Any


def deduplicate_chunks(chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Remove duplicate chunks based on text_hash.

    Args:
        chunks: List of chunk dictionaries with 'text_hash' key

    Returns:
        Deduplicated list of chunks
    """
    seen_hashes = set()
    unique_chunks = []

    for chunk in chunks:
        text_hash = chunk.get("text_hash")
        if text_hash and text_hash not in seen_hashes:
            seen_hashes.add(text_hash)
            unique_chunks.append(chunk)

    return unique_chunks
