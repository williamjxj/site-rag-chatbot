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


def chunk_markdown_by_headings(
    text: str, headings: list[tuple[int, str, int]], max_chars: int = 1800, overlap: int = 200
) -> list[tuple[str, list[str]]]:
    """
    Chunk markdown text by headings, preserving heading paths.

    Args:
        text: Markdown text to chunk
        headings: List of (level, heading_text, position) tuples
        max_chars: Maximum characters per chunk
        overlap: Number of characters to overlap between chunks

    Returns:
        List of (chunk_text, heading_path) tuples where heading_path is a list of strings
    """
    if not headings:
        # No headings, fall back to regular chunking
        return [(chunk, []) for chunk in chunk_text(text, max_chars, overlap)]

    chunks = []
    # Track heading path: list of (level, heading_text) tuples
    heading_stack = []

    # Process each section between headings
    for i, (level, heading_text, heading_pos) in enumerate(headings):
        # Update heading stack: pop headings at same or deeper level
        while heading_stack and heading_stack[-1][0] >= level:
            heading_stack.pop()
        heading_stack.append((level, heading_text))
        
        # Build heading path from stack
        current_heading_path = [h for _, h in heading_stack]

        # Get section start and end positions
        section_start = heading_pos
        section_end = headings[i + 1][2] if i + 1 < len(headings) else len(text)

        # Extract section content (skip the heading line itself)
        section_text = text[section_start:section_end]
        # Remove the heading line from section content
        section_lines = section_text.split("\n")
        if section_lines and section_lines[0].strip().startswith("#"):
            section_text = "\n".join(section_lines[1:]).strip()
        else:
            section_text = section_text.strip()

        if not section_text or len(section_text) < 50:
            continue

        # If section fits in one chunk, use it as-is
        if len(section_text) <= max_chars:
            chunks.append((section_text, current_heading_path.copy()))
        else:
            # Section is too large, chunk it with overlap
            section_chunks = chunk_text(section_text, max_chars, overlap)
            for chunk in section_chunks:
                chunks.append((chunk, current_heading_path.copy()))

    # Handle content before first heading
    if headings and headings[0][2] > 0:
        intro_text = text[: headings[0][2]].strip()
        if intro_text and len(intro_text) >= 50:
            if len(intro_text) <= max_chars:
                chunks.insert(0, (intro_text, []))
            else:
                intro_chunks = chunk_text(intro_text, max_chars, overlap)
                chunks = [(chunk, []) for chunk in intro_chunks] + chunks

    # If no chunks were created, fall back to regular chunking
    if not chunks:
        return [(chunk, []) for chunk in chunk_text(text, max_chars, overlap)]

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
