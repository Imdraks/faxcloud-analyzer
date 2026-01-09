from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from pathlib import Path
import sys

# Application version
__version__ = "1.2.0"

DEBUG = os.environ.get("DEBUG", "").lower() in ("1", "true", "yes")


@dataclass(frozen=True)
class Settings:
    """
    Centralized configuration for filesystem locations and defaults.
    """

    base_dir: Path
    data_dir: Path
    imports_dir: Path
    reports_dir: Path
    reports_qr_dir: Path
    logs_dir: Path
    database_path: Path
    default_base_url: str = os.environ.get("BASE_URL", "https://faxcloud-analyzer.local/reports")
    max_upload_size_mb: int = int(os.environ.get("MAX_UPLOAD_SIZE_MB", "100"))
    log_level: str = os.environ.get("LOG_LEVEL", "INFO")


def _build_settings() -> Settings:
    if getattr(sys, "frozen", False):
        # Running as a packaged executable (PyInstaller): keep data next to the EXE.
        project_root = Path(sys.executable).resolve().parent
    else:
        project_root = Path(__file__).resolve().parents[2]
    data_dir = project_root / "data"
    return Settings(
        base_dir=project_root,
        data_dir=data_dir,
        imports_dir=data_dir / "imports",
        reports_dir=data_dir / "reports",
        reports_qr_dir=data_dir / "reports_qr",
        logs_dir=project_root / "logs",
        database_path=project_root / "database" / "faxcloud.db",
    )


settings = _build_settings()


def set_debug_mode(enabled: bool) -> None:
    """
    Enable or disable debug logging globally.
    """

    global DEBUG
    DEBUG = enabled
    level = logging.DEBUG if enabled else logging.INFO
    configure_logging(level)


def ensure_directories() -> None:
    """
    Create required directories if they are missing.
    """

    for path in [
        settings.data_dir,
        settings.imports_dir,
        settings.reports_dir,
        settings.reports_qr_dir,
        settings.logs_dir,
        settings.database_path.parent,
    ]:
        path.mkdir(parents=True, exist_ok=True)


def configure_logging(level: int | None = None) -> None:
    if level is None:
        level_str = settings.log_level.upper()
        level = getattr(logging, level_str, logging.INFO)
    
    ensure_directories()
    log_file = settings.logs_dir / "analyzer.log"
    root_logger = logging.getLogger()
    if root_logger.handlers:
        root_logger.setLevel(level)
        return

    # Improved log format with more details
    log_format = "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s"
    
    logging.basicConfig(
        level=level,
        format=log_format,
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )
