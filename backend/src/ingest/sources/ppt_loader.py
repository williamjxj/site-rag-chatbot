"""PowerPoint document loader (.ppt - old format).

Note: .ppt files (old binary format) require additional system dependencies.
For best results, convert .ppt files to .pptx format.
"""

from pathlib import Path


def load_ppt(path: Path) -> dict[str, str]:
    """
    Load and extract text from PowerPoint .ppt file (old binary format).

    Args:
        path: Path to .ppt file

    Returns:
        Dictionary with 'uri', 'title', and 'text' keys

    Raises:
        ValueError: If .ppt file cannot be read (requires textract or similar)
    """
    # .ppt files (old binary format) require textract or LibreOffice
    # For now, raise a helpful error
    raise ValueError(
        ".ppt files (old binary format) are not directly supported. "
        "Please convert to .pptx format or install textract with system dependencies. "
        "Alternatively, use .pptx files which are fully supported."
    )

