"""
API Service - Couche API unifiée avec versioning et pagination
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ApiResponse:
    """Réponse API unifiée"""
    
    def __init__(self, success: bool = True, data: Any = None, 
                 message: str = None, errors: Dict = None, 
                 meta: Dict = None, status_code: int = 200):
        self.success = success
        self.data = data
        self.message = message or ("Succès" if success else "Erreur")
        self.errors = errors or {}
        self.meta = meta or {}
        self.status_code = status_code
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit en dictionnaire pour JSON"""
        return {
            'success': self.success,
            'message': self.message,
            'data': self.data,
            'errors': self.errors if self.errors else None,
            'meta': self.meta if self.meta else None,
            'timestamp': self.timestamp,
        }

class PaginatedResponse:
    """Réponse paginée"""
    
    def __init__(self, items: List[Any], total: int, page: int, 
                 limit: int, has_more: bool = False):
        self.items = items
        self.total = total
        self.page = page
        self.limit = limit
        self.has_more = has_more
        self.pages = (total + limit - 1) // limit if limit > 0 else 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'items': self.items,
            'pagination': {
                'total': self.total,
                'page': self.page,
                'limit': self.limit,
                'pages': self.pages,
                'has_more': self.has_more,
            }
        }

class ApiService:
    """Service API centralisé"""
    
    VERSION = "2.0"
    
    @staticmethod
    def success(data: Any = None, message: str = "Succès", 
                meta: Dict = None, status_code: int = 200) -> ApiResponse:
        """Crée une réponse de succès"""
        return ApiResponse(
            success=True,
            data=data,
            message=message,
            meta=meta,
            status_code=status_code
        )
    
    @staticmethod
    def error(message: str = "Erreur", errors: Dict = None, 
              status_code: int = 400) -> ApiResponse:
        """Crée une réponse d'erreur"""
        return ApiResponse(
            success=False,
            message=message,
            errors=errors,
            status_code=status_code
        )
    
    @staticmethod
    def paginated(items: List[Any], total: int, page: int, 
                  limit: int) -> Dict[str, Any]:
        """Crée une réponse paginée"""
        has_more = (page * limit) < total
        paginated = PaginatedResponse(items, total, page, limit, has_more)
        return paginated.to_dict()
    
    @staticmethod
    def validate_pagination(page: int = 1, limit: int = 20) -> Tuple[int, int]:
        """Valide les paramètres de pagination"""
        page = max(1, min(page, 100000))  # Max 100k pages
        limit = max(1, min(limit, 100))   # Max 100 items
        return page, limit
    
    @staticmethod
    def build_query_filters(filters: Dict) -> Dict[str, Any]:
        """Construit les filtres de requête"""
        result = {}
        
        # Filtres courants
        if 'search' in filters and filters['search']:
            result['search'] = filters['search'].strip()
        
        if 'sort_by' in filters and filters['sort_by']:
            result['sort_by'] = filters['sort_by']
            result['sort_order'] = filters.get('sort_order', 'ASC').upper()
        
        if 'date_from' in filters and filters['date_from']:
            result['date_from'] = filters['date_from']
        
        if 'date_to' in filters and filters['date_to']:
            result['date_to'] = filters['date_to']
        
        return result
    
    @staticmethod
    def format_stats(total: int, sent: int, received: int, errors: int) -> Dict[str, Any]:
        """Formate les statistiques"""
        total = max(total, 1)  # Éviter division par zéro
        success = total - errors
        
        return {
            'total_fax': total,
            'fax_envoyes': sent,
            'fax_recus': received,
            'erreurs_totales': errors,
            'taux_reussite': round((success / total) * 100, 2),
            'taux_erreur': round((errors / total) * 100, 2),
        }
    
    @staticmethod
    def format_report(report: Dict) -> Dict[str, Any]:
        """Formate un rapport pour la réponse API"""
        return {
            'report_id': report.get('id'),
            'date_rapport': report.get('date_rapport'),
            'fichier_source': report.get('fichier_source'),
            'total_fax': report.get('total_fax'),
            'fax_envoyes': report.get('fax_envoyes'),
            'fax_recus': report.get('fax_recus'),
            'erreurs': report.get('erreurs_totales'),
            'taux_reussite': report.get('taux_reussite'),
        }

# Instance globale
api_service = ApiService()
