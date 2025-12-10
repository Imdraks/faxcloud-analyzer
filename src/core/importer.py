"""
Module d'importation des fichiers FaxCloud (CSV/XLSX)
Responsabilités:
- Lecture des fichiers CSV et XLSX
- Validation de la structure
- Normalisation des données
"""

import pandas as pd
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import config

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════
# IMPORTATION
# ═══════════════════════════════════════════════════════════════════════════

def import_faxcloud_export(file_path: str) -> Dict:
    """
    Importe un fichier CSV ou XLSX FaxCloud
    
    Args:
        file_path: Chemin du fichier à importer
    
    Returns:
        {
            "success": bool,
            "rows": List[Dict],
            "total_rows": int,
            "errors": List[str],
            "message": str
        }
    """
    file_path = Path(file_path)
    
    # Vérifier l'existence du fichier
    if not file_path.exists():
        error_msg = f"Fichier non trouvé: {file_path}"
        logger.error(error_msg)
        return {
            "success": False,
            "rows": [],
            "total_rows": 0,
            "errors": [error_msg],
            "message": error_msg
        }
    
    # Vérifier l'extension
    suffix = file_path.suffix.lower()
    if suffix not in ['.csv', '.xlsx', '.xls']:
        error_msg = f"Format non supporté: {suffix}. Acceptés: {config.ACCEPTED_FORMATS}"
        logger.error(error_msg)
        return {
            "success": False,
            "rows": [],
            "total_rows": 0,
            "errors": [error_msg],
            "message": error_msg
        }
    
    try:
        # Lire le fichier
        logger.info(f"Lecture du fichier: {file_path}")
        
        if suffix == '.csv':
            df = pd.read_csv(file_path, sep=';', encoding='utf-8')
        else:  # .xlsx ou .xls
            df = pd.read_excel(file_path)
        
        logger.info(f"✓ Fichier chargé: {len(df)} lignes")
        
        # Valider les colonnes
        validation = validate_structure(df)
        if not validation['success']:
            logger.error(f"Structure invalide: {validation['errors']}")
            return {
                "success": False,
                "rows": [],
                "total_rows": 0,
                "errors": validation['errors'],
                "message": "Structure du fichier invalide"
            }
        
        # Normaliser les données
        rows = normalize_data(df)
        
        logger.info(f"✓ Importation réussie: {len(rows)} lignes valides")
        
        return {
            "success": True,
            "rows": rows,
            "total_rows": len(rows),
            "errors": [],
            "message": f"Importation réussie: {len(rows)} lignes"
        }
        
    except Exception as e:
        error_msg = f"Erreur lors de la lecture: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "rows": [],
            "total_rows": 0,
            "errors": [error_msg],
            "message": error_msg
        }


# ═══════════════════════════════════════════════════════════════════════════
# VALIDATION
# ═══════════════════════════════════════════════════════════════════════════

def validate_structure(df: pd.DataFrame) -> Dict:
    """
    Valide la structure du DataFrame
    Vérifie la présence des colonnes requises
    """
    errors = []
    
    # Colonnes requises (index)
    required_columns = ['A', 'B', 'D', 'F', 'G', 'H', 'K']
    
    # Vérifier le nombre minimum de colonnes
    if len(df.columns) < 14:
        errors.append(f"Nombre insuffisant de colonnes: {len(df.columns)} (minimum 14 attendues)")
    
    # Vérifier que les colonnes essentielles ont des données
    if df.empty:
        errors.append("Le fichier est vide")
    
    # Vérifier les colonnes clés
    try:
        # Accéder aux colonnes par index (0-based)
        # A=0, B=1, D=3, F=5, G=6, H=7, K=10
        _ = df.iloc[:, 0]  # A - Fax ID
        _ = df.iloc[:, 1]  # B - Utilisateur
        _ = df.iloc[:, 3]  # D - Mode
        _ = df.iloc[:, 5]  # F - DateTime
        _ = df.iloc[:, 6]  # G - Numéro envoi
        _ = df.iloc[:, 7]  # H - Numéro appelé
        _ = df.iloc[:, 10] # K - Pages
    except Exception as e:
        errors.append(f"Colonnes requises manquantes: {str(e)}")
    
    return {
        "success": len(errors) == 0,
        "errors": errors
    }


