"""
Module de gestion de la base de données SQLite / MySQL
Gère la création, l'initialisation et les opérations CRUD
"""

import sqlite3
import json
import logging
from datetime import datetime
from uuid import UUID
from typing import Optional, List, Dict, Any
from pathlib import Path

from .config import Config, DATABASE_TYPE

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════
# SCHÉMA DE BASE DE DONNÉES
# ═══════════════════════════════════════════════════════════════════════════

SCHEMA = """
-- Table des rapports
CREATE TABLE IF NOT EXISTS reports (
    id TEXT PRIMARY KEY,
    date_rapport TIMESTAMP NOT NULL,
    contract_id TEXT NOT NULL,
    date_debut DATE NOT NULL,
    date_fin DATE NOT NULL,
    fichier_source TEXT NOT NULL,
    
    total_fax INTEGER NOT NULL DEFAULT 0,
    fax_envoyes INTEGER NOT NULL DEFAULT 0,
    fax_recus INTEGER NOT NULL DEFAULT 0,
    pages_totales INTEGER NOT NULL DEFAULT 0,
    pages_envoyees INTEGER NOT NULL DEFAULT 0,
    pages_recues INTEGER NOT NULL DEFAULT 0,
    
    erreurs_totales INTEGER NOT NULL DEFAULT 0,
    taux_reussite REAL NOT NULL DEFAULT 0.0,
    
    qr_path TEXT,
    url_rapport TEXT,
    
    donnees_json TEXT NOT NULL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des entrées FAX
CREATE TABLE IF NOT EXISTS fax_entries (
    id TEXT PRIMARY KEY,
    report_id TEXT NOT NULL,
    
    fax_id TEXT NOT NULL,
    utilisateur TEXT NOT NULL,
    mode TEXT NOT NULL,
    date_heure TIMESTAMP,
    numero_original TEXT,
    numero_normalise TEXT,
    pages INTEGER,
    
    valide BOOLEAN NOT NULL DEFAULT 1,
    erreurs TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (report_id) REFERENCES reports(id)
);

-- Table d'historique des analyses
CREATE TABLE IF NOT EXISTS analysis_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id TEXT NOT NULL,
    fichier_source TEXT NOT NULL,
    date_analyse TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    statut TEXT NOT NULL,
    message TEXT,
    FOREIGN KEY (report_id) REFERENCES reports(id)
);

-- Index pour optimiser les requêtes
CREATE INDEX IF NOT EXISTS idx_reports_date ON reports(date_rapport DESC);
CREATE INDEX IF NOT EXISTS idx_reports_contract ON reports(contract_id);
CREATE INDEX IF NOT EXISTS idx_fax_entries_report ON fax_entries(report_id);
CREATE INDEX IF NOT EXISTS idx_fax_entries_valide ON fax_entries(valide);
CREATE INDEX IF NOT EXISTS idx_analysis_report ON analysis_history(report_id);
"""

# ═══════════════════════════════════════════════════════════════════════════
# CLASSE DATABASE
# ═══════════════════════════════════════════════════════════════════════════

