"""Word document loader (.doc - old format).

Note: .doc files (old binary format) require additional system dependencies.
For best results, convert .doc files to .docx format.
"""

from pathlib import Path


def load_doc(path: Path) -> dict[str, str]:
    """
    Load and extract text from Word .doc file (old binary format).

    Args:
        path: Path to .doc file

    Returns:
        Dictionary with 'uri', 'title', and 'text' keys

    Raises:
        ValueError: If .doc file cannot be read (requires textract or similar)
    """
    # .doc files (old binary format) require textract or LibreOffice
    # For now, raise a helpful error
    raise ValueError(
        ".doc files (old binary format) are not directly supported. "
        "Please convert to .docx format or install textract with system dependencies. "
        "Alternatively, use .docx files which are fully supported."
    )

