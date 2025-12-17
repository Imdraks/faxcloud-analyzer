from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path


DEBUG = False


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
    default_base_url: str = "https://faxcloud-analyzer.local/reports"


def _build_settings() -> Settings:
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


def configure_logging(level: int = logging.INFO) -> None:
    ensure_directories()
    log_file = settings.logs_dir / "analyzer.log"
    root_logger = logging.getLogger()
    if root_logger.handlers:
        root_logger.setLevel(level)
        return

    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
    )
