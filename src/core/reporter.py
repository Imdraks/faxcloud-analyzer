from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

import qrcode

from .config import settings, ensure_directories

logger = logging.getLogger(__name__)


def generate_qr_code(report_id: str, base_url: Optional[str] = None) -> str:
    ensure_directories()
    base_url = base_url or settings.default_base_url
    url = f"{base_url}/{report_id}"
    qr_path = settings.reports_qr_dir / f"{report_id}.png"
    img = qrcode.make(url)
    img.save(qr_path)
    logger.info("QR code généré: %s", qr_path)
    return str(qr_path)


def _write_report(report: Dict) -> str:
    ensure_directories()
    path = settings.reports_dir / f"{report['report_id']}.json"
    with path.open("w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    logger.info("Rapport sauvegardé: %s", path)
    return str(path)


def generate_report(analysis: Dict, include_qr: bool = True) -> Dict:
    report = dict(analysis)
    qr_path = generate_qr_code(report["report_id"]) if include_qr else None
    report["qr_path"] = qr_path
    report["url_rapport"] = f"{settings.default_base_url}/{report['report_id']}"
    _write_report(report)
    return report


def list_report_files() -> List[str]:
    ensure_directories()
    return sorted(str(path) for path in settings.reports_dir.glob("*.json"))
