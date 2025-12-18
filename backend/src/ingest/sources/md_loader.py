"""Markdown and text file loader with heading extraction."""

import re
from pathlib import Path
from datetime import datetime


def extract_headings(text: str) -> list[tuple[int, str, int]]:
    """
    Extract headings from markdown text with their levels and positions.

    Args:
        text: Markdown text content

    Returns:
        List of tuples: (level, heading_text, start_position)
    """
    headings = []
    lines = text.split("\n")
    pos = 0

    for i, line in enumerate(lines):
        line_stripped = line.strip()

        # ATX-style headings (# ## ###)
        match = re.match(r"^(#{1,6})\s+(.+)$", line_stripped)
        if match:
            level = len(match.group(1))
            heading_text = match.group(2).strip()
            headings.append((level, heading_text, pos))

        # Setext-style headings (=== or ---)
        elif i > 0 and line_stripped:
            prev_line = lines[i - 1].strip()
            if prev_line:
                if re.match(r"^=+$", line_stripped):
                    headings.append((1, prev_line, pos - len(lines[i - 1]) - 1))
                elif re.match(r"^-+$", line_stripped):
                    headings.append((2, prev_line, pos - len(lines[i - 1]) - 1))

        pos += len(line) + 1  # +1 for newline

    return headings




def load_md(path: Path) -> dict:
    """
    Load text from Markdown or text file with heading extraction.

    Args:
        path: Path to file

    Returns:
        Dictionary with 'uri', 'title', 'text', 'heading_path' (optional), and 'last_modified' (optional)
    """
    text = path.read_text(encoding="utf-8", errors="ignore")
    title = path.stem  # filename without extension

    # Get last modified time if available
    last_modified = None
    try:
        stat = path.stat()
        last_modified = datetime.fromtimestamp(stat.st_mtime).isoformat()
    except OSError:
        pass

    result = {
        "uri": str(path),
        "title": title,
        "text": text,
    }

    # Extract headings for markdown files (stored for heading-aware chunking)
    if path.suffix.lower() in [".md", ".mdx"]:
        headings = extract_headings(text)
        if headings:
            result["headings"] = headings

    if last_modified:
        result["last_modified"] = last_modified

    return result