# ═══════════════════════════════════════════════════════════════════════════
# NORMALISATION
# ═══════════════════════════════════════════════════════════════════════════

def normalize_data(df: pd.DataFrame) -> List[Dict]:
    """
    Normalise les données du DataFrame
    Convertit en liste de dictionnaires avec types corrects
    """
    rows = []
    
    for idx, row in df.iterrows():
        try:
            # Extraire les colonnes (index 0-based)
            normalized_row = {
                'A': str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else '',     # Fax ID
                'B': str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else '',     # Utilisateur
                'C': str(row.iloc[2]).strip() if pd.notna(row.iloc[2]) else '',     # Revendeur
                'D': str(row.iloc[3]).strip().upper() if pd.notna(row.iloc[3]) else '', # Mode
                'E': str(row.iloc[4]).strip() if pd.notna(row.iloc[4]) else '',     # Email
                'F': normalize_datetime(row.iloc[5]) if pd.notna(row.iloc[5]) else '', # DateTime
                'G': str(row.iloc[6]).strip() if pd.notna(row.iloc[6]) else '',     # Numéro envoi
                'H': str(row.iloc[7]).strip() if pd.notna(row.iloc[7]) else '',     # Numéro appelé
                'I': str(row.iloc[8]).strip() if pd.notna(row.iloc[8]) else '',     # Appel intl
                'J': str(row.iloc[9]).strip() if pd.notna(row.iloc[9]) else '',     # Appel interne
                'K': int(row.iloc[10]) if pd.notna(row.iloc[10]) else 0,             # Pages
                'L': int(row.iloc[11]) if pd.notna(row.iloc[11]) else 0,             # Durée
                'M': int(row.iloc[12]) if pd.notna(row.iloc[12]) else 0,             # Pages facturées
                'N': str(row.iloc[13]).strip() if len(row) > 13 and pd.notna(row.iloc[13]) else ''  # Type facturation
            }
            
            # Ne garder que les lignes avec des données valides
            if normalized_row['A'] and normalized_row['D'] and normalized_row['H']:
                rows.append(normalized_row)
        
        except Exception as e:
            logger.warning(f"Erreur normalisation ligne {idx}: {str(e)}")
            continue
    
    return rows


def normalize_datetime(value) -> str:
    """
    Normalise une valeur de date/heure
    Retourne au format ISO 8601
    """
    try:
        if isinstance(value, str):
            # Essayer différents formats
            for fmt in ['%Y-%m-%d %H:%M:%S', '%d/%m/%Y %H:%M:%S', '%d-%m-%Y %H:%M:%S']:
                try:
                    dt = datetime.strptime(value, fmt)
                    return dt.isoformat()
                except:
                    continue
            # Si aucun format ne correspond, retourner la chaîne
            return str(value)
        else:
            # Si c'est un Timestamp pandas
            return pd.Timestamp(value).isoformat()
    except Exception as e:
        logger.warning(f"Erreur normalisation date: {str(e)}")
        return str(value)


# ═══════════════════════════════════════════════════════════════════════════
# UTILITAIRES
# ═══════════════════════════════════════════════════════════════════════════

def list_imports() -> List[Path]:
    """
    Liste tous les fichiers importés
    """
    import_dir = config.DIRS['imports']
    import_dir.mkdir(parents=True, exist_ok=True)
    
    files = list(import_dir.glob('*'))
    return files


def save_import(file_path: Path) -> Optional[Path]:
    """
    Sauvegarde un fichier importé
    """
    import_dir = config.DIRS['imports']
    import_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        destination = import_dir / file_path.name
        import shutil
        shutil.copy2(file_path, destination)
        logger.info(f"✓ Fichier sauvegardé: {destination}")
        return destination
    except Exception as e:
        logger.error(f"✗ Erreur sauvegarde fichier: {e}")
        return None


# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Exemple d'utilisation
    result = import_faxcloud_export("exports/example.csv")
    print(f"Résultat: {result['success']}")
    print(f"Lignes importées: {result['total_rows']}")
    if result['errors']:
        print(f"Erreurs: {result['errors']}")
