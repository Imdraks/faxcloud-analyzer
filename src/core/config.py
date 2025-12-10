# Configuration globale - FaxCloud Analyzer

import os
import logging
from pathlib import Path

# ═══════════════════════════════════════════════════════════════════════════
# 📁 CONFIGURATION DES CHEMINS
# ═══════════════════════════════════════════════════════════════════════════

# Racine du projet (remonte de src/core vers la racine)
PROJECT_ROOT = Path(__file__).parent.parent.parent.absolute()

# Dossiers principaux
DIRS = {
    'imports': PROJECT_ROOT / 'data' / 'imports',
    'reports_json': PROJECT_ROOT / 'data' / 'reports',
    'reports_qr': PROJECT_ROOT / 'data' / 'reports_qr',
    'exports': PROJECT_ROOT / 'exports',
    'database': PROJECT_ROOT / 'database',
    'web': PROJECT_ROOT / 'web',
    'logs': PROJECT_ROOT / 'logs'
}

# Chemin de la base de données SQLite
DATABASE_PATH = DIRS['database'] / 'faxcloud.db'

# ═══════════════════════════════════════════════════════════════════════════
# 🔧 CONFIGURATION DE L'APPLICATION
# ═══════════════════════════════════════════════════════════════════════════

# Web
WEB_HOST = "0.0.0.0"
WEB_PORT = 8000
BASE_URL = "http://localhost:8000"
REPORTS_BASE_URL = f"{BASE_URL}/reports"

# Logging
LOG_LEVEL = logging.INFO
LOG_FORMAT = "[%(asctime)s] %(levelname)s - %(name)s - %(message)s"
LOG_FILE = DIRS['logs'] / 'analyzer.log'

# Formats acceptés
ACCEPTED_FORMATS = ['csv', 'xlsx', 'xls']

# ═══════════════════════════════════════════════════════════════════════════
# 📊 CONFIGURATION D'ANALYSE
# ═══════════════════════════════════════════════════════════════════════════

# Règles de validation des numéros
VALIDATION_RULES = {
    'phone_length': 11,              # Longueur attendue après normalisation
    'country_code': '33',             # Code pays France
    'enable_asterisk': False,         # Validation Asterisk (futur)
}

# Colonnes CSV attendues (index)
CSV_COLUMNS = {
    'fax_id': 0,                      # A - Fax ID
    'utilisateur': 1,                 # B - Nom et prénom utilisateur
    'revendeur': 2,                   # C - Revendeur
    'mode': 3,                        # D - Mode (SF/RF)
    'email': 4,                       # E - Adresse de messagerie
    'datetime': 5,                    # F - Date et heure du fax
    'numero_envoi': 6,                # G - Numéro d'envoi
    'numero_appele': 7,               # H - Numéro appelé
    'appel_international': 8,         # I - Appel international
    'appel_interne': 9,               # J - Appel interne
    'pages_reelles': 10,              # K - Nombre de pages réel
    'duree': 11,                      # L - Durée
    'pages_facturees': 12,            # M - Pages facturées
    'type_facturation': 13            # N - Type facturation
}

# Types de FAX
FAX_TYPES = {
    'SF': 'send',                     # Send Fax
    'RF': 'receive'                   # Receive Fax
}

# ═══════════════════════════════════════════════════════════════════════════
# 📱 CONFIGURATION QR CODE
# ═══════════════════════════════════════════════════════════════════════════

QR_CONFIG = {
    'version': 1,                     # Taille minimale QR
    'error_correction': 'H',          # Haute correction d'erreur
    'box_size': 10,                   # Pixels par boîte QR
    'border': 4,                      # Pixels de bordure
    'fill_color': 'black',
    'back_color': 'white',
    'format': 'PNG'
}

# ═══════════════════════════════════════════════════════════════════════════
# 🗄️ CONFIGURATION BASE DE DONNÉES
# ═══════════════════════════════════════════════════════════════════════════

DB_CONFIG = {
    'echo': False,                    # Logs SQL
    'timeout': 30,                    # Timeout connexion
    'isolation_level': 'DEFERRED'
}

# ═══════════════════════════════════════════════════════════════════════════
# 🎯 FONCTION D'INITIALISATION
# ═══════════════════════════════════════════════════════════════════════════

def ensure_directories():
    """Créer tous les répertoires nécessaires"""
    for key, path in DIRS.items():
        path.mkdir(parents=True, exist_ok=True)
        print(f"✓ Répertoire {key}: {path}")

def setup_logging():
    """Configurer le logging"""
    ensure_directories()
    
    logging.basicConfig(
        level=LOG_LEVEL,
        format=LOG_FORMAT,
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler()
        ]
    )

# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("🔧 Configuration FaxCloud Analyzer")
    print(f"📁 Racine du projet: {PROJECT_ROOT}")
    print("\nRépertoires:")
    ensure_directories()
    print("\n✅ Configuration validée!")
