"""Markdown and text file loader."""

from pathlib import Path


def load_md(path: Path) -> dict[str, str]:
    """
    Load text from Markdown or text file.

    Args:
        path: Path to file

    Returns:
        Dictionary with 'path', 'title', and 'text' keys
    """
    text = path.read_text(encoding="utf-8", errors="ignore")
    title = path.name
    return {"path": str(path), "title": title, "text": text}
