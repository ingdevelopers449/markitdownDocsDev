"""Core exceptions and error handling."""

class Doc2MarkdownError(Exception):
    """Base exception for application."""
    pass

class ConversionError(Doc2MarkdownError):
    """Raised when file conversion fails."""
    pass

class UnsupportedFormatError(Doc2MarkdownError):
    """Raised when input file format is not supported."""
    pass

class OutputWriteError(Doc2MarkdownError):
    """Raised when markdown file cannot be saved."""
    pass

