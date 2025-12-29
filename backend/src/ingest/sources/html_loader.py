"""HTML file loader."""

from pathlib import Path
from bs4 import BeautifulSoup


def load_html(path: Path) -> dict[str, str]:
    """
    Load and extract text from HTML file.

    Args:
        path: Path to HTML file

    Returns:
        Dictionary with 'uri', 'title', and 'text' keys
    """
    html = path.read_text(encoding="utf-8", errors="ignore")
    soup = BeautifulSoup(html, "lxml")
    
    # Remove common boilerplate tags
    for tag in soup(["script", "style", "noscript", "svg"]):
        tag.decompose()
    
    # Extract title
    title = path.stem
    if soup.title and soup.title.text:
        title = soup.title.text.strip()
    
    # Prefer <main> if available
    main = soup.find("main")
    node = main if main else soup.body or soup
    
    if not node:
        text = ""
    else:
        text = node.get_text("\n", strip=True)
    
    return {"uri": str(path), "title": title, "text": text}

