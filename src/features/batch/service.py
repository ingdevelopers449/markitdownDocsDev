"""Batch processing service for converting multiple files or folders."""
from pathlib import Path
from typing import List, Callable, Optional
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.features.converter.service import ConversionService
from src.features.converter.models import ConversionRequest, ConversionResult

class BatchService:
    """Service to handle batch conversions with concurrent execution and progress callbacks."""

    def __init__(self, conversion_service: Optional[ConversionService] = None):
        self._converter = conversion_service or ConversionService()

    def discover_files(self, directory: Path, recursive: bool = True) -> List[Path]:
        """Discover all supported document files in a directory."""
        directory = Path(directory)
        if not directory.is_dir():
            return []

        pattern = "**/*" if recursive else "*"
        found = []
        for p in directory.glob(pattern):
            if p.is_file() and self._converter.is_supported(p):
                # Avoid processing already converted .md files
                if p.suffix.lower() != ".md":
                    found.append(p)
        return sorted(found)

    def convert_batch(
        self,
        files: List[Path],
        output_dir: Optional[Path] = None,
        progress_callback: Optional[Callable[[int, int, ConversionResult], None]] = None,
        max_workers: int = 4,
        cancel_event: Optional[threading.Event] = None,
    ) -> List[ConversionResult]:
        """
        Convert multiple files concurrently.
        Calls progress_callback(completed, total, result) after each file.
        """
        total = len(files)
        results: List[ConversionResult] = []

        if total == 0:
            return results

        allocated_targets = set()
        target_lock = threading.Lock()

        def unique_target(source_file: Path) -> Optional[Path]:
            if output_dir is None:
                return None
            with target_lock:
                stem = source_file.stem
                if stem.lower().endswith(".xlsx") or stem.lower().endswith(".xls"):
                    stem = stem.rsplit(".", 1)[0]
                target = Path(output_dir) / f"{stem}.md"
                candidate = target
                suffix = 2
                key = str(candidate.resolve()).lower()
                while candidate.exists() or key in allocated_targets:
                    candidate = target.with_name(f"{target.stem}_{suffix}{target.suffix}")
                    suffix += 1
                    key = str(candidate.resolve()).lower()
                allocated_targets.add(key)
                return candidate

        def process_one(source_file: Path) -> Optional[ConversionResult]:
            if cancel_event and cancel_event.is_set():
                return None
            target = None
            if output_dir:
                target = unique_target(source_file)
            req = ConversionRequest(source_path=source_file, output_path=target)
            return self._converter.convert_file(req)

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_file = {executor.submit(process_one, f): f for f in files}
            completed_count = 0

            for future in as_completed(future_to_file):
                res = future.result()
                if res is None:
                    continue
                results.append(res)
                completed_count += 1
                if progress_callback:
                    progress_callback(completed_count, total, res)

        return results
