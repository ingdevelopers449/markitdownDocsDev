"""Core application configuration and constants."""
from pathlib import Path

APP_NAME = "Doc2Markdown Studio"
APP_VERSION = "1.0.0"

SUPPORTED_EXTENSIONS = {
    ".xlsx": "Excel Spreadsheet",
    ".xls": "Excel Spreadsheet (Legacy)",
    ".csv": "Comma Separated Values",
    ".docx": "Word Document",
    ".pptx": "PowerPoint Presentation",
    ".pdf": "PDF Document",
    ".html": "HTML Document",
    ".htm": "HTML Document",
    ".json": "JSON File",
    ".xml": "XML File",
    ".txt": "Plain Text",
}

DEFAULT_OUTPUT_DIR = Path.home() / "Documents" / "Markdown_Exports"

