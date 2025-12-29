"""CSV file loader."""

from pathlib import Path
import csv


def load_csv(path: Path) -> dict[str, str]:
    """
    Load and extract text from CSV file.

    Args:
        path: Path to CSV file

    Returns:
        Dictionary with 'uri', 'title', and 'text' keys
    """
    parts = []
    
    try:
        with open(path, "r", encoding="utf-8", errors="ignore", newline="") as f:
            # Try to detect delimiter
            sample = f.read(1024)
            f.seek(0)
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(sample).delimiter
            
            reader = csv.reader(f, delimiter=delimiter)
            
            # Read all rows
            for row_num, row in enumerate(reader, 1):
                # Join row values with pipe separator
                row_text = " | ".join(str(cell) if cell else "" for cell in row)
                if row_text.strip():
                    parts.append(row_text)
    except Exception as e:
        # Fallback: try with comma delimiter
        try:
            with open(path, "r", encoding="utf-8", errors="ignore", newline="") as f:
                reader = csv.reader(f, delimiter=",")
                for row in reader:
                    row_text = " | ".join(str(cell) if cell else "" for cell in row)
                    if row_text.strip():
                        parts.append(row_text)
        except Exception:
            raise ValueError(f"Failed to read CSV file: {e}") from e
    
    text = "\n".join(parts).strip()
    return {"uri": str(path), "title": path.stem, "text": text}

