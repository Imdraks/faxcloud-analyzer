"""
Module de base de données - Opérations MySQL
Responsabilités:
- Connexion à MySQL (WampServer)
- Création et gestion des tables
- Insertion des rapports et entrées
- Requêtes de consultation
"""

import logging
import json
from typing import Dict, List, Optional
from pathlib import Path

try:
    import mysql.connector
    from mysql.connector import Error as MySQLError
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False
    MySQLError = None

import config

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════
# GESTION CONNEXION
# ═══════════════════════════════════════════════════════════════════════════

def get_connection():
    """
    Obtient une connexion à la base de données MySQL
    
    Returns:
        Connexion MySQL ou None si erreur
    """
    if not MYSQL_AVAILABLE:
        logger.warning("⚠️  mysql-connector-python non installé")
        return None
    
    try:
        conn = mysql.connector.connect(
            host=config.MYSQL_CONFIG['host'],
            user=config.MYSQL_CONFIG['user'],
            password=config.MYSQL_CONFIG['password'],
            database=config.MYSQL_CONFIG['database'],
            port=config.MYSQL_CONFIG['port']
        )
        logger.debug("✓ Connexion MySQL établie")
        return conn
    
    except MySQLError as e:
        logger.error(f"✗ Erreur connexion MySQL: {e}")
        return None


# ═══════════════════════════════════════════════════════════════════════════
# INITIALISATION BASE DE DONNÉES
# ═══════════════════════════════════════════════════════════════════════════

def init_database():
    """
    Crée les tables nécessaires si elles n'existent pas
    """
    if not MYSQL_AVAILABLE:
        logger.warning("⚠️  MySQL non disponible - initialisation ignorée")
        return
    
    try:
        conn = get_connection()
        if not conn:
            logger.error("✗ Impossible de se connecter à MySQL")
            return
        
        cursor = conn.cursor()
        
        logger.info("🔧 Initialisation base de données...")
        
        # Table des rapports
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id VARCHAR(36) PRIMARY KEY,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                contract_id VARCHAR(255),
                date_debut DATE,
                date_fin DATE,
                total_fax INT DEFAULT 0,
                fax_envoyes INT DEFAULT 0,
                fax_recus INT DEFAULT 0,
                pages_totales INT DEFAULT 0,
                pages_envoyees INT DEFAULT 0,
                pages_recues INT DEFAULT 0,
                erreurs_totales INT DEFAULT 0,
                taux_reussite DECIMAL(5, 2) DEFAULT 0,
                qr_path VARCHAR(500),
                json_data LONGTEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_contract (contract_id),
                INDEX idx_timestamp (timestamp)
            )
        """)
        logger.info("✓ Table 'reports' créée/vérifiée")
        
        # Table des entrées
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entries (
                id INT AUTO_INCREMENT PRIMARY KEY,
                report_id VARCHAR(36) NOT NULL,
                fax_id VARCHAR(255),
                utilisateur VARCHAR(255),
                mode VARCHAR(2),
                numero_original VARCHAR(255),
                numero_normalise VARCHAR(11),
                pages INT DEFAULT 0,
                valide BOOLEAN DEFAULT FALSE,
                erreurs TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (report_id) REFERENCES reports(id) ON DELETE CASCADE,
                INDEX idx_report (report_id),
                INDEX idx_utilisateur (utilisateur),
                INDEX idx_numero (numero_normalise)
            )
        """)
        logger.info("✓ Table 'entries' créée/vérifiée")
        
        # Table des statistiques par utilisateur
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_stats (
                id INT AUTO_INCREMENT PRIMARY KEY,
                report_id VARCHAR(36) NOT NULL,
                utilisateur VARCHAR(255),
                total_envois INT DEFAULT 0,
                erreurs INT DEFAULT 0,
                pages INT DEFAULT 0,
                taux_reussite DECIMAL(5, 2) DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (report_id) REFERENCES reports(id) ON DELETE CASCADE,
                INDEX idx_report (report_id),
                INDEX idx_utilisateur (utilisateur)
            )
        """)
        logger.info("✓ Table 'user_stats' créée/vérifiée")
        
        # Table des statistiques d'erreurs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS error_stats (
                id INT AUTO_INCREMENT PRIMARY KEY,
                report_id VARCHAR(36) NOT NULL,
                type_erreur VARCHAR(255),
                count INT DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (report_id) REFERENCES reports(id) ON DELETE CASCADE,
                INDEX idx_report (report_id),
                INDEX idx_type (type_erreur)
            )
        """)
        logger.info("✓ Table 'error_stats' créée/vérifiée")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info("✅ Initialisation base de données réussie")
    
    except Exception as e:
        logger.error(f"✗ Erreur initialisation base de données: {e}")


