"""History models and persistence service."""
import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from src.features.converter.models import ConversionResult

import os
from pathlib import Path

# Save history inside local application directory or local appdata to avoid permission issues
APP_DATA_DIR = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "Doc2Markdown"
APP_DATA_DIR.mkdir(parents=True, exist_ok=True)
HISTORY_FILE = APP_DATA_DIR / "history.json"

class HistoryService:
    """Manages conversion logs and audit history for developers."""

    def __init__(self, storage_path: Path = HISTORY_FILE):
        self.storage_path = storage_path

    def record_conversion(self, result: ConversionResult) -> None:
        """Appends a conversion result to history file."""
        entry = {
            "source": str(result.source_path),
            "output": str(result.output_path) if result.output_path else None,
            "success": result.success,
            "original_size": result.original_size_bytes,
            "markdown_size": result.markdown_size_bytes,
            "estimated_tokens": result.estimated_tokens,
            "savings_percentage": result.savings_percentage,
            "duration_seconds": result.duration_seconds,
            "timestamp": result.converted_at.isoformat(),
            "error": result.error_message,
        }

        history = self.get_all()
        history.insert(0, entry)
        # Keep latest 200 records
        history = history[:200]

        try:
            self.storage_path.write_text(json.dumps(history, indent=2), encoding="utf-8")
        except Exception:
            pass

    def get_all(self) -> List[Dict[str, Any]]:
        """Reads all history records."""
        if not self.storage_path.exists():
            return []
        try:
            return json.loads(self.storage_path.read_text(encoding="utf-8"))
        except Exception:
            return []

    def clear(self) -> None:
        """Clears conversion history."""
        if self.storage_path.exists():
            try:
                self.storage_path.unlink()
            except Exception:
                pass

