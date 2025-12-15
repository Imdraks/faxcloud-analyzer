"""
Configuration centralisée du projet FaxCloud Analyzer
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any
from datetime import datetime
from dotenv import load_dotenv

# Charger les variables d'environnement du fichier .env
load_dotenv(Path(__file__).parent.parent.parent / '.env')

# ═══════════════════════════════════════════════════════════════════════════
# CHEMINS ET RÉPERTOIRES
# ═══════════════════════════════════════════════════════════════════════════

PROJECT_ROOT = Path(__file__).parent.parent.parent
SRC_DIR = PROJECT_ROOT / "src"
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"
DOCS_DIR = PROJECT_ROOT / "docs"

# Sous-répertoires DATA
IMPORTS_DIR = DATA_DIR / "imports"
REPORTS_DIR = DATA_DIR / "reports"
REPORTS_QR_DIR = DATA_DIR / "reports_qr"
DATABASE_DIR = DATA_DIR / "database"

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION BASE DE DONNÉES
# ═══════════════════════════════════════════════════════════════════════════

# Type de BDD: 'mysql' ou 'sqlite'
DATABASE_TYPE = os.getenv('DATABASE_TYPE', 'mysql')

if DATABASE_TYPE == 'mysql':
    # Configuration MySQL (WampServer/phpMyAdmin)
    DATABASE_CONFIG = {
        "type": "mysql",
        "host": os.getenv('DB_HOST', 'localhost'),
        "port": int(os.getenv('DB_PORT', 3306)),
        "user": os.getenv('DB_USER', 'root'),
        "password": os.getenv('DB_PASSWORD', ''),
        "database": os.getenv('DB_NAME', 'faxcloud_analyzer'),
        "charset": 'utf8mb4',
        "autocommit": True
    }
else:
    # Configuration SQLite (fallback)
    DATABASE_PATH = DATABASE_DIR / "faxcloud.db"
    DATABASE_CONFIG = {
        "type": "sqlite",
        "path": str(DATABASE_PATH),
        "timeout": 5.0,
        "check_same_thread": False
    }

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION LOGGING
# ═══════════════════════════════════════════════════════════════════════════

LOG_FILE = LOGS_DIR / "faxcloud_analyzer.log"
LOG_LEVEL = logging.INFO

LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "[%(asctime)s] %(name)s - %(levelname)s - %(message)s"
        },
        "detailed": {
            "format": "[%(asctime)s] %(name)s:%(lineno)d - %(levelname)s - %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "standard",
            "stream": "ext://sys.stdout"
        },
        "file": {
            "class": "logging.FileHandler",
            "level": "DEBUG",
            "formatter": "detailed",
            "filename": str(LOG_FILE)
        }
    },
    "root": {
        "level": "DEBUG",
        "handlers": ["console", "file"]
    }
}

# ═══════════════════════════════════════════════════════════════════════════
# RÈGLES D'ANALYSE
# ═══════════════════════════════════════════════════════════════════════════

# Colonnes attendues du fichier CSV/XLSX (par index)
EXPECTED_COLUMNS = {
    'fax_id': 0,              # Colonne A
    'utilisateur': 1,         # Colonne B
    'mode': 3,                # Colonne D
    'date_heure': 5,          # Colonne F
    'numero': 7,              # Colonne H
    'pages': 10               # Colonne K
}

# Types de fax valides
VALID_FAX_MODES = {
    'SF': 'Envoyé',
    'RF': 'Reçu'
}

# Règles de validation des numéros
NUMBER_VALIDATION_RULES = {
    'min_length': 11,
    'max_length': 11,
    'required_prefix': '33',
    'allow_empty': False,
    'require_numeric': True
}

# Types d'erreurs
ERROR_TYPES = {
    'ERR_001': "Numéro vide",
    'ERR_002': "Format de numéro illisible (caractères invalides)",
    'ERR_003': "Nombre de chiffres incorrect (doit être 11)",
    'ERR_004': "Indicatif incorrect (doit commencer par 33)",
    'ERR_005': "Nombre de pages invalide (doit être >= 1)",
    'ERR_006': "Mode de fax invalide (doit être SF ou RF)",
    'ERR_007': "Date/heure manquante ou invalide",
    'ERR_008': "Utilisateur non renseigné",
    'ERR_099': "Erreur inconnue"
}

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION WEB
# ═══════════════════════════════════════════════════════════════════════════

FLASK_CONFIG = {
    "DEBUG": False,
    "HOST": "127.0.0.1",
    "PORT": 5000,
    "TEMPLATES_AUTO_RELOAD": True,
    "JSON_SORT_KEYS": False
}

# URL de base pour les rapports (via QR code)
BASE_REPORT_URL = "http://localhost:5000/report"

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION QR CODE
# ═══════════════════════════════════════════════════════════════════════════

QR_CODE_CONFIG = {
    "version": 1,
    "error_correction": "M",
    "box_size": 10,
    "border": 2
}

# ═══════════════════════════════════════════════════════════════════════════
# CLASSE DE CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

class Config:
    """Configuration centralisée et méthodes utilitaires"""
    
    # Chemins
    PROJECT_ROOT = PROJECT_ROOT
    SRC_DIR = SRC_DIR
    DATA_DIR = DATA_DIR
    LOGS_DIR = LOGS_DIR
    IMPORTS_DIR = IMPORTS_DIR
    REPORTS_DIR = REPORTS_DIR
    REPORTS_QR_DIR = REPORTS_QR_DIR
    DATABASE_DIR = DATABASE_DIR
    
    # Configs
    DATABASE_CONFIG = DATABASE_CONFIG
    LOG_CONFIG = LOG_CONFIG
    FLASK_CONFIG = FLASK_CONFIG
    QR_CODE_CONFIG = QR_CODE_CONFIG
    EXPECTED_COLUMNS = EXPECTED_COLUMNS
    VALID_FAX_MODES = VALID_FAX_MODES
    NUMBER_VALIDATION_RULES = NUMBER_VALIDATION_RULES
    ERROR_TYPES = ERROR_TYPES
    BASE_REPORT_URL = BASE_REPORT_URL
    USE_NGROK = os.getenv('USE_NGROK', 'false').lower() == 'true'
    
    @staticmethod
    def ensure_directories() -> None:
        """Crée tous les répertoires nécessaires s'ils n'existent pas"""
        dirs_to_create = [
            LOGS_DIR,
            IMPORTS_DIR,
            REPORTS_DIR,
            REPORTS_QR_DIR,
            DATABASE_DIR
        ]
        
        for dir_path in dirs_to_create:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """Retourne un logger configuré"""
        return logging.getLogger(name)
    
    @staticmethod
    def setup_logging() -> None:
        """Configure le système de logging"""
        import logging.config
        
        Config.ensure_directories()
        
        # Créer le fichier log s'il n'existe pas
        LOG_FILE.touch(exist_ok=True)
        
        logging.config.dictConfig(LOG_CONFIG)
    
    @staticmethod
    def to_dict() -> Dict[str, Any]:
        """Retourne la configuration sous forme de dictionnaire"""
        return {
            "database": DATABASE_CONFIG,
            "flask": FLASK_CONFIG,
            "qr_code": QR_CODE_CONFIG,
            "validation_rules": {
                "fax_modes": VALID_FAX_MODES,
                "number_rules": NUMBER_VALIDATION_RULES,
                "error_types": ERROR_TYPES
            },
            "paths": {
                "project_root": str(PROJECT_ROOT),
                "data": str(DATA_DIR),
                "reports": str(REPORTS_DIR),
                "qr_codes": str(REPORTS_QR_DIR),
                "database": str(DATABASE_DIR),
                "logs": str(LOGS_DIR)
            }
        }
