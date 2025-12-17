"""
📊 Performance Monitoring & Metrics Dashboard
Collecte des métriques en temps réel
"""

import time
import psutil
import logging
from datetime import datetime
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Collecte les métriques de performance du système"""
    
    def __init__(self, max_history=1000):
        self.metrics = defaultdict(deque)
        self.max_history = max_history
        self.start_time = time.time()
    
    def record_metric(self, metric_name, value):
        """Enregistrer une métrique"""
        self.metrics[metric_name].append({
            'timestamp': datetime.now().isoformat(),
            'value': value
        })
        
        # Limiter l'historique
        if len(self.metrics[metric_name]) > self.max_history:
            self.metrics[metric_name].popleft()
    
    def get_system_metrics(self):
        """Obtenir les métriques système"""
        try:
            process = psutil.Process()
            
            return {
                'cpu_percent': process.cpu_percent(interval=0.1),
                'memory_mb': process.memory_info().rss / 1024 / 1024,
                'memory_percent': process.memory_percent(),
                'num_threads': process.num_threads(),
                'open_files': len(process.open_files()),
                'uptime_seconds': time.time() - self.start_time
            }
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            return {}
    
    def get_uptime(self):
        """Obtenir le temps d'uptime en secondes"""
        return time.time() - self.start_time
    
    def get_metrics_summary(self):
        """Résumé des métriques collectées"""
        summary = {}
        
        for metric_name, values in self.metrics.items():
            if values:
                values_list = [v['value'] for v in values if isinstance(v['value'], (int, float))]
                if values_list:
                    summary[metric_name] = {
                        'current': values[-1]['value'],
                        'average': sum(values_list) / len(values_list),
                        'min': min(values_list),
                        'max': max(values_list),
                        'count': len(values)
                    }
        
        return summary


# Instance globale
_metrics_collector = MetricsCollector()

def get_metrics_collector():
    """Obtenir l'instance du collecteur de métriques"""
    return _metrics_collector


class APIRateLimiter:
    """Rate limiting par endpoint et par IP"""
    
    def __init__(self, default_rpm=60):  # 60 requests per minute
        self.limits = defaultdict(dict)  # {endpoint: {ip: [timestamps]}}
        self.default_rpm = default_rpm
    
    def is_allowed(self, endpoint, client_ip, rpm=None):
        """Vérifier si la requête est autorisée"""
        rpm = rpm or self.default_rpm
        current_time = time.time()
        
        # Initialiser l'endpoint s'il n'existe pas
        if endpoint not in self.limits:
            self.limits[endpoint] = {}
        
        # Initialiser l'IP s'il n'existe pas
        if client_ip not in self.limits[endpoint]:
            self.limits[endpoint][client_ip] = []
        
        # Nettoyer les timestamps > 1 minute
        cutoff_time = current_time - 60
        self.limits[endpoint][client_ip] = [
            ts for ts in self.limits[endpoint][client_ip]
            if ts > cutoff_time
        ]
        
        # Vérifier la limite
        if len(self.limits[endpoint][client_ip]) >= rpm:
            logger.warning(f"Rate limit exceeded: {endpoint} from {client_ip}")
            return False
        
        # Ajouter le timestamp actuel
        self.limits[endpoint][client_ip].append(current_time)
        return True
    
    def get_stats(self):
        """Obtenir les statistiques de rate limiting"""
        stats = {}
        for endpoint, ips in self.limits.items():
            stats[endpoint] = {
                'unique_ips': len(ips),
                'total_requests': sum(len(reqs) for reqs in ips.values())
            }
        return stats


# Instance globale
_rate_limiter = APIRateLimiter()

def get_rate_limiter():
    """Obtenir l'instance du rate limiter"""
    return _rate_limiter
