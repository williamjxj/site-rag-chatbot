"""PDF document loader."""

from pathlib import Path
from pypdf import PdfReader


def load_pdf(path: Path) -> dict[str, str]:
    """
    Load and extract text from PDF file.

    Args:
        path: Path to PDF file

    Returns:
        Dictionary with 'path', 'title', and 'text' keys
    """
    reader = PdfReader(str(path))
    parts = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            parts.append(text)
    text = "\n".join(parts).strip()
    return {"path": str(path), "title": path.name, "text": text}
