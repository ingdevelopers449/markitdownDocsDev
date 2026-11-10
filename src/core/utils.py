"""Core utilities for token estimation and file operations."""
import os
import re
from pathlib import Path
from typing import Tuple

def estimate_tokens(text: str) -> int:
    """
    Estimate token count for LLMs (approx. 4 chars or 0.75 words per token).
    Provides consistent estimation across OpenAI/Claude/Gemini formats.
    """
    if not text:
        return 0
    # Clean whitespace
    words = len(re.findall(r'\S+', text))
    chars = len(text)
    # Heuristic: roughly 1 token ~ 3.5 to 4 characters or ~0.75 word
    token_est_chars = chars / 3.8
    token_est_words = words * 1.3
    return int(max(token_est_chars, token_est_words))

def get_file_metadata(file_path: Path) -> dict:
    """Retrieve file size, extension, and basic stats."""
    if not file_path.exists():
        return {}
    stat = file_path.stat()
    return {
        "name": file_path.name,
        "extension": file_path.suffix.lower(),
        "size_bytes": stat.st_size,
        "size_kb": round(stat.st_size / 1024, 2),
    }

def format_size(size_bytes: int) -> str:
    """Convert size in bytes to human-readable string."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

