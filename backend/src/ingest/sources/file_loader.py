"""File loading dispatcher."""

from pathlib import Path
from .md_loader import load_md
from .pdf_loader import load_pdf


def iter_files(root: str):
    """
    Iterate over all supported files in directory.

    Args:
        root: Root directory path

    Yields:
        Path objects for supported files
    """
    rootp = Path(root)
    if not rootp.exists():
        return
    for p in rootp.rglob("*"):
        if p.is_file():
            yield p


def load_file(path: Path) -> dict[str, str] | None:
    """
    Load file based on extension.

    Args:
        path: Path to file

    Returns:
        Dictionary with file content or None if unsupported format
    """
    ext = path.suffix.lower()
    if ext in [".md", ".mdx", ".txt"]:
        return load_md(path)
    if ext == ".pdf":
        return load_pdf(path)
    return None
