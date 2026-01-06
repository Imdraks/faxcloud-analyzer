"""
Service de données - Gestion des rapports et entrées FAX
Utilise MySQL via src/core/db_mysql.py avec fallback en mémoire
"""
import sys
import json
import logging
import random
from pathlib import Path
from datetime import datetime, timedelta

# Ajouter src au path pour importer db_mysql
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

logger = logging.getLogger(__name__)

# Essayer d'importer MySQL, sinon fallback en mémoire
try:
    from src.core.db_mysql import DatabaseMySQL
    USE_MYSQL = True
except ImportError:
    USE_MYSQL = False
    logger.warning("MySQL non disponible, utilisation du mode mémoire")


class DataService:
    """Service pour gérer les données (MySQL ou mémoire)"""
    
    def __init__(self):
        self.db = None
        self._use_mysql = USE_MYSQL
        self.reports = []
        self.entries = []
        self.report_counter = 1
        self.entry_counter = 1
        
        if USE_MYSQL:
            try:
                self.db = DatabaseMySQL()
                self.db.initialize()
                logger.info("[OK] DataService connecte a MySQL")
            except Exception as e:
                logger.warning(f"[WARN] Echec MySQL: {e}, basculement en mode memoire")
                self._use_mysql = False
                self._init_sample_data()
        else:
            self._init_sample_data()
    
    def _init_sample_data(self):
        """Initialiser avec des données d'exemple (mode mémoire)"""
        for i in range(1, 6):
            entries_count = random.randint(100, 1000)
            valid_count = int(entries_count * 0.95)
            report = {
                'id': i,
                'name': f'Rapport Fax {i}',
                'file_size': random.randint(50000, 500000),
                'entries': entries_count,
                'valid': valid_count,
                'errors': entries_count - valid_count,
                'status': 'completed',
                'created_at': (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat()
            }
            self.reports.append(report)
            self.report_counter = i + 1
    
    # ========== REPORTS ==========
    
    def get_all_reports(self, limit=20, offset=0):
        """Récupérer tous les rapports"""
        if self._use_mysql:
            try:
                return self.db.list_reports(limit, offset)
            except Exception as e:
                logger.error(f"Erreur MySQL get_all_reports: {e}")
                return []
        
        reports = sorted(self.reports, key=lambda x: x['created_at'], reverse=True)
        return reports[offset:offset + limit] if limit else reports
    
    def get_report(self, report_id):
        """Récupérer un rapport spécifique"""
        if self._use_mysql:
            try:
                return self.db.get_report(str(report_id))
            except Exception as e:
                logger.error(f"Erreur MySQL get_report: {e}")
                return None
        
        return next((r for r in self.reports if r['id'] == report_id), None)
    
    def create_report(self, name, file_size=0):
        """Créer un nouveau rapport"""
        report = {
            'id': self.report_counter,
            'name': name,
            'file_size': file_size,
            'entries': 0,
            'valid': 0,
            'errors': 0,
            'status': 'processing',
            'created_at': datetime.now().isoformat()
        }
        self.reports.append(report)
        self.report_counter += 1
        return report
    
    # ========== ENTRIES ==========
    
    def get_report_entries(self, report_id, limit=50, offset=0):
        """Récupérer les entrées d'un rapport"""
        if self._use_mysql:
            try:
                entries = self.db.get_fax_entries(str(report_id))
                return entries[offset:offset + limit] if limit else entries
            except Exception as e:
                logger.error(f"Erreur MySQL get_report_entries: {e}")
                return []
        
        entries = [e for e in self.entries if e['report_id'] == report_id]
        return entries[offset:offset + limit] if limit else entries
    
    def add_entry(self, report_id, data):
        """Ajouter une entrée FAX"""
        entry = {
            'id': self.entry_counter,
            'report_id': report_id,
            **data,
            'created_at': datetime.now().isoformat()
        }
        self.entries.append(entry)
        self.entry_counter += 1
        
        report = self.get_report(report_id)
        if report:
            report['entries'] = report.get('entries', 0) + 1
            if data.get('status') == 'valid':
                report['valid'] = report.get('valid', 0) + 1
            else:
                report['errors'] = report.get('errors', 0) + 1
        
        return entry
    
    # ========== STATS ==========
    
    def get_stats(self):
        """Récupérer les statistiques globales"""
        if self._use_mysql:
            try:
                conn = self.db.get_connection()
                cursor = conn.cursor()
                
                cursor.execute("SELECT COUNT(*) FROM reports")
                total_reports = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM reports_entries")
                total_entries = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM reports_entries WHERE valide = 1")
                valid_entries = cursor.fetchone()[0]
                
                cursor.close()
                conn.close()
                
                error_entries = total_entries - valid_entries
                success_rate = round((valid_entries / total_entries * 100) if total_entries > 0 else 0, 2)
                
                return {
                    'total_reports': total_reports,
                    'total_entries': total_entries,
                    'valid_entries': valid_entries,
                    'error_entries': error_entries,
                    'success_rate': success_rate
                }
            except Exception as e:
                logger.error(f"Erreur MySQL get_stats: {e}")
        
        # Fallback mémoire
        total_reports = len(self.reports)
        total_entries = sum(r.get('entries', 0) for r in self.reports)
        valid_entries = sum(r.get('valid', 0) for r in self.reports)
        error_entries = sum(r.get('errors', 0) for r in self.reports)
        success_rate = round((valid_entries / total_entries * 100) if total_entries > 0 else 0, 2)
        
        return {
            'total_reports': total_reports,
            'total_entries': total_entries,
            'valid_entries': valid_entries,
            'error_entries': error_entries,
            'success_rate': success_rate
        }
    
    def get_trends(self, days=7):
        """Obtenir les tendances des N derniers jours"""
        if self._use_mysql:
            try:
                conn = self.db.get_connection()
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT DATE(date_rapport) as day, 
                           SUM(total_fax) as total,
                           SUM(total_fax - erreurs_totales) as valid
                    FROM reports
                    WHERE date_rapport >= DATE_SUB(NOW(), INTERVAL %s DAY)
                    GROUP BY DATE(date_rapport)
                    ORDER BY day
                """, (days,))
                
                trends = []
                for row in cursor.fetchall():
                    trends.append({
                        'date': row[0].strftime('%Y-%m-%d') if row[0] else '',
                        'total': row[1] or 0,
                        'valid': row[2] or 0
                    })
                
                cursor.close()
                conn.close()
                return trends
            except Exception as e:
                logger.error(f"Erreur MySQL get_trends: {e}")
        
        # Fallback avec données simulées
        trends = []
        for i in range(days, 0, -1):
            day = datetime.now() - timedelta(days=i)
            count = random.randint(500, 2000)
            trends.append({
                'date': day.strftime('%Y-%m-%d'),
                'total': count,
                'valid': int(count * 0.95)
            })
        return trends


# Instance globale
data_service = DataService()
