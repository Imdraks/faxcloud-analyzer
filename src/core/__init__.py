"""
FaxCloud Analyzer core package.

This module exposes helper functions to keep import paths concise for the CLI.
"""

from .config import settings
from .db import (
    get_all_reports,
    get_report_by_id,
    init_database,
    insert_report_to_db,
)
from .importer import import_faxcloud_export
from .analyzer import analyze_data
from .reporter import generate_qr_code, generate_report, list_report_files
from src.server import create_app

__all__ = [
    "analyze_data",
    "generate_qr_code",
    "generate_report",
    "get_all_reports",
    "get_report_by_id",
    "import_faxcloud_export",
    "init_database",
    "insert_report_to_db",
    "list_report_files",
    "settings",
    "create_app",
]
