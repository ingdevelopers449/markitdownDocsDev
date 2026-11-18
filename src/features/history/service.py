"""History models and persistence service."""
import json
import os
import tempfile
import threading
from pathlib import Path
from typing import List, Dict, Any

from src.features.converter.models import ConversionResult

from src.core.exceptions import HistoryError

# Save history inside local application directory or local appdata to avoid permission issues
APP_DATA_DIR = Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "Doc2Markdown"
APP_DATA_DIR.mkdir(parents=True, exist_ok=True)
HISTORY_FILE = APP_DATA_DIR / "history.json"

class HistoryService:
    """Manages conversion logs and audit history for developers."""

    def __init__(self, storage_path: Path = HISTORY_FILE):
        self.storage_path = storage_path
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()

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

        with self._lock:
            history = self.get_all()
            history.insert(0, entry)
            history = history[:200]
            temp_name = None
            try:
                with tempfile.NamedTemporaryFile(
                    mode="w",
                    encoding="utf-8",
                    dir=str(self.storage_path.parent),
                    prefix=f".{self.storage_path.name}.",
                    suffix=".tmp",
                    delete=False,
                ) as temp_file:
                    json.dump(history, temp_file, indent=2)
                    temp_name = temp_file.name
                os.replace(temp_name, self.storage_path)
            except Exception as exc:
                if temp_name:
                    try:
                        Path(temp_name).unlink(missing_ok=True)
                    except OSError:
                        pass
                raise HistoryError(f"No se pudo guardar el historial: {exc}") from exc

    def get_all(self) -> List[Dict[str, Any]]:
        """Reads all history records."""
        if not self.storage_path.exists():
            return []
        try:
            with self._lock:
                return json.loads(self.storage_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise HistoryError("El archivo de historial esta corrupto") from exc
        except OSError as exc:
            raise HistoryError(f"No se pudo leer el historial: {exc}") from exc

    def clear(self) -> None:
        """Clears conversion history."""
        if self.storage_path.exists():
            try:
                with self._lock:
                    self.storage_path.unlink()
            except OSError as exc:
                raise HistoryError(f"No se pudo limpiar el historial: {exc}") from exc
