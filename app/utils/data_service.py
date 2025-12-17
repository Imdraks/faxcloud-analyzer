#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data Service - In-memory data management for FaxCloud Analyzer
Gère les données en mémoire pour les tests
"""

from datetime import datetime, timedelta
import random

class DataService:
    """Service de gestion des données"""
    
    def __init__(self):
        self.reports = []
        self.entries = []
        self._generate_sample_data()
    
    def _generate_sample_data(self):
        """Générer des données d'exemple"""
        # Créer quelques rapports d'exemple
        for i in range(1, 6):
            report = {
                'id': i,
                'name': f'Rapport d\'Analyse #{i}',
                'created_at': (datetime.now() - timedelta(days=i)).isoformat(),
                'entry_count': random.randint(100, 500),
                'file_size': random.randint(1000000, 5000000),
                'status': 'completed'
            }
            self.reports.append(report)
            
            # Générer des entrées pour chaque rapport
            for j in range(1, random.randint(50, 150)):
                entry = {
                    'id': len(self.entries) + 1,
                    'report_id': i,
                    'data': f'Données FAX #{j} - Rapport #{i}',
                    'status': 'success' if random.random() > 0.1 else 'error',
                    'message': 'Validation réussie' if random.random() > 0.1 else 'Erreur de validation',
                    'created_at': (datetime.now() - timedelta(days=i, hours=random.randint(0, 23))).isoformat()
                }
                self.entries.append(entry)
    
    def get_all_reports(self, limit=20, offset=0):
        """Récupérer tous les rapports"""
        return self.reports[offset:offset+limit]
    
    def get_report(self, report_id):
        """Récupérer un rapport spécifique"""
        for report in self.reports:
            if report['id'] == report_id:
                return report
        return None
    
    def create_report(self, name, file_size):
        """Créer un nouveau rapport"""
        report_id = max([r['id'] for r in self.reports]) + 1 if self.reports else 1
        report = {
            'id': report_id,
            'name': name,
            'created_at': datetime.now().isoformat(),
            'entry_count': 0,
            'file_size': file_size,
            'status': 'pending'
        }
        self.reports.append(report)
        return report
    
    def get_report_entries(self, report_id, limit=50, offset=0):
        """Récupérer les entrées d'un rapport"""
        entries = [e for e in self.entries if e['report_id'] == report_id]
        return entries[offset:offset+limit]
    
    def add_entry(self, report_id, entry_data):
        """Ajouter une entrée à un rapport"""
        entry_id = max([e['id'] for e in self.entries]) + 1 if self.entries else 1
        entry = {
            'id': entry_id,
            'report_id': report_id,
            'data': entry_data.get('data', ''),
            'status': entry_data.get('status', 'pending'),
            'message': entry_data.get('message', ''),
            'created_at': datetime.now().isoformat()
        }
        self.entries.append(entry)
        
        # Mettre à jour le nombre d'entrées du rapport
        for report in self.reports:
            if report['id'] == report_id:
                report['entry_count'] += 1
                break
        
        return entry
    
    def get_stats(self):
        """Récupérer les statistiques globales"""
        total_entries = len(self.entries)
        success_entries = len([e for e in self.entries if e['status'] == 'success'])
        error_entries = len([e for e in self.entries if e['status'] == 'error'])
        
        return {
            'total_reports': len(self.reports),
            'total_entries': total_entries,
            'success_entries': success_entries,
            'error_entries': error_entries,
            'success_rate': round((success_entries / total_entries * 100) if total_entries > 0 else 0, 1)
        }
    
    def get_trends(self, days=7):
        """Récupérer les tendances des derniers jours"""
        trends = []
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).date()
            count = len([e for e in self.entries if datetime.fromisoformat(e['created_at']).date() == date])
            trends.insert(0, {'date': str(date), 'count': count})
        return trends

# Instance globale
data_service = DataService()
