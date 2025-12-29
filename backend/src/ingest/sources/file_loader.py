"""File loading dispatcher."""

from pathlib import Path
from .md_loader import load_md
from .pdf_loader import load_pdf
from .docx_loader import load_docx
from .doc_loader import load_doc
from .excel_loader import load_excel
from .pptx_loader import load_pptx
from .ppt_loader import load_ppt
from .html_loader import load_html
from .csv_loader import load_csv


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
    if ext == ".docx":
        return load_docx(path)
    if ext == ".doc":
        # .doc (old format) may raise ValueError with helpful message
        return load_doc(path)
    if ext in [".xlsx", ".xls"]:
        return load_excel(path)
    if ext == ".pptx":
        return load_pptx(path)
    if ext == ".ppt":
        # .ppt (old format) may raise ValueError with helpful message
        return load_ppt(path)
    if ext in [".html", ".htm"]:
        return load_html(path)
    if ext == ".csv":
        return load_csv(path)
    return None
