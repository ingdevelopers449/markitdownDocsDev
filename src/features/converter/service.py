"""Conversion service implementing Microsoft MarkItDown with clean Markdown pipeline."""
import logging
import os
import re
import tempfile
import time
from pathlib import Path
try:
    from markitdown import MarkItDown
except ImportError:
    MarkItDown = None

from src.core.config import SUPPORTED_EXTENSIONS
from src.core.exceptions import ConversionError, UnsupportedFormatError, OutputWriteError
from src.core.utils import estimate_tokens
from src.features.converter.models import ConversionRequest, ConversionResult
from src.features.converter.sniffer import sniff_and_read_tabular, dataframe_to_markdown

class ConversionService:
    """Service responsible for converting document files to clean Markdown with auto-detection."""

    def __init__(self):
        # Lazy initialization: do not load heavy Magika/ONNX models during app startup
        self._engine = None

    @property
    def engine(self):
        """Loads MarkItDown engine on first conversion request."""
        if self._engine is None:
            if MarkItDown is None:
                raise ConversionError(
                    "MarkItDown no esta disponible para esta version de Python"
                )
            self._engine = MarkItDown()
        return self._engine

    def is_supported(self, file_path: Path) -> bool:
        """Check if file extension is supported."""
        ext = file_path.suffix.lower()
        # Handle compound extensions like .xlsx.xls or any known extension
        return ext in SUPPORTED_EXTENSIONS or file_path.name.lower().endswith(tuple(SUPPORTED_EXTENSIONS.keys()))

    def convert_file(self, request: ConversionRequest) -> ConversionResult:
        """
        Convert a single document file to Markdown.
        Automatically detects file structure and applies fallback parsers.
        """
        try:
            source = Path(request.source_path)
            start_time = time.time()
            if not source.exists():
                raise ConversionError(f"Archivo no encontrado: {source}")
            if not source.is_file():
                raise ConversionError(f"La ruta no es un archivo: {source}")
            if not self.is_supported(source):
                raise UnsupportedFormatError(f"Formato no soportado: {source.suffix.lower() or '(sin extension)'}")

            orig_size = source.stat().st_size
            raw_text = ""

            # 1. Primary Strategy: Microsoft MarkItDown engine
            try:
                result = self.engine.convert(str(source))
                raw_text = result.text_content or ""
            except Exception as markitdown_exc:
                # 2. Resilient Fallback Strategy: Auto-detect and parse (Excel/HTML/CSV)
                df = sniff_and_read_tabular(source)
                if df is not None and not df.empty:
                    raw_text = dataframe_to_markdown(df)
                else:
                    logging.debug("MarkItDown fallo para %s", source, exc_info=markitdown_exc)
                    raise markitdown_exc

            # If MarkItDown returned raw HTML table tags (e.g. from an HTML-based .xls), clean them into markdown
            if "<table" in raw_text.lower():
                df = sniff_and_read_tabular(source)
                if df is not None and not df.empty:
                    raw_text = dataframe_to_markdown(df)

            # Clean and optimize text to reduce token waste
            markdown_content = self._optimize_markdown(
                raw_text, 
                clean=request.clean_markdown,
                source=source,
                add_header=request.add_metadata_header
            )

            # Determine output path (.md)
            output_file = request.output_path
            if output_file is None:
                # Remove last extension or compound extension
                stem = source.stem
                if stem.lower().endswith(".xlsx") or stem.lower().endswith(".xls"):
                    stem = Path(stem).stem
                output_file = source.with_name(f"{stem}.md")

            # Write converted file
            output_file.parent.mkdir(parents=True, exist_ok=True)
            temp_name = None
            try:
                with tempfile.NamedTemporaryFile(
                    mode="w",
                    encoding="utf-8",
                    dir=str(output_file.parent),
                    prefix=f".{output_file.name}.",
                    suffix=".tmp",
                    delete=False,
                ) as temp_file:
                    temp_file.write(markdown_content)
                    temp_name = temp_file.name
                os.replace(temp_name, output_file)
            except Exception as exc:
                if temp_name:
                    try:
                        Path(temp_name).unlink(missing_ok=True)
                    except OSError:
                        pass
                raise OutputWriteError(
                    f"No se pudo guardar el archivo Markdown '{output_file}': {exc}"
                ) from exc

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
            if "source" not in locals():
                source = Path(request.source_path)
            if "start_time" not in locals():
                start_time = time.time()
            if "orig_size" not in locals():
                orig_size = source.stat().st_size if source.exists() and source.is_file() else 0
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