# ═══════════════════════════════════════════════════════════════════════════
# INSERTION DONNÉES
# ═══════════════════════════════════════════════════════════════════════════

def insert_report_to_db(report_id: str, report_json: Dict, qr_path: str = "") -> bool:
    """
    Insère un rapport complet en base de données
    
    Args:
        report_id: UUID du rapport
        report_json: Données JSON du rapport
        qr_path: Chemin du QR code (optionnel)
    
    Returns:
        True si succès, False sinon
    """
    if not MYSQL_AVAILABLE:
        logger.warning("⚠️  MySQL non disponible - insertion ignorée")
        return False
    
    try:
        conn = get_connection()
        if not conn:
            logger.warning("⚠️  Impossible de se connecter à MySQL")
            return False
        
        cursor = conn.cursor()
        
        stats = report_json.get("statistics", {})
        
        # Insérer le rapport
        cursor.execute("""
            INSERT INTO reports (
                id, contract_id, date_debut, date_fin,
                total_fax, fax_envoyes, fax_recus,
                pages_totales, pages_envoyees, pages_recues,
                erreurs_totales, taux_reussite, qr_path, json_data
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            report_id,
            report_json.get("contract_id", ""),
            report_json.get("date_debut", ""),
            report_json.get("date_fin", ""),
            stats.get("total_fax", 0),
            stats.get("fax_envoyes", 0),
            stats.get("fax_recus", 0),
            stats.get("pages_totales", 0),
            stats.get("pages_envoyees", 0),
            stats.get("pages_recues", 0),
            stats.get("erreurs_totales", 0),
            stats.get("taux_reussite", 0),
            qr_path,
            json.dumps(report_json, ensure_ascii=False)
        ))
        
        logger.info(f"✓ Rapport {report_id} inséré en base")
        
        # Insérer les entrées
        entries = report_json.get("entries", [])
        for entry in entries:
            cursor.execute("""
                INSERT INTO entries (
                    report_id, fax_id, utilisateur, mode,
                    numero_original, numero_normalise, pages,
                    valide, erreurs
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                report_id,
                entry.get("fax_id", ""),
                entry.get("utilisateur", ""),
                entry.get("mode", ""),
                entry.get("numero_original", ""),
                entry.get("numero_normalise", ""),
                entry.get("pages", 0),
                entry.get("valide", False),
                "; ".join(entry.get("erreurs", []))
            ))
        
        logger.info(f"✓ {len(entries)} entrées insérées")
        
        # Insérer les statistiques par utilisateur
        envois_par_utilisateur = stats.get("envois_par_utilisateur", {})
        erreurs_par_utilisateur = stats.get("erreurs_par_utilisateur", {})
        pages_par_utilisateur = stats.get("pages_par_utilisateur", {})
        
        for utilisateur, count in envois_par_utilisateur.items():
            erreurs = erreurs_par_utilisateur.get(utilisateur, 0)
            pages = pages_par_utilisateur.get(utilisateur, 0)
            success_rate = (100 * (count - erreurs) / count) if count > 0 else 0
            
            cursor.execute("""
                INSERT INTO user_stats (
                    report_id, utilisateur, total_envois, erreurs, pages, taux_reussite
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                report_id,
                utilisateur,
                count,
                erreurs,
                pages,
                success_rate
            ))
        
        logger.info(f"✓ {len(envois_par_utilisateur)} utilisateurs enregistrés")
        
        # Insérer les statistiques d'erreurs
        erreurs_par_type = stats.get("erreurs_par_type", {})
        for type_erreur, count in erreurs_par_type.items():
            cursor.execute("""
                INSERT INTO error_stats (
                    report_id, type_erreur, count
                ) VALUES (%s, %s, %s)
            """, (
                report_id,
                type_erreur,
                count
            ))
        
        logger.info(f"✓ {len(erreurs_par_type)} types d'erreurs enregistrés")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info("✅ Rapport complètement inséré")
        return True
    
    except Exception as e:
        logger.warning(f"⚠️  Erreur insertion base de données: {e}")
        return False


# ═══════════════════════════════════════════════════════════════════════════
# REQUÊTES
# ═══════════════════════════════════════════════════════════════════════════

def get_report_by_id(report_id: str) -> Optional[Dict]:
    """
    Récupère un rapport complet par son ID
    
    Args:
        report_id: UUID du rapport
    
    Returns:
        Dictionnaire du rapport ou None
    """
    if not MYSQL_AVAILABLE:
        return None
    
    try:
        conn = get_connection()
        if not conn:
            return None
        
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM reports WHERE id = %s", (report_id,))
        report = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return report
    
    except Exception as e:
        logger.warning(f"⚠️  Erreur requête: {e}")
        return None


def get_reports_by_contract(contract_id: str) -> List[Dict]:
    """
    Récupère tous les rapports d'un contrat
    
    Args:
        contract_id: ID du contrat
    
    Returns:
        Liste des rapports
    """
    if not MYSQL_AVAILABLE:
        return []
    
    try:
        conn = get_connection()
        if not conn:
            return []
        
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute(
            """SELECT * FROM reports 
               WHERE contract_id = %s 
               ORDER BY timestamp DESC""",
            (contract_id,)
        )
        reports = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return reports
    
    except Exception as e:
        logger.warning(f"⚠️  Erreur requête: {e}")
        return []


def get_user_stats(report_id: str) -> List[Dict]:
    """
    Récupère les statistiques par utilisateur pour un rapport
    
    Args:
        report_id: UUID du rapport
    
    Returns:
        Liste des statistiques par utilisateur
    """
    if not MYSQL_AVAILABLE:
        return []
    
    try:
        conn = get_connection()
        if not conn:
            return []
        
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute(
            "SELECT * FROM user_stats WHERE report_id = %s",
            (report_id,)
        )
        stats = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return stats
    
    except Exception as e:
        logger.warning(f"⚠️  Erreur requête: {e}")
        return []


def get_error_stats(report_id: str) -> List[Dict]:
    """
    Récupère les statistiques d'erreurs pour un rapport
    
    Args:
        report_id: UUID du rapport
    
    Returns:
        Liste des statistiques d'erreurs
    """
    if not MYSQL_AVAILABLE:
        return []
    
    try:
        conn = get_connection()
        if not conn:
            return []
        
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute(
            "SELECT * FROM error_stats WHERE report_id = %s",
            (report_id,)
        )
        stats = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return stats
    
    except Exception as e:
        logger.warning(f"⚠️  Erreur requête: {e}")
        return []


# ═══════════════════════════════════════════════════════════════════════════
# TEST
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys
    
    logging.basicConfig(level=logging.INFO)
    config.ensure_directories()
    
    print("🗄️  Module base de données prêt")
    print(f"MySQL disponible: {MYSQL_AVAILABLE}")
    
    if MYSQL_AVAILABLE:
        print("\nInitialisation base de données...")
        init_database()
