"""
Module de gestion de la base de données SQLite
Responsabilités:
- Initialisation de la base de données
- Insertion des rapports et entrées
- Consultation des données
"""

import sqlite3
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import config

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════
# INITIALISATION
# ═══════════════════════════════════════════════════════════════════════════

def init_database(db_path: Path = None) -> None:
    """
    Initialise la base de données SQLite
    Crée les tables si elles n'existent pas
    """
    if db_path is None:
        db_path = config.DATABASE_PATH
    
    # Créer le dossier s'il n'existe pas
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # Table des rapports
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id TEXT PRIMARY KEY,
                date_rapport TEXT NOT NULL,
                contract_id TEXT NOT NULL,
                date_debut TEXT NOT NULL,
                date_fin TEXT NOT NULL,
                fichier_source TEXT,
                total_fax INTEGER NOT NULL,
                fax_envoyes INTEGER NOT NULL,
                fax_recus INTEGER NOT NULL,
                pages_totales INTEGER NOT NULL,
                erreurs_totales INTEGER NOT NULL,
                taux_reussite REAL NOT NULL,
                qr_path TEXT NOT NULL,
                url_rapport TEXT NOT NULL,
                created_at TEXT NOT NULL,
                UNIQUE(id)
            )
        """)
        
        # Table des entrées FAX
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fax_entries (
                id TEXT PRIMARY KEY,
                report_id TEXT NOT NULL,
                fax_id TEXT NOT NULL,
                utilisateur TEXT NOT NULL,
                type TEXT NOT NULL,
                numero_original TEXT,
                numero_normalise TEXT,
                valide BOOLEAN NOT NULL,
                pages INTEGER NOT NULL,
                datetime TEXT NOT NULL,
                erreurs TEXT,
                FOREIGN KEY (report_id) REFERENCES reports(id),
                UNIQUE(id)
            )
        """)
        
        # Indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_reports_contract 
            ON reports(contract_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_reports_created 
            ON reports(created_at)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_fax_entries_report 
            ON fax_entries(report_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_fax_entries_utilisateur 
            ON fax_entries(utilisateur)
        """)
        
        conn.commit()
        logger.info(f"✓ Base de données initialisée: {db_path}")
        
    except Exception as e:
        logger.error(f"✗ Erreur initialisation base de données: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


# ═══════════════════════════════════════════════════════════════════════════
# INSERTION
# ═══════════════════════════════════════════════════════════════════════════

def insert_report_to_db(
    report_id: str,
    report_json: Dict,
    qr_path: str,
    db_path: Path = None
) -> bool:
    """
    Insère un rapport et ses entrées en base de données
    """
    if db_path is None:
        db_path = config.DATABASE_PATH
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # Extraire les statistiques
        stats = report_json.get('statistics', {})
        
        # Insérer le rapport principal
        cursor.execute("""
            INSERT INTO reports (
                id, date_rapport, contract_id, date_debut, date_fin,
                total_fax, fax_envoyes, fax_recus, pages_totales,
                erreurs_totales, taux_reussite, qr_path, url_rapport,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            report_id,
            report_json.get('timestamp', datetime.now().isoformat()),
            report_json.get('contract_id', ''),
            report_json.get('date_debut', ''),
            report_json.get('date_fin', ''),
            stats.get('total_fax', 0),
            stats.get('fax_envoyes', 0),
            stats.get('fax_recus', 0),
            stats.get('pages_totales', 0),
            stats.get('erreurs_totales', 0),
            stats.get('taux_reussite', 0.0),
            qr_path,
            report_json.get('report_url', ''),
            datetime.now().isoformat()
        ))
        
        # Insérer les entrées FAX
        for entry in report_json.get('entries', []):
            erreurs_json = json.dumps(entry.get('erreurs', []))
            
            cursor.execute("""
                INSERT INTO fax_entries (
                    id, report_id, fax_id, utilisateur, type,
                    numero_original, numero_normalise, valide, pages,
                    datetime, erreurs
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                entry.get('id', ''),
                report_id,
                entry.get('fax_id', ''),
                entry.get('utilisateur', ''),
                entry.get('type', ''),
                entry.get('numero_original', ''),
                entry.get('numero_normalise', ''),
                entry.get('valide', False),
                entry.get('pages', 0),
                entry.get('datetime', ''),
                erreurs_json
            ))
        
        conn.commit()
        logger.info(f"✓ Rapport inséré en base: {report_id}")
        return True
        
    except Exception as e:
        logger.error(f"✗ Erreur insertion rapport: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()


# ═══════════════════════════════════════════════════════════════════════════
# CONSULTATION
# ═══════════════════════════════════════════════════════════════════════════

def get_all_reports(db_path: Path = None) -> List[Dict]:
    """
    Récupère tous les rapports
    """
    if db_path is None:
        db_path = config.DATABASE_PATH
    
    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM reports 
            ORDER BY created_at DESC
        """)
        
        reports = [dict(row) for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        return reports
        
    except Exception as e:
        logger.error(f"✗ Erreur lecture rapports: {e}")
        return []


def get_report_by_id(report_id: str, db_path: Path = None) -> Optional[Dict]:
    """
    Récupère un rapport complet avec ses entrées
    """
    if db_path is None:
        db_path = config.DATABASE_PATH
    
    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Récupérer le rapport principal
        cursor.execute("""
            SELECT * FROM reports WHERE id = ?
        """, (report_id,))
        report_row = cursor.fetchone()
        
        if not report_row:
            logger.warning(f"Rapport non trouvé: {report_id}")
            return None
        
        report = dict(report_row)
        
        # Récupérer les entrées associées
        cursor.execute("""
            SELECT * FROM fax_entries WHERE report_id = ?
        """, (report_id,))
        
        entries = []
        for row in cursor.fetchall():
            entry = dict(row)
            # Parser les erreurs depuis JSON
            if entry.get('erreurs'):
                try:
                    entry['erreurs'] = json.loads(entry['erreurs'])
                except:
                    entry['erreurs'] = []
            entries.append(entry)
        
        report['entries'] = entries
        
        cursor.close()
        conn.close()
        
        return report
        
    except Exception as e:
        logger.error(f"✗ Erreur lecture rapport {report_id}: {e}")
        return None


def get_reports_by_contract(contract_id: str, db_path: Path = None) -> List[Dict]:
    """
    Récupère tous les rapports d'un contrat
    """
    if db_path is None:
        db_path = config.DATABASE_PATH
    
    try:
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM reports 
            WHERE contract_id = ?
            ORDER BY created_at DESC
        """, (contract_id,))
        
        reports = [dict(row) for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        return reports
        
    except Exception as e:
        logger.error(f"✗ Erreur lecture rapports du contrat: {e}")
        return []


def get_statistics(db_path: Path = None) -> Dict:
    """
    Retourne les statistiques globales
    """
    if db_path is None:
        db_path = config.DATABASE_PATH
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Nombre de rapports
        cursor.execute("SELECT COUNT(*) FROM reports")
        total_reports = cursor.fetchone()[0]
        
        # Total FAX
        cursor.execute("SELECT SUM(total_fax) FROM reports")
        total_fax = cursor.fetchone()[0] or 0
        
        # Total erreurs
        cursor.execute("SELECT SUM(erreurs_totales) FROM reports")
        total_errors = cursor.fetchone()[0] or 0
        
        # Taux moyen
        cursor.execute("SELECT AVG(taux_reussite) FROM reports")
        avg_success = cursor.fetchone()[0] or 0.0
        
        # Nombre d'utilisateurs uniques
        cursor.execute("SELECT COUNT(DISTINCT utilisateur) FROM fax_entries")
        users_count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        return {
            'total_reports': total_reports,
            'total_fax': total_fax,
            'total_errors': total_errors,
            'avg_success_rate': round(avg_success, 2),
            'users_count': users_count
        }
        
    except Exception as e:
        logger.error(f"✗ Erreur calcul statistiques: {e}")
        return {
            'total_reports': 0,
            'total_fax': 0,
            'total_errors': 0,
            'avg_success_rate': 0.0,
            'users_count': 0
        }


# ═══════════════════════════════════════════════════════════════════════════
# UTILITAIRES
# ═══════════════════════════════════════════════════════════════════════════

def delete_report(report_id: str, db_path: Path = None) -> bool:
    """
    Supprime un rapport et ses entrées
    """
    if db_path is None:
        db_path = config.DATABASE_PATH
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Supprimer les entrées d'abord
        cursor.execute("DELETE FROM fax_entries WHERE report_id = ?", (report_id,))
        
        # Supprimer le rapport
        cursor.execute("DELETE FROM reports WHERE id = ?", (report_id,))
        
        conn.commit()
        logger.info(f"✓ Rapport supprimé: {report_id}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"✗ Erreur suppression rapport: {e}")
        return False


# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Initialisation de la base de données...")
    init_database()
    print("✅ Base de données prête!")
