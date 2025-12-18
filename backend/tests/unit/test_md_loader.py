"""Unit tests for markdown loader."""

import tempfile
from pathlib import Path

from src.ingest.sources.md_loader import load_md, extract_headings


def test_extract_headings_atx_style():
    """Test extraction of ATX-style headings (# ## ###)."""
    text = """# Introduction
Some intro text.

## Getting Started
More text here.

### Installation
Install steps.

## Usage
Usage info.
"""
    headings = extract_headings(text)
    assert len(headings) == 4
    assert headings[0] == (1, "Introduction", 0)
    assert headings[1] == (2, "Getting Started", len("# Introduction\nSome intro text.\n\n"))
    assert headings[2][0] == 3
    assert headings[2][1] == "Installation"
    assert headings[3][0] == 2
    assert headings[3][1] == "Usage"


def test_extract_headings_setext_style():
    """Test extraction of Setext-style headings (=== and ---)."""
    text = """Introduction
============

Some text.

Getting Started
---------------

More text.
"""
    headings = extract_headings(text)
    assert len(headings) >= 2
    # Setext headings should be detected
    assert any(h[1] == "Introduction" for h in headings)
    assert any(h[1] == "Getting Started" for h in headings)


def test_load_md_basic():
    """Test basic markdown file loading."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("# Test Document\n\nThis is test content.")
        temp_path = Path(f.name)

    try:
        result = load_md(temp_path)
        assert result["uri"] == str(temp_path)
        assert result["title"] == temp_path.stem
        assert "Test Document" in result["text"]
        assert "headings" in result
        assert len(result["headings"]) > 0
        assert result["headings"][0][1] == "Test Document"
    finally:
        temp_path.unlink()


def test_load_md_with_headings():
    """Test markdown loading with multiple headings."""
    content = """# Main Title

Introduction paragraph.

## Section One

Content for section one.

### Subsection 1.1

Subsection content.

## Section Two

Content for section two.
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(content)
        temp_path = Path(f.name)

    try:
        result = load_md(temp_path)
        assert "headings" in result
        headings = result["headings"]
        assert len(headings) == 4
        assert headings[0][1] == "Main Title"
        assert headings[0][0] == 1
        assert headings[1][1] == "Section One"
        assert headings[1][0] == 2
        assert headings[2][1] == "Subsection 1.1"
        assert headings[2][0] == 3
        assert headings[3][1] == "Section Two"
        assert headings[3][0] == 2
    finally:
        temp_path.unlink()


def test_load_md_no_headings():
    """Test markdown file without headings."""
    content = "Just plain text without any headings.\n\nMore text here."
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(content)
        temp_path = Path(f.name)

    try:
        result = load_md(temp_path)
        assert result["uri"] == str(temp_path)
        assert result["text"] == content
        # Should still have headings key but empty list
        assert "headings" not in result or len(result.get("headings", [])) == 0
    finally:
        temp_path.unlink()


def test_load_md_last_modified():
    """Test that last_modified is included when available."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("# Test")
        temp_path = Path(f.name)

    try:
        result = load_md(temp_path)
        assert "last_modified" in result
        assert result["last_modified"] is not None
    finally:
        temp_path.unlink()

