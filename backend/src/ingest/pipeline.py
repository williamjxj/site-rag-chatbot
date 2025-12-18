"""Main ingestion orchestration."""

import uuid
from pathlib import Path

from ..db import SessionLocal, Chunk
from ..config import settings
from .chunking import chunk_text, chunk_markdown_by_headings, hash_text
from .normalize import normalize_text
from .dedupe import deduplicate_chunks
from .sources.sitemap_crawler import fetch_sitemap_urls, fetch_page
from .sources.file_loader import iter_files, load_file
from ..rag.embedder import embed_texts


def upsert_chunks(items: list[dict]) -> None:
    """
    Upsert chunks into database with embeddings.

    Args:
        items: List of chunk dictionaries with required fields
    """
    if not items:
        return

    with SessionLocal() as db:
        # Embed in batches
        texts = [it["text"] for it in items]
        embeddings = embed_texts(texts)

        for it, emb in zip(items, embeddings):
            existing = db.get(Chunk, it["id"])
            if existing:
                # Skip if unchanged
                if existing.text_hash == it["text_hash"]:
                    continue
                # Update existing chunk
                existing.text = it["text"]
                existing.text_hash = it["text_hash"]
                existing.embedding = emb
                existing.title = it.get("title")
                existing.heading_path = it.get("heading_path")
            else:
                # Insert new chunk
                db.add(
                    Chunk(
                        id=it["id"],
                        source=it["source"],
                        uri=it["uri"],
                        title=it.get("title"),
                        heading_path=it.get("heading_path"),
                        text=it["text"],
                        text_hash=it["text_hash"],
                        embedding=emb,
                    )
                )
        db.commit()


def ingest_website() -> None:
    """Ingest content from website via sitemap."""
    if not settings.sitemap_url:
        return

    urls = fetch_sitemap_urls(settings.sitemap_url)
    items = []
    for url in urls:
        try:
            page = fetch_page(url)
            normalized_text = normalize_text(page["text"])
            if not normalized_text:
                continue
            for chunk_text_content in chunk_text(normalized_text):
                h = hash_text(url + "\n" + chunk_text_content)
                items.append(
                    {
                        "id": str(uuid.uuid5(uuid.NAMESPACE_URL, h)),
                        "source": "web",
                        "uri": url,
                        "title": page.get("title"),
                        "heading_path": None,
                        "text": chunk_text_content,
                        "text_hash": h,
                    }
                )
        except Exception as e:
            print(f"Error processing {url}: {e}")
            continue

    if items:
        # Deduplicate before upserting
        items = deduplicate_chunks(items)
        upsert_chunks(items)
        print(f"Ingested {len(items)} chunks from website")


def ingest_docs() -> None:
    """Ingest content from local documents with heading-aware chunking for markdown."""
    docs_path = Path(settings.docs_dir)
    if not docs_path.exists():
        print(f"Docs directory not found: {docs_path}")
        return

    items = []
    for p in iter_files(settings.docs_dir):
        try:
            loaded = load_file(p)
            if not loaded or not loaded["text"].strip():
                continue
            uri = loaded.get("uri") or loaded.get("path")
            normalized_text = normalize_text(loaded["text"])
            if not normalized_text:
                continue

            # Check if this is a markdown file with headings
            # Re-extract headings from normalized text to ensure positions match
            from .sources.md_loader import extract_headings

            is_markdown = p.suffix.lower() in [".md", ".mdx"]
            headings = extract_headings(normalized_text) if is_markdown else None

            if is_markdown and headings:
                # Use heading-aware chunking for markdown
                chunked = chunk_markdown_by_headings(normalized_text, headings)
                for chunk_text_content, heading_path in chunked:
                    h = hash_text(uri + "\n" + str(heading_path) + "\n" + chunk_text_content)
                    items.append(
                        {
                            "id": str(uuid.uuid5(uuid.NAMESPACE_URL, h)),
                            "source": "file",
                            "uri": uri,
                            "title": loaded.get("title"),
                            "heading_path": heading_path if heading_path else None,
                            "text": chunk_text_content,
                            "text_hash": h,
                        }
                    )
            else:
                # Use regular chunking for other file types
                for chunk_text_content in chunk_text(normalized_text):
                    h = hash_text(uri + "\n" + chunk_text_content)
                    items.append(
                        {
                            "id": str(uuid.uuid5(uuid.NAMESPACE_URL, h)),
                            "source": "file",
                            "uri": uri,
                            "title": loaded.get("title"),
                            "heading_path": None,
                            "text": chunk_text_content,
                            "text_hash": h,
                        }
                    )
        except Exception as e:
            print(f"Error processing {p}: {e}")
            continue

    if items:
        # Deduplicate before upserting
        items = deduplicate_chunks(items)
        upsert_chunks(items)
        print(f"Ingested {len(items)} chunks from documents")


def ingest_all(source: str = "all") -> dict[str, int]:
    """
    Ingest all content sources.

    Args:
        source: Which source to ingest ('web', 'file', or 'all')

    Returns:
        Dictionary with ingestion statistics
    """
    stats = {"web_chunks": 0, "file_chunks": 0}

    if source in ["web", "all"]:
        ingest_website()
        # Count web chunks
        with SessionLocal() as db:
            from sqlalchemy import select, func
            result = db.execute(
                select(func.count(Chunk.id)).where(Chunk.source == "web")
            ).scalar()
            stats["web_chunks"] = result or 0

    if source in ["file", "all"]:
        ingest_docs()
        # Count file chunks
        with SessionLocal() as db:
            from sqlalchemy import select, func
            result = db.execute(
                select(func.count(Chunk.id)).where(Chunk.source == "file")
            ).scalar()
            stats["file_chunks"] = result or 0

    return stats
