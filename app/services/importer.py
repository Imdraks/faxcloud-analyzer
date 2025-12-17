import csv
import hashlib
import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import yaml
from fastapi import HTTPException

from app.core.settings import settings

logger = logging.getLogger(__name__)


class ImportErrorDetail(HTTPException):
    def __init__(self, message: str):
        super().__init__(status_code=400, detail=message)


class ColumnMapper:
    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        with open(self.config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def map_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        required = {"sent_at", "status", "recipient"}
        aliases = self.config.get("aliases", {})
        renamed = {}
        lower_cols = {c.lower(): c for c in df.columns}

        for canonical, synonyms in aliases.items():
            for name in [canonical] + synonyms:
                key = name.lower()
                if key in lower_cols:
                    renamed[lower_cols[key]] = canonical
                    break

        df = df.rename(columns=renamed)
        missing = [col for col in required if col not in df.columns]
        if missing:
            raise ImportErrorDetail(f"Colonnes essentielles manquantes: {', '.join(missing)}")
        return df


class FileImporterService:
    SUPPORTED_EXT = {".csv", ".xlsx", ".xls"}

    def __init__(self):
        self.mapper = ColumnMapper(settings.columns_config)

    def compute_checksum(self, file_path: Path) -> str:
        h = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()

    def save_original(self, temp_path: Path, report_id: str, ext: str) -> Path:
        dest_dir = settings.uploads_dir / report_id
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / f"original{ext}"
        shutil.copy2(temp_path, dest)
        return dest

    def load_dataframe(self, file_path: Path) -> pd.DataFrame:
        ext = file_path.suffix.lower()
        if ext not in self.SUPPORTED_EXT:
            raise ImportErrorDetail("Format non supporté (CSV/XLSX)")
        if ext == ".csv":
            return pd.read_csv(file_path, dtype=str, keep_default_na=False, sep=None, engine="python")
        return pd.read_excel(file_path, dtype=str, keep_default_na=False)

    def normalize_row(self, row: pd.Series) -> Dict[str, Any]:
        def opt_int(value: Any) -> Optional[int]:
            try:
                return int(float(value)) if value != "" else None
            except (TypeError, ValueError):
                return None

        sent_at_raw = row.get("sent_at", "")
        sent_at = None
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M"):
            try:
                sent_at = datetime.strptime(sent_at_raw, fmt)
                break
            except (ValueError, TypeError):
                continue
        if not sent_at:
            raise ImportErrorDetail(f"Date invalide: {sent_at_raw}")

        return {
            "sent_at": sent_at,
            "recipient": row.get("recipient", ""),
            "sender": row.get("sender") or None,
            "status": row.get("status", "").lower(),
            "status_code": row.get("status_code") or None,
            "error_code": row.get("error_code") or None,
            "pages": opt_int(row.get("pages")),
            "duration_seconds": opt_int(row.get("duration_seconds")),
            "raw_row": json.dumps(row.to_dict(), ensure_ascii=False),
        }

    def import_file(self, temp_path: Path) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        df = self.load_dataframe(temp_path)
        df = self.mapper.map_columns(df)

        rows: List[Dict[str, Any]] = []
        for _, row in df.iterrows():
            try:
                rows.append(self.normalize_row(row))
            except ImportErrorDetail as e:
                logger.warning("Ligne rejetée: %s", e.detail)
                continue

        if not rows:
            raise ImportErrorDetail("Aucune ligne valide après import")

        return rows, {"rows": len(rows), "columns": list(df.columns)}
