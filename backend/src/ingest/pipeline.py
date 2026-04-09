"""Main ingestion orchestration."""

import uuid
from pathlib import Path

from ..config import settings
from ..db import Chunk, SessionLocal
from ..rag.embedder import embed_texts
from .chunking import chunk_markdown_by_headings, chunk_text, hash_text
from .dedupe import deduplicate_chunks
from .normalize import normalize_text
from .sources.file_loader import iter_files, load_file
from .sources.sitemap_crawler import fetch_page, fetch_sitemap_urls


def upsert_chunks(items: list[dict], user_id: int | None = None) -> None:
    """
    Upsert chunks into database with embeddings.

    Args:
        items: List of chunk dictionaries with required fields
        user_id: Optional user ID for multi-tenant isolation
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
                if user_id:
                    existing.user_id = user_id
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
                        user_id=user_id,
                    )
                )
        db.commit()


def ingest_website(user_id: int | None = None) -> None:
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
                        "user_id": user_id,
                    }
                )
        except Exception as e:
            print(f"Error processing {url}: {e}")

    if items:
        items = deduplicate_chunks(items)
        upsert_chunks(items, user_id)

    if items:
        # Deduplicate before upserting
        items = deduplicate_chunks(items)
        upsert_chunks(items)
        print(f"Ingested {len(items)} chunks from website")


def ingest_single_file(file_path: Path, user_id: int | None = None) -> int:
    """
    Ingest a single file and return the number of chunks created.

    Args:
        file_path: Path to the file to ingest
        user_id: Optional user ID for multi-tenant isolation

    Returns:
        Number of chunks ingested
    """
    items = []
    try:
        loaded = load_file(file_path)
        if not loaded or not loaded["text"].strip():
            return 0

        uri = loaded.get("uri") or loaded.get("path") or str(file_path)
        normalized_text = normalize_text(loaded["text"])
        if not normalized_text:
            return 0

        # Check if this is a markdown file with headings
        from .sources.md_loader import extract_headings

        is_markdown = file_path.suffix.lower() in [".md", ".mdx"]
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
                        "user_id": user_id,
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
                        "user_id": user_id,
                    }
                )
    except Exception as e:
        raise ValueError(f"Error processing {file_path}: {e}") from e

    if items:
        # Deduplicate before upserting
        items = deduplicate_chunks(items)
        upsert_chunks(items, user_id)
        return len(items)
    return 0


def ingest_docs(user_id: int | None = None) -> None:
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

            from .sources.md_loader import extract_headings

            is_markdown = p.suffix.lower() in [".md", ".mdx"]
            headings = extract_headings(normalized_text) if is_markdown else None

            if is_markdown and headings:
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
                            "user_id": user_id,
                        }
                    )
            else:
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
                            "user_id": user_id,
                        }
                    )
        except Exception as e:
            print(f"Error processing {p}: {e}")

    if items:
        items = deduplicate_chunks(items)
        upsert_chunks(items, user_id)
        print(f"Ingested {len(items)} chunks from documents")


def ingest_all(source: str = "all", user_id: int | None = None) -> dict[str, int]:
    """
    Ingest all content sources.

    Args:
        source: Which source to ingest ('web', 'file', or 'all')
        user_id: Optional user ID for multi-tenant isolation

    Returns:
        Dictionary with ingestion statistics
    """
    stats = {"web_chunks": 0, "file_chunks": 0}

    if source in ["web", "all"]:
        ingest_website(user_id)
        # Count web chunks for this user
        with SessionLocal() as db:
            from sqlalchemy import func, select

            if user_id:
                result = db.execute(
                    select(func.count(Chunk.id)).where(Chunk.source == "web", Chunk.user_id == user_id)
                ).scalar()
            else:
                result = db.execute(select(func.count(Chunk.id)).where(Chunk.source == "web")).scalar()
            stats["web_chunks"] = result or 0

    if source in ["file", "all"]:
        ingest_docs(user_id)
        # Count file chunks for this user
        with SessionLocal() as db:
            from sqlalchemy import func, select

            if user_id:
                result = db.execute(
                    select(func.count(Chunk.id)).where(Chunk.source == "file", Chunk.user_id == user_id)
                ).scalar()
            else:
                result = db.execute(select(func.count(Chunk.id)).where(Chunk.source == "file")).scalar()
            stats["file_chunks"] = result or 0

    return stats
