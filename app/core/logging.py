import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from app.core.settings import settings


def setup_logging() -> None:
    log_file = Path(settings.logs_dir) / "app.log"
    log_file.parent.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s", "%Y-%m-%d %H:%M:%S"
    )

    file_handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=3)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(settings.log_level)
    root.addHandler(file_handler)
    root.addHandler(console_handler)
