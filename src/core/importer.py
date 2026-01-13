from __future__ import annotations

import logging
import re
import unicodedata
from pathlib import Path
from typing import Dict, List

import pandas as pd

logger = logging.getLogger(__name__)


TARGET_COLUMNS = (
    "fax_id",
    "utilisateur",
    "mode",
    "datetime",
    "numero_envoi",
    "numero_appele",
    "pages",
)


def _canonicalize_column_name(name: str) -> str:
    text = str(name or "").strip().lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.replace("'", " ")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


COLUMN_ALIASES: Dict[str, List[str]] = {
    "fax_id": [
        "fax id",
        "faxid",
        "id fax",
    ],
    "utilisateur": [
        "utilisateur",
        "nom et prenom utilisateur",
        "nom et prenom",
        "nom prenom utilisateur",
        "nom prenom",
        "user",
    ],
    "mode": [
        "mode",
        "type",
        "type fax",
    ],
    "datetime": [
        "date heure",
        "date heure du fax",
        "date et heure",
        "date et heure du fax",
        "date/heure",
    ],
    "numero_envoi": [
        "numero envoi",
        "numero d envoi",
        "numero d'envoi",
        "numero d envoi",
        "numero d envoie",
    ],
    "numero_appele": [
        "numero appele",
        "numero appele",
        "numero appele",
        "numero appel",
        "numero appelee",
    ],
    "pages": [
        "nombre de page reel",
        "nombre de page real",
        "nombre de pages",
        "pages",
        "pages facturees",
        "pages facturee",
    ],
}


def _read_file(file_path: Path) -> pd.DataFrame:
    if file_path.suffix.lower() in {".xlsx", ".xls"}:
        return pd.read_excel(file_path)
    
    # Essayer différents encodings pour CSV
    encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
    for encoding in encodings:
        try:
            # FaxCloud exports are often ';' separated. sep=None will sniff, but ';' is common.
            return pd.read_csv(file_path, sep=None, engine="python", encoding=encoding)
        except (UnicodeDecodeError, LookupError):
            continue
    
    # Fallback: charger sans encoder spécifique (pandas gérera)
    return pd.read_csv(file_path, sep=None, engine="python", encoding='utf-8', errors='replace')


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    # Map canonical name -> original column name
    canonical_to_original: Dict[str, str] = {}
    for col in df.columns:
        canonical_to_original[_canonicalize_column_name(col)] = col

    rename_map: Dict[str, str] = {}
    missing_targets: List[str] = []
    for target in TARGET_COLUMNS:
        aliases = COLUMN_ALIASES.get(target, [])
        found_original = None
        for alias in aliases:
            key = _canonicalize_column_name(alias)
            if key in canonical_to_original:
                found_original = canonical_to_original[key]
                break
        if not found_original:
            missing_targets.append(target)
            continue
        rename_map[found_original] = target

    if missing_targets:
        found = ", ".join(map(str, df.columns))
        missing = ", ".join(missing_targets)
        raise ValueError(
            "Colonnes manquantes dans le fichier: "
            + missing
            + ". Colonnes trouvées: "
            + found
        )

    return df.rename(columns=rename_map)


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
