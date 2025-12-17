"""
Configuration centralisée de FaxCloud Analyzer
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ========== ENVIRONNEMENT ==========
DEBUG = os.getenv('FLASK_DEBUG', True)
ENVIRONMENT = os.getenv('FLASK_ENV', 'development')

# ========== BASE DE DONNÉES ==========
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', 3306))
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_NAME = os.getenv('DB_NAME', 'faxcloud_db')

SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# ========== FLASK ==========
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-prod')
JSON_SORT_KEYS = False

# ========== UPLOAD ==========
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'data', 'uploads')
ALLOWED_EXTENSIONS = {'csv', 'xlsx'}
MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB

# ========== LOGGING ==========
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.path.join(os.path.dirname(__file__), '..', 'logs', 'app.log')

# ========== NGROK (OPTIONNEL) ==========
NGROK_ENABLED = os.getenv('NGROK_ENABLED', 'false').lower() == 'true'
NGROK_AUTHTOKEN = os.getenv('NGROK_AUTHTOKEN', '')

# Créer dossiers s'ils n'existent pas
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