class Database:
    """Gestionnaire de base de données (SQLite ou MySQL selon la config)"""
    
    def __new__(cls, db_path: Optional[str] = None):
        """Factory pattern pour retourner la bonne classe de DB"""
        if DATABASE_TYPE == 'mysql':
            from .db_mysql import DatabaseMySQL
            logger.info(f"Utilisation de MySQL: {Config.DATABASE_CONFIG['host']}:{Config.DATABASE_CONFIG.get('port', 3306)}")
            return DatabaseMySQL(Config.DATABASE_CONFIG)
        else:
            # SQLite
            logger.info(f"Utilisation de SQLite: {Config.DATABASE_CONFIG['path']}")
            return super().__new__(cls)
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialise la connexion à la base de données SQLite"""
        if db_path is None:
            db_path = Config.DATABASE_CONFIG['path']
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Initialisation de la base de données: {self.db_path}")
    
    def get_connection(self) -> sqlite3.Connection:
        """Retourne une connexion à la base de données"""
        try:
            conn = sqlite3.connect(
                str(self.db_path),
                timeout=Config.DATABASE_CONFIG['timeout'],
                check_same_thread=Config.DATABASE_CONFIG['check_same_thread']
            )
            conn.row_factory = sqlite3.Row
            return conn
        except sqlite3.Error as e:
            logger.error(f"Erreur de connexion à la base: {e}")
            raise
    
    def initialize(self) -> None:
        """Crée les tables de la base de données"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Exécuter le schéma
            cursor.executescript(SCHEMA)
            
            conn.commit()
            logger.info("Base de données initialisée avec succès")
        except sqlite3.Error as e:
            logger.error(f"Erreur lors de l'initialisation: {e}")
            raise
        finally:
            conn.close()
    
    # ═════════════════════════════════════════════════════════════════════
    # OPÉRATIONS SUR LES RAPPORTS
    # ═════════════════════════════════════════════════════════════════════
    
    def save_report(self, report_data: Dict[str, Any]) -> str:
        """Sauvegarde un rapport complet dans la base"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Insérer le rapport
            cursor.execute("""
                INSERT INTO reports (
                    id, date_rapport, contract_id, date_debut, date_fin,
                    fichier_source, total_fax, fax_envoyes, fax_recus,
                    pages_totales, pages_envoyees, pages_recues,
                    erreurs_totales, taux_reussite, qr_path, url_rapport,
                    donnees_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                report_data['rapport_id'],
                report_data['timestamp'],
                report_data['contract_id'],
                report_data.get('date_debut', ''),
                report_data.get('date_fin', ''),
                report_data.get('fichier_source', ''),
                report_data['statistics']['total_fax'],
                report_data['statistics']['fax_envoyes'],
                report_data['statistics']['fax_recus'],
                report_data['statistics']['pages_totales'],
                report_data['statistics'].get('pages_envoyees', 0),
                report_data['statistics'].get('pages_recues', 0),
                report_data['statistics']['erreurs_totales'],
                report_data['statistics']['taux_reussite'],
                report_data.get('qr_path'),
                report_data.get('report_url'),
                json.dumps(report_data, default=str, ensure_ascii=False)
            ))
            
            # Insérer les entrées FAX
            for entry in report_data.get('entries', []):
                self.save_fax_entry(cursor, report_data['rapport_id'], entry)
            
            conn.commit()
            logger.info(f"Rapport {report_data['rapport_id']} sauvegardé")
            return report_data['rapport_id']
        
        except sqlite3.Error as e:
            logger.error(f"Erreur lors de la sauvegarde du rapport: {e}")
            raise
        finally:
            conn.close()
    
    def save_fax_entry(self, cursor: sqlite3.Cursor, report_id: str, entry: Dict[str, Any]) -> None:
        """Sauvegarde une entrée FAX"""
        from uuid import uuid4
        
        cursor.execute("""
            INSERT INTO fax_entries (
                id, report_id, fax_id, utilisateur, mode, date_heure,
                numero_original, numero_normalise, pages, valide, erreurs
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            str(uuid4()),
            report_id,
            entry.get('fax_id', ''),
            entry.get('utilisateur', ''),
            entry.get('mode', ''),
            entry.get('date_heure'),
            entry.get('numero_original'),
            entry.get('numero_normalise'),
            entry.get('pages'),
            1 if entry.get('valide', True) else 0,
            json.dumps(entry.get('erreurs', []))
        ))
    
    def get_report(self, report_id: str) -> Optional[Dict[str, Any]]:
        """Récupère un rapport par ID"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT donnees_json FROM reports WHERE id = ?", (report_id,))
            row = cursor.fetchone()
            
            if row:
                return json.loads(row[0])
            return None
        
        except sqlite3.Error as e:
            logger.error(f"Erreur lors de la lecture du rapport: {e}")
            return None
        finally:
            conn.close()
    
    def list_reports(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Liste tous les rapports"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, date_rapport, contract_id, total_fax, 
                       fax_envoyes, fax_recus, erreurs_totales, taux_reussite
                FROM reports
                ORDER BY date_rapport DESC
                LIMIT ? OFFSET ?
            """, (limit, offset))
            
            reports = []
            for row in cursor.fetchall():
                reports.append({
                    'id': row[0],
                    'date_rapport': row[1],
                    'contract_id': row[2],
                    'total_fax': row[3],
                    'fax_envoyes': row[4],
                    'fax_recus': row[5],
                    'erreurs': row[6],
                    'taux_reussite': row[7]
                })
            
            return reports
        
        except sqlite3.Error as e:
            logger.error(f"Erreur lors de la liste des rapports: {e}")
            return []
        finally:
            conn.close()
    
    def get_report(self, report_id: str) -> Optional[Dict[str, Any]]:
        """Récupère un rapport complet depuis la BDD"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, date_rapport, contract_id, date_debut, date_fin,
                       fichier_source, donnees_json, qr_path, url_rapport
                FROM reports
                WHERE id = ?
            """, (report_id,))
            
            row = cursor.fetchone()
            
            if not row:
                return None
            
            # Charger le JSON stocké
            report_data = json.loads(row[6])
            
            # Ajouter les chemins si disponibles
            if row[7]:
                report_data['qr_path'] = row[7]
            if row[8]:
                report_data['report_url'] = row[8]
            
            return report_data
        
        except sqlite3.Error as e:
            logger.error(f"Erreur lors de la lecture du rapport: {e}")
            return None
        finally:
            conn.close()
    
    def get_fax_entries(self, report_id: str, only_errors: bool = False) -> List[Dict[str, Any]]:
        """Récupère les entrées FAX d'un rapport"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            where_clause = "WHERE report_id = ?"
            params = [report_id]
            
            if only_errors:
                where_clause += " AND valide = 0"
            
            cursor.execute(f"""
                SELECT id, fax_id, utilisateur, mode, date_heure,
                       numero_original, numero_normalise, pages, valide, erreurs
                FROM fax_entries
                {where_clause}
                ORDER BY date_heure
            """, params)
            
            entries = []
            for row in cursor.fetchall():
                entries.append({
                    'id': row[0],
                    'fax_id': row[1],
                    'utilisateur': row[2],
                    'mode': row[3],
                    'date_heure': row[4],
                    'numero_original': row[5],
                    'numero_normalise': row[6],
                    'pages': row[7],
                    'valide': bool(row[8]),
                    'erreurs': json.loads(row[9]) if row[9] else []
                })
            
            return entries
        
        except sqlite3.Error as e:
            logger.error(f"Erreur lors de la lecture des entrées FAX: {e}")
            return []
        finally:
            conn.close()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques globales"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Compter les rapports et statistiques
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_rapports,
                    SUM(total_fax) as total_fax_global,
                    SUM(erreurs_totales) as total_erreurs,
                    AVG(taux_reussite) as taux_reussite_moyen,
                    COUNT(DISTINCT contract_id) as clients_uniques
                FROM reports
            """)
            
            row = cursor.fetchone()
            
            return {
                'total_reports': row[0] or 0,
                'total_fax': row[1] or 0,
                'total_errors': row[2] or 0,
                'avg_success_rate': round(row[3] or 0, 2),
                'unique_clients': row[4] or 0
            }
        
        except sqlite3.Error as e:
            logger.error(f"Erreur lors du calcul des statistiques: {e}")
            return {}
        finally:
            conn.close()
