"""
Service de données - Gestion des rapports et entrées FAX
"""
import json
from datetime import datetime, timedelta
import random

class DataService:
    """Service pour gérer les données"""
    
    def __init__(self):
        # Base de données en mémoire pour les tests
        self.reports = []
        self.entries = []
        self.report_counter = 1
        self.entry_counter = 1
        self._init_sample_data()
    
    def _init_sample_data(self):
        """Initialiser avec des données d'exemple"""
        # Créer 5 rapports d'exemple
        for i in range(1, 6):
            report = {
                'id': i,
                'name': f'Rapport Fax {i}',
                'file_size': random.randint(50000, 500000),
                'entries': random.randint(100, 1000),
                'valid': random.randint(50, 900),
                'errors': random.randint(0, 50),
                'status': 'completed',
                'created_at': (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat()
            }
            report['errors'] = report['entries'] - report['valid']
            self.reports.append(report)
            self.report_counter = i + 1
            
            # Créer des entrées pour ce rapport
            for j in range(report['entries']):
                entry = {
                    'id': self.entry_counter,
                    'report_id': i,
                    'fax_number': f'+33{random.randint(1,9)}{random.randint(10000000, 99999999)}',
                    'caller_id': f'Caller_{random.randint(1, 100)}',
                    'recipient': f'Recipient_{random.randint(1, 100)}',
                    'duration': random.randint(30, 300),
                    'page_count': random.randint(1, 10),
                    'status': 'valid' if random.random() > 0.1 else 'error',
                    'error_message': 'Transmission échouée' if random.random() > 0.1 else None,
                    'created_at': datetime.now().isoformat()
                }
                self.entries.append(entry)
                self.entry_counter += 1
    
    # REPORTS
    def get_all_reports(self, limit=None, offset=0):
        """Récupérer tous les rapports"""
        reports = sorted(self.reports, key=lambda x: x['created_at'], reverse=True)
        if limit:
            return reports[offset:offset + limit]
        return reports
    
    def get_report(self, report_id):
        """Récupérer un rapport spécifique"""
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
    
    # ENTRIES
    def get_report_entries(self, report_id, limit=None, offset=0):
        """Récupérer les entrées d'un rapport"""
        entries = [e for e in self.entries if e['report_id'] == report_id]
        if limit:
            return entries[offset:offset + limit]
        return entries
    
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
        
        # Mettre à jour le rapport
        report = self.get_report(report_id)
        if report:
            report['entries'] = report.get('entries', 0) + 1
            if entry['status'] == 'valid':
                report['valid'] = report.get('valid', 0) + 1
            else:
                report['errors'] = report.get('errors', 0) + 1
        
        return entry
    
    # STATS
    def get_stats(self):
        """Récupérer les statistiques globales"""
        total_reports = len(self.reports)
        total_entries = sum(r['entries'] for r in self.reports)
        valid_entries = sum(r['valid'] for r in self.reports)
        error_entries = sum(r['errors'] for r in self.reports)
        
        success_rate = round((valid_entries / total_entries * 100) if total_entries > 0 else 0, 2)
        
        return {
            'total_reports': total_reports,
            'total_entries': total_entries,
            'valid_entries': valid_entries,
            'error_entries': error_entries,
            'success_rate': success_rate
        }
    
    def get_trends(self, days=7):
        """Obtenir les tendances des 7 derniers jours"""
        trends = []
        for i in range(days, 0, -1):
            day = datetime.now() - timedelta(days=i)
            # Simuler des données
            count = random.randint(500, 2000)
            trends.append({
                'date': day.strftime('%Y-%m-%d'),
                'total': count,
                'valid': int(count * 0.95)
            })
        return trends

# Instance globale
data_service = DataService()
