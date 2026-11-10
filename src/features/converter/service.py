"""Conversion service implementing Microsoft MarkItDown with clean Markdown pipeline."""
import time
from pathlib import Path
from typing import Optional
from markitdown import MarkItDown

from src.core.config import SUPPORTED_EXTENSIONS
from src.core.exceptions import ConversionError, UnsupportedFormatError
from src.core.utils import estimate_tokens
from src.features.converter.models import ConversionRequest, ConversionResult

class ConversionService:
    """Service responsible for converting document files to clean Markdown."""

    def __init__(self):
        # Initialize official MarkItDown engine
        self._engine = MarkItDown()

    def is_supported(self, file_path: Path) -> bool:
        """Check if file extension is supported."""
        return file_path.suffix.lower() in SUPPORTED_EXTENSIONS

    def convert_file(self, request: ConversionRequest) -> ConversionResult:
        """
        Convert a single document file to Markdown.
        Cleans repetitive whitespaces and optimizes token footprint.
        """
        source = Path(request.source_path)
        if not source.exists():
            raise ConversionError(f"Archivo no encontrado: {source}")

        if not self.is_supported(source):
            raise UnsupportedFormatError(
                f"Formato no soportado: '{source.suffix}'. "
                f"Formatos soportados: {', '.join(SUPPORTED_EXTENSIONS.keys())}"
            )

        start_time = time.time()
        orig_size = source.stat().st_size

        try:
            # Perform conversion using MarkItDown
            result = self._engine.convert(str(source))
            raw_text = result.text_content or ""

            # Clean and optimize text to reduce token waste
            markdown_content = self._optimize_markdown(
                raw_text, 
                clean=request.clean_markdown,
                source=source,
                add_header=request.add_metadata_header
            )

            # Determine output path
            output_file = request.output_path
            if output_file is None:
                output_file = source.with_suffix(".md")

            # Write converted file
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text(markdown_content, encoding="utf-8")

            duration = time.time() - start_time
            md_size = len(markdown_content.encode("utf-8"))
            tokens = estimate_tokens(markdown_content)
            saved_bytes = max(0, orig_size - md_size)
            savings_pct = (saved_bytes / orig_size * 100) if orig_size > 0 else 0.0

            return ConversionResult(
                source_path=source,
                output_path=output_file,
                markdown_content=markdown_content,
                original_size_bytes=orig_size,
                markdown_size_bytes=md_size,
                estimated_tokens=tokens,
                saved_bytes=saved_bytes,
                savings_percentage=round(savings_pct, 1),
                duration_seconds=round(duration, 3),
                success=True
            )

        except Exception as e:
            duration = time.time() - start_time
            return ConversionResult(
                source_path=source,
                output_path=None,
                markdown_content="",
                original_size_bytes=orig_size,
                markdown_size_bytes=0,
                estimated_tokens=0,
                saved_bytes=0,
                savings_percentage=0.0,
                duration_seconds=round(duration, 3),
                success=False,
                error_message=str(e)
            )

    def _optimize_markdown(self, text: str, clean: bool, source: Path, add_header: bool) -> str:
        """Sanitizes Markdown to maximize prompt/context efficiency for LLMs."""
        if not text:
            return ""

        content = text
        if clean:
            # Replace 3 or more blank lines with just 2
            import re
            content = re.sub(r'\n{3,}', '\n\n', content)
            # Strip trailing whitespaces on lines
            content = "\n".join(line.rstrip() for line in content.splitlines())
            content = content.strip()

        if add_header:
            header = (
                f"<!-- Documento convertido: {source.name} -->\n"
                f"<!-- Optimizado para LLM / Historias de Usuario -->\n\n"
            )
            content = header + content

        return content

