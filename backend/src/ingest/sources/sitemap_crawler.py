"""Website crawling via sitemap."""

import requests
import xml.etree.ElementTree as ET
from urllib.parse import urljoin
from bs4 import BeautifulSoup


def fetch_sitemap_urls(sitemap_url: str) -> list[str]:
    """
    Fetch all URLs from a sitemap.xml.

    Args:
        sitemap_url: URL to sitemap.xml

    Returns:
        List of URLs from sitemap
    """
    response = requests.get(sitemap_url, timeout=30)
    response.raise_for_status()
    root = ET.fromstring(response.text)
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = []
    for loc in root.findall(".//sm:loc", ns):
        if loc.text:
            urls.append(loc.text.strip())
    return urls


def html_to_text(html: str) -> str:
    """
    Extract text from HTML, removing boilerplate.

    Args:
        html: HTML content

    Returns:
        Extracted text
    """
    soup = BeautifulSoup(html, "lxml")
    # Remove common boilerplate tags
    for tag in soup(["script", "style", "noscript", "svg"]):
        tag.decompose()
    # Prefer <main> if available
    main = soup.find("main")
    node = main if main else soup.body or soup
    if not node:
        return ""
    text = node.get_text("\n", strip=True)
    return text


def fetch_page(url: str) -> dict[str, str | None]:
    """
    Fetch a webpage and extract text content.

    Args:
        url: URL to fetch

    Returns:
        Dictionary with 'url', 'title', and 'text' keys
    """
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    html = response.text
    text = html_to_text(html)
    title = None
    soup = BeautifulSoup(html, "lxml")
    if soup.title and soup.title.text:
        title = soup.title.text.strip()
    return {"url": url, "title": title, "text": text}
