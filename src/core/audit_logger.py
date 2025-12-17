"""
📋 Advanced Logging & Audit Trail System
Tracking complet de toutes les opérations
"""

import logging
from datetime import datetime
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class AuditLogger:
    """Système d'audit complet pour toutes les opérations"""
    
    def __init__(self, audit_file='logs/audit.log'):
        self.audit_file = Path(audit_file)
        self.audit_file.parent.mkdir(parents=True, exist_ok=True)
        self.events = []
    
    def log_event(self, event_type, user_id=None, resource_id=None, 
                  action=None, status=None, details=None):
        """Logger un événement d'audit"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,  # upload, delete, export, etc.
            'user_id': user_id or 'anonymous',
            'resource_id': resource_id,
            'action': action,
            'status': status,  # success, failed, warning
            'details': details or {}
        }
        
        self.events.append(event)
        
        # Écrire dans le fichier d'audit
        with open(self.audit_file, 'a') as f:
            f.write(json.dumps(event) + '\n')
        
        logger.info(f"[AUDIT] {event_type}: {status}")
    
    def log_upload(self, report_id, file_size, entry_count, valid_count, status):
        """Logger un upload"""
        self.log_event(
            'upload',
            resource_id=report_id,
            action='file_import',
            status=status,
            details={
                'file_size': file_size,
                'total_entries': entry_count,
                'valid_entries': valid_count,
                'error_entries': entry_count - valid_count,
                'success_rate': f"{(valid_count / entry_count * 100):.1f}%" if entry_count > 0 else "0%"
            }
        )
    
    def log_export(self, report_id, format_type, status):
        """Logger un export"""
        self.log_event(
            'export',
            resource_id=report_id,
            action=f'export_{format_type}',
            status=status
        )
    
    def log_api_call(self, endpoint, method, status_code, response_time):
        """Logger un appel API"""
        self.log_event(
            'api_call',
            action=f'{method} {endpoint}',
            status='success' if 200 <= status_code < 300 else 'error',
            details={
                'status_code': status_code,
                'response_time_ms': f"{response_time:.2f}"
            }
        )
    
    def get_recent_events(self, limit=50):
        """Récupérer les événements récents"""
        return self.events[-limit:]
    
    def get_stats(self):
        """Obtenir les statistiques d'audit"""
        if not self.events:
            return {'total_events': 0}
        
        event_types = {}
        statuses = {}
        
        for event in self.events:
            event_type = event.get('event_type')
            status = event.get('status')
            
            event_types[event_type] = event_types.get(event_type, 0) + 1
            statuses[status] = statuses.get(status, 0) + 1
        
        return {
            'total_events': len(self.events),
            'event_types': event_types,
            'status_breakdown': statuses,
            'first_event': self.events[0]['timestamp'],
            'last_event': self.events[-1]['timestamp']
        }


# Instance globale
_audit_logger = AuditLogger()

def get_audit_logger():
    """Obtenir l'instance d'audit"""
    return _audit_logger


# Décorateur pour logger les API calls
def audit_api_call(f):
    """Décorateur pour tracker les appels API"""
    def wrapper(*args, **kwargs):
        import time
        from flask import request
        
        start_time = time.time()
        result = f(*args, **kwargs)
        response_time = (time.time() - start_time) * 1000
        
        status_code = result[1] if isinstance(result, tuple) else 200
        _audit_logger.log_api_call(
            request.path,
            request.method,
            status_code,
            response_time
        )
        
        return result
    
    wrapper.__name__ = f.__name__
    return wrapper
