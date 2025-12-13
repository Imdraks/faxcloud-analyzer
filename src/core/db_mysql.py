"""
Module de gestion de la base de données MySQL
Utilise mysql-connector-python pour se connecter à WampServer/phpMyAdmin
"""

import mysql.connector
import json
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import uuid4

from .config import Config

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════
# CLASSE DATABASE MYSQL
# ═══════════════════════════════════════════════════════════════════════════

class DatabaseMySQL:
    """Gestionnaire de base de données MySQL"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialise la connexion à la base de données MySQL"""
        if config is None:
            config = Config.DATABASE_CONFIG
        
        self.config = config
        self.pool = None
        self.init_connection()
    
    def init_connection(self):
        """Initialise la connexion à MySQL"""
        try:
            # Test de la connexion
            conn = mysql.connector.connect(
                host=self.config['host'],
                port=self.config.get('port', 3306),
                user=self.config['user'],
                password=self.config.get('password', ''),
                database=self.config['database'],
                charset=self.config.get('charset', 'utf8mb4'),
                autocommit=self.config.get('autocommit', True)
            )
            conn.close()
            logger.info(f"Connexion MySQL réussie: {self.config['host']}:{self.config.get('port', 3306)}")
        except mysql.connector.Error as e:
            logger.error(f"Erreur connexion MySQL: {e}")
            raise
    
    def initialize(self):
        """Initialise la base de données (alias pour compatibilité)"""
        self.init_connection()
        self._migrate_analysis_table()
        logger.info("Base de données MySQL initialisée avec succès")
    
    def _migrate_analysis_table(self):
        """Crée ou migre la table analysis_history avec la bonne structure"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Vérifier si la table existe
            cursor.execute("""
                SELECT COUNT(*) FROM information_schema.TABLES 
                WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'analysis_history'
            """, (self.config['database'],))
            
            table_exists = cursor.fetchone()[0] > 0
            
            if table_exists:
                # Vérifier si la colonne analysis_name existe
                cursor.execute("""
                    SELECT COUNT(*) FROM information_schema.COLUMNS 
                    WHERE TABLE_SCHEMA = %s AND TABLE_NAME = 'analysis_history' 
                    AND COLUMN_NAME = 'analysis_name'
                """, (self.config['database'],))
                
                has_analysis_name = cursor.fetchone()[0] > 0
                
                if not has_analysis_name:
                    logger.info("Ajout de colonnes à la table analysis_history...")
                    # Recréer la table avec la bonne structure
                    cursor.execute("DROP TABLE IF EXISTS analysis_history")
                    self._create_analysis_table(cursor)
                    logger.info("Table analysis_history recréée avec succès")
            else:
                logger.info("Création de la table analysis_history...")
                self._create_analysis_table(cursor)
                logger.info("Table analysis_history créée avec succès")
            
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            logger.warning(f"Erreur lors de la migration: {e}")
    
    def _create_analysis_table(self, cursor):
        """Crée la table analysis_history avec la bonne structure"""
        cursor.execute("""
            CREATE TABLE analysis_history (
                id INT AUTO_INCREMENT PRIMARY KEY,
                report_id VARCHAR(255) NOT NULL,
                analysis_name VARCHAR(255) NOT NULL,
                fichier_source VARCHAR(255),
                date_analyse TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_fax INT NOT NULL DEFAULT 0,
                fax_envoyes INT NOT NULL DEFAULT 0,
                fax_recus INT NOT NULL DEFAULT 0,
                erreurs_totales INT NOT NULL DEFAULT 0,
                taux_reussite FLOAT NOT NULL DEFAULT 0.0,
                statut VARCHAR(50) NOT NULL,
                message TEXT,
                FOREIGN KEY (report_id) REFERENCES reports(id),
                INDEX idx_analysis_date (date_analyse DESC),
                INDEX idx_analysis_report (report_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
    
    def get_connection(self):
        """Retourne une connexion MySQL"""
        return mysql.connector.connect(
            host=self.config['host'],
            port=self.config.get('port', 3306),
            user=self.config['user'],
            password=self.config.get('password', ''),
            database=self.config['database'],
            charset=self.config.get('charset', 'utf8mb4'),
            autocommit=False
        )
    
    # ═════════════════════════════════════════════════════════════════════
    # GESTION DES RAPPORTS
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
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
            logger.info(f"Rapport {report_data['rapport_id']} sauvegardé en MySQL")
            return report_data['rapport_id']
        
        except mysql.connector.Error as e:
            logger.error(f"Erreur MySQL save_report: {e}")
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()
    
    def save_fax_entry(self, cursor, report_id: str, entry: Dict[str, Any]) -> None:
        """Sauvegarde une entrée FAX"""
        cursor.execute("""
            INSERT INTO fax_entries (
                id, report_id, fax_id, utilisateur, mode, date_heure,
                numero_original, numero_normalise, pages, valide, erreurs
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            str(uuid4()),
            report_id,
            entry.get('fax_id'),
            entry.get('utilisateur'),
            entry.get('mode'),
            entry.get('date_heure'),
            entry.get('numero_original'),
            entry.get('numero_normalise'),
            entry.get('pages'),
            1 if entry.get('valide') else 0,
            json.dumps(entry.get('erreurs', []))
        ))
    
    def get_report(self, report_id: str) -> Optional[Dict[str, Any]]:
        """Récupère un rapport complet depuis la BDD"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT donnees_json, qr_path, url_rapport
                FROM reports
                WHERE id = %s
            """, (report_id,))
            
            row = cursor.fetchone()
            
            if not row:
                return None
            
            # Charger le JSON stocké
            report_data = json.loads(row[0])
            
            # Ajouter les chemins si disponibles
            if row[1]:
                report_data['qr_path'] = row[1]
            if row[2]:
                report_data['report_url'] = row[2]
            
            return report_data
        
        except mysql.connector.Error as e:
            logger.error(f"Erreur MySQL get_report: {e}")
            return None
        finally:
            cursor.close()
            conn.close()
    
    def list_reports(self, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """Liste les rapports avec pagination"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, date_rapport, contract_id, total_fax, 
                       fax_envoyes, fax_recus, erreurs_totales, taux_reussite
                FROM reports
                ORDER BY date_rapport DESC
                LIMIT %s OFFSET %s
            """, (limit, offset))
            
            reports = []
            for row in cursor.fetchall():
                reports.append({
                    'id': row[0],
                    'date_rapport': str(row[1]),
                    'contract_id': row[2],
                    'total_fax': row[3],
                    'fax_envoyes': row[4],
                    'fax_recus': row[5],
                    'erreurs': row[6],
                    'taux_reussite': row[7]
                })
            
            return reports
        
        except mysql.connector.Error as e:
            logger.error(f"Erreur MySQL list_reports: {e}")
            return []
        finally:
            cursor.close()
            conn.close()
    
    # ═════════════════════════════════════════════════════════════════════
    # GESTION DE L'HISTORIQUE D'ANALYSE
    # ═════════════════════════════════════════════════════════════════════
    
    def save_analysis(self, analysis_data: Dict[str, Any]) -> str:
        """Sauvegarde une analyse dans l'historique"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            analysis_id = str(uuid4())
            report_id = analysis_data.get('rapport_id', '')
            fichier_source = analysis_data.get('fichier_source', '')
            stats = analysis_data.get('statistics', {})
            
            # Générer un nom automatique si pas fourni
            from datetime import datetime
            timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")
            analysis_name = f"{fichier_source.split('/')[-1].split('.')[0]} - {timestamp}" if fichier_source else f"Analyse - {timestamp}"
            
            cursor.execute("""
                INSERT INTO analysis_history (
                    id, report_id, analysis_name, fichier_source, date_analyse,
                    total_fax, fax_envoyes, fax_recus, erreurs_totales, taux_reussite,
                    statut, message
                ) VALUES (%s, %s, %s, %s, NOW(), %s, %s, %s, %s, %s, %s, %s)
            """, (
                analysis_id,
                report_id,
                analysis_name,
                fichier_source,
                stats.get('total_fax', 0),
                stats.get('fax_envoyes', 0),
                stats.get('fax_recus', 0),
                stats.get('erreurs_totales', 0),
                stats.get('taux_reussite', 0),
                'completed',
                f"Analyse: {stats.get('total_fax', 0)} FAX analysés"
            ))
            
            conn.commit()
            logger.info(f"Analyse {analysis_id} sauvegardée en MySQL")
            return analysis_id
        
        except mysql.connector.Error as e:
            logger.error(f"Erreur MySQL save_analysis: {e}")
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_analysis_history(self, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """Récupère l'historique des analyses"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, report_id, analysis_name, fichier_source, date_analyse,
                       total_fax, fax_envoyes, fax_recus, erreurs_totales, taux_reussite
                FROM analysis_history
                ORDER BY date_analyse DESC
                LIMIT %s OFFSET %s
            """, (limit, offset))
            
            columns = [desc[0] for desc in cursor.description]
            analyses = []
            
            for row in cursor.fetchall():
                analysis = dict(zip(columns, row))
                # Renommer pour compatibilité avec le frontend
                if 'date_analyse' in analysis:
                    analysis['analysis_date'] = analysis['date_analyse']
                    analysis['fichier_source'] = analysis['analysis_name']
                analyses.append(analysis)
            
            cursor.close()
            conn.close()
            return analyses
        
        except mysql.connector.Error as e:
            logger.error(f"Erreur MySQL get_analysis_history: {e}")
            raise
    
    def get_fax_entries(self, report_id: str, only_errors: bool = False) -> List[Dict[str, Any]]:
        """Récupère les entrées FAX d'un rapport"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT id, fax_id, utilisateur, mode, date_heure,
                       numero_original, numero_normalise, pages, valide, erreurs
                FROM fax_entries
                WHERE report_id = %s
            """
            params = [report_id]
            
            if only_errors:
                query += " AND valide = 0"
            
            query += " ORDER BY date_heure"
            
            cursor.execute(query, params)
            
            entries = []
            for row in cursor.fetchall():
                entries.append({
                    'id': row[0],
                    'fax_id': row[1],
                    'utilisateur': row[2],
                    'mode': row[3],
                    'date_heure': str(row[4]) if row[4] else None,
                    'numero_original': row[5],
                    'numero_normalise': row[6],
                    'pages': row[7],
                    'valide': bool(row[8]),
                    'erreurs': json.loads(row[9]) if row[9] else []
                })
            
            return entries
        
        except mysql.connector.Error as e:
            logger.error(f"Erreur MySQL get_fax_entries: {e}")
            return []
        finally:
            cursor.close()
            conn.close()
    
    def get_report_data(self, report_id: str) -> Optional[str]:
        """Récupère les données JSON complètes d'un rapport"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT donnees_json FROM reports WHERE id = %s
            """, (report_id,))
            
            row = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if row:
                return row[0]
            return None
        
        except mysql.connector.Error as e:
            logger.error(f"Erreur MySQL get_report_data: {e}")
            return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques globales"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_rapports,
                    COALESCE(SUM(total_fax), 0) as total_fax_global,
                    COALESCE(SUM(erreurs_totales), 0) as total_erreurs,
                    COALESCE(AVG(taux_reussite), 0) as taux_reussite_moyen,
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
        
        except mysql.connector.Error as e:
            logger.error(f"Erreur MySQL get_statistics: {e}")
            return {}
        finally:
            cursor.close()
            conn.close()
    
    # ═════════════════════════════════════════════════════════════════════
    # GESTION DES TOKENS DE PARTAGE
    # ═════════════════════════════════════════════════════════════════════
    
    def create_share_token(self, report_id: str, days: int = 7, utilisateur: str = None) -> str:
        """Crée un token de partage pour un rapport"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            import secrets
            from datetime import timedelta
            
            token = secrets.token_urlsafe(32)
            expires_at = datetime.now() + timedelta(days=days)
            
            cursor.execute("""
                INSERT INTO share_tokens (token, report_id, expires_at, utilisateur)
                VALUES (%s, %s, %s, %s)
            """, (token, report_id, expires_at, utilisateur))
            
            conn.commit()
            logger.info(f"Token de partage créé pour rapport {report_id}: {token}")
            return token
        
        except mysql.connector.Error as e:
            logger.error(f"Erreur MySQL create_share_token: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_report_by_share_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Récupère un rapport à partir d'un token de partage"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Vérifier que le token est valide et non expiré
            cursor.execute("""
                SELECT report_id FROM share_tokens
                WHERE token = %s AND expires_at > NOW()
            """, (token,))
            
            result = cursor.fetchone()
            if not result:
                logger.warning(f"Token de partage invalide ou expiré: {token}")
                cursor.close()
                conn.close()
                return None
            
            report_id = result[0]
            
            # Récupérer le rapport
            cursor.execute("""
                SELECT donnees_json, qr_path FROM reports WHERE id = %s
            """, (report_id,))
            
            row = cursor.fetchone()
            if not row:
                cursor.close()
                conn.close()
                return None
            
            report_data = json.loads(row[0])
            report_data['qr_path'] = row[1]
            report_data['rapport_id'] = report_id
            
            cursor.close()
            conn.close()
            return report_data
        
        except mysql.connector.Error as e:
            logger.error(f"Erreur MySQL get_report_by_share_token: {e}")
            return None
    
    def list_share_tokens(self, report_id: str) -> List[Dict[str, Any]]:
        """Liste les tokens de partage actifs pour un rapport"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT token, created_at, expires_at, utilisateur
                FROM share_tokens
                WHERE report_id = %s AND expires_at > NOW()
                ORDER BY created_at DESC
            """, (report_id,))
            
            tokens = []
            for row in cursor.fetchall():
                tokens.append({
                    'token': row[0],
                    'created_at': str(row[1]),
                    'expires_at': str(row[2]),
                    'utilisateur': row[3]
                })
            
            cursor.close()
            conn.close()
            return tokens
        
        except mysql.connector.Error as e:
            logger.error(f"Erreur MySQL list_share_tokens: {e}")
            return []
    
    def delete_share_token(self, token: str) -> bool:
        """Supprime un token de partage"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM share_tokens WHERE token = %s", (token,))
            conn.commit()
            
            cursor.close()
            conn.close()
            return True
        
        except mysql.connector.Error as e:
            logger.error(f"Erreur MySQL delete_share_token: {e}")
            return False
