"""Unit and integration tests for Doc2Markdown."""
import unittest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock
from src.features.converter.service import ConversionService
from src.features.converter.models import ConversionRequest
from src.core.utils import estimate_tokens, format_size
from src.features.batch.service import BatchService
from src.features.history.service import HistoryService
from src.features.converter.models import ConversionResult

class TestDoc2Markdown(unittest.TestCase):
    def test_token_estimation(self):
        text = "Esta es una historia de usuario de prueba con varios criterios de aceptacion."
        tokens = estimate_tokens(text)
        self.assertGreater(tokens, 0)

    def test_format_size(self):
        self.assertEqual(format_size(500), "500.0 B")
        self.assertEqual(format_size(1024), "1.0 KB")

    def test_excel_conversion(self):
        excel_path = Path("test_historia_usuario.xlsx")
        if excel_path.exists():
            service = ConversionService()
            req = ConversionRequest(source_path=excel_path)
            res = service.convert_file(req)
            self.assertTrue(res.success)
            self.assertIn("| ID Historia |", res.markdown_content)
            self.assertGreater(res.estimated_tokens, 0)

    def test_missing_file_returns_failed_result(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            missing = Path(temp_dir) / "missing.pdf"
            res = ConversionService().convert_file(
                ConversionRequest(source_path=missing)
            )
        self.assertFalse(res.success)
        self.assertIn("no encontrado", res.error_message)

    def test_unsupported_file_returns_failed_result(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "archivo.bin"
            source.write_bytes(b"datos")
            res = ConversionService().convert_file(
                ConversionRequest(source_path=source)
            )
        self.assertFalse(res.success)
        self.assertIn("Formato no soportado", res.error_message)

    def test_batch_unique_output_names(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            first = temp / "uno" / "reporte.xlsx"
            second = temp / "dos" / "reporte.xlsx"
            first.parent.mkdir()
            second.parent.mkdir()
            first.write_bytes(b"uno")
            second.write_bytes(b"dos")

            converter = Mock()
            converter.is_supported.side_effect = lambda path: True

            def convert(req):
                target = req.output_path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text("markdown", encoding="utf-8")
                return ConversionResult(
                    source_path=Path(req.source_path),
                    output_path=target,
                    markdown_content="markdown",
                    original_size_bytes=3,
                    markdown_size_bytes=8,
                    estimated_tokens=2,
                    saved_bytes=0,
                    savings_percentage=0,
                    duration_seconds=0.01,
                    success=True,
                )

            converter.convert_file.side_effect = convert
            output_dir = temp / "salida"
            results = BatchService(converter).convert_batch(
                [first, second], output_dir=output_dir
            )

            self.assertEqual(len(results), 2)
            targets = {str(r.output_path.resolve()).lower() for r in results}
            self.assertEqual(len(targets), 2)

    def test_history_is_written_atomically_and_limited(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            history_file = Path(temp_dir) / "history.json"
            history = HistoryService(history_file)
            for index in range(205):
                history.record_conversion(
                    ConversionResult(
                        source_path=Path(f"source-{index}.txt"),
                        output_path=Path(f"output-{index}.md"),
                        markdown_content="",
                        original_size_bytes=10,
                        markdown_size_bytes=5,
                        estimated_tokens=2,
                        saved_bytes=5,
                        savings_percentage=50,
                        duration_seconds=0.1,
                        success=True,
                    )
                )

            records = history.get_all()
            self.assertEqual(len(records), 200)
            json.loads(history_file.read_text(encoding="utf-8"))

if __name__ == "__main__":
    unittest.main()
