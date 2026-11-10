"""Automatic file format sniffer and converter with fallback mechanisms."""
import csv
import io
from pathlib import Path
from typing import Optional
import pandas as pd
from markitdown import MarkItDown

def sniff_and_read_tabular(file_path: Path) -> Optional[pd.DataFrame]:
    """Attempts to auto-detect tabular formats (Excel, HTML tables, CSV/TSV) regardless of file extension."""
    # 1. Try reading as modern Excel (openpyxl)
    try:
        return pd.read_excel(file_path, engine="openpyxl")
    except Exception:
        pass

    # 2. Try reading as legacy Excel (xlrd)
    try:
        return pd.read_excel(file_path, engine="xlrd")
    except Exception:
        pass

    # 3. Many web systems export HTML tables disguised as .xls or .xlsx
    try:
        tables = pd.read_html(file_path)
        if tables:
            return tables[0]
    except Exception:
        pass

    # 4. Try reading as CSV or TSV with sniffed delimiter
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            sample = f.read(4096)
            dialect = csv.Sniffer().sniff(sample)
            f.seek(0)
            return pd.read_csv(f, dialect=dialect)
    except Exception:
        pass

    return None

def dataframe_to_markdown(df: pd.DataFrame) -> str:
    """Converts a pandas DataFrame cleanly to Markdown table."""
    # Drop entirely empty rows and columns
    cleaned_df = df.dropna(how="all").dropna(axis=1, how="all")
    return cleaned_df.to_markdown(index=False)

