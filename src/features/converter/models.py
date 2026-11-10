"""Data models for conversion feature."""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
from datetime import datetime

@dataclass
class ConversionRequest:
    """Represents a file conversion request."""
    source_path: Path
    output_path: Optional[Path] = None
    clean_markdown: bool = True
    add_metadata_header: bool = True

@dataclass
class ConversionResult:
    """Represents the output and statistics of a conversion."""
    source_path: Path
    output_path: Optional[Path]
    markdown_content: str
    original_size_bytes: int
    markdown_size_bytes: int
    estimated_tokens: int
    saved_bytes: int
    savings_percentage: float
    duration_seconds: float
    success: bool
    error_message: Optional[str] = None
    converted_at: datetime = field(default_factory=datetime.now)

