from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, List

import pandas as pd

logger = logging.getLogger(__name__)


REQUIRED_COLUMNS = {
    "Fax ID": "fax_id",
    "Utilisateur": "utilisateur",
    "Mode": "mode",
    "Date/Heure": "datetime",
    "Numéro envoi": "numero_envoi",
    "Numéro appelé": "numero_appele",
    "Pages": "pages",
}


def _read_file(file_path: Path) -> pd.DataFrame:
    if file_path.suffix.lower() in {".xlsx", ".xls"}:
        return pd.read_excel(file_path)
    return pd.read_csv(file_path, sep=None, engine="python")


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    columns_map = {col: REQUIRED_COLUMNS[col] for col in REQUIRED_COLUMNS if col in df.columns}
    missing = set(REQUIRED_COLUMNS.keys()) - set(columns_map.keys())
    if missing:
        raise ValueError(f"Colonnes manquantes dans le fichier: {', '.join(sorted(missing))}")
    return df.rename(columns=columns_map)


def import_faxcloud_export(file_path: str) -> List[Dict]:
    """
    Import CSV/XLSX data and return a list of dictionaries ready for analysis.
    """

    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Fichier introuvable: {file_path}")

    logger.info("Lecture du fichier %s", path)
    df = _read_file(path)
    df = _normalize_columns(df)
    df["pages"] = pd.to_numeric(df["pages"], errors="coerce").fillna(0).astype(int)
    records = df.to_dict(orient="records")
    logger.info("Import terminé: %s lignes", len(records))
    return records
