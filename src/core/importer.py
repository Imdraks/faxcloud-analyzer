"""
Importation - Lecture CSV/XLSX FaxCloud
"""
import logging
from pathlib import Path
from typing import Dict, List
import pandas as pd
import config

logger = logging.getLogger(__name__)


def import_faxcloud_export(file_path: str) -> Dict:
    """Import FaxCloud CSV/XLSX and normalize to 14 columns (0-13)"""
    try:
        logger.info("=" * 70)
        logger.info("IMPORT FAXCLOUD")
        logger.info("=" * 70)
        
        file_path = Path(file_path)
        if not file_path.exists():
            logger.error(f"Fichier non trouve: {file_path}")
            return {"success": False, "rows": [], "count": 0, "message": "Fichier non trouve"}
        
        logger.info(f"Fichier: {file_path.name}")
        
        # Detecter format
        ext = file_path.suffix.lower()
        if ext not in ['.csv', '.xlsx', '.xls']:
            logger.error("Format non reconnu")
            return {"success": False, "rows": [], "count": 0, "message": "Format non reconnu"}
        
        file_format = 'csv' if ext == '.csv' else 'xlsx'
        logger.info(f"Format: {file_format.upper()}")
        
        # Lire le fichier
        df = None
        if file_format == 'csv':
            for sep in [';', ',', '\t']:
                try:
                    df = pd.read_csv(file_path, sep=sep, dtype=str, keep_default_na=False, 
                                    na_values=[], on_bad_lines='skip', encoding='utf-8')
                    logger.info(f"CSV lu avec separateur '{sep}'")
                    break
                except:
                    try:
                        df = pd.read_csv(file_path, sep=sep, dtype=str, keep_default_na=False,
                                        na_values=[], on_bad_lines='skip', encoding='latin-1')
                        logger.info(f"CSV lu (latin-1) avec separateur '{sep}'")
                        break
                    except:
                        continue
        else:
            try:
                df = pd.read_excel(file_path, dtype=str, keep_default_na=False, na_values=[])
                logger.info("XLSX lu")
            except Exception as e:
                logger.error(f"Erreur XLSX: {e}")
                return {"success": False, "rows": [], "count": 0, "message": str(e)}
        
        if df is None or df.empty:
            logger.error("Fichier vide ou illisible")
            return {"success": False, "rows": [], "count": 0, "message": "Fichier vide"}
        
        logger.info(f"Fichier lu: {len(df)} lignes, {len(df.columns)} colonnes")
        
        # Verifier 14 colonnes minimum
        if len(df.columns) < 14:
            logger.error(f"Colonnes insuffisantes: {len(df.columns)}")
            return {"success": False, "rows": [], "count": 0, "message": f"Besoin 14 colonnes, trouve {len(df.columns)}"}
        
        # Normaliser
        rows = []
        for idx, row in df.iterrows():
            normalized = {}
            for col_idx in range(14):
                val = str(row.iloc[col_idx]) if pd.notna(row.iloc[col_idx]) else ""
                normalized[col_idx] = val.strip()
            rows.append(normalized)
        
        logger.info(f"REUSSI: {len(rows)} lignes")
        logger.info("=" * 70)
        
        return {"success": True, "rows": rows, "count": len(rows), "message": f"Import OK: {len(rows)} lignes"}
    
    except Exception as e:
        logger.error(f"Erreur: {e}")
        return {"success": False, "rows": [], "count": 0, "message": str(e)}
