"""Unit and integration tests for Doc2Markdown."""
import unittest
from pathlib import Path
from src.features.converter.service import ConversionService
from src.features.converter.models import ConversionRequest
from src.core.utils import estimate_tokens, format_size

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

if __name__ == "__main__":
    unittest.main()
