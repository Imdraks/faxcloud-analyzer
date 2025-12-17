"""
Service Cache - Gestion du cache en mémoire pour les queries fréquentes
"""

from datetime import datetime, timedelta
from functools import wraps
import json
import hashlib
from typing import Any, Dict, Optional, Callable

class CacheService:
    """Service de cache simple et efficace"""
    
    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self._expires: Dict[str, datetime] = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Récupère une valeur du cache"""
        if key not in self._cache:
            return None
        
        if key in self._expires and datetime.now() > self._expires[key]:
            del self._cache[key]
            del self._expires[key]
            return None
        
        return self._cache[key]
    
    def set(self, key: str, value: Any, ttl_seconds: int = 300) -> None:
        """Stocke une valeur dans le cache"""
        self._cache[key] = value
        self._expires[key] = datetime.now() + timedelta(seconds=ttl_seconds)
    
    def invalidate(self, pattern: str = "*") -> None:
        """Invalide les entrées du cache"""
        if pattern == "*":
            self._cache.clear()
            self._expires.clear()
        else:
            keys_to_delete = [k for k in self._cache.keys() if pattern in k]
            for key in keys_to_delete:
                del self._cache[key]
                if key in self._expires:
                    del self._expires[key]
    
    def cache_key(self, prefix: str, **kwargs) -> str:
        """Génère une clé de cache unique"""
        params = json.dumps(kwargs, sort_keys=True)
        hash_val = hashlib.md5(params.encode()).hexdigest()[:8]
        return f"{prefix}:{hash_val}"
    
    def cached(self, ttl_seconds: int = 300):
        """Décorateur pour cacher le résultat d'une fonction"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Générer une clé basée sur la fonction et ses arguments
                cache_key = f"{func.__name__}:{hashlib.md5(str((args, kwargs)).encode()).hexdigest()[:8]}"
                
                # Vérifier le cache
                result = self.get(cache_key)
                if result is not None:
                    return result
                
                # Exécuter et cacher
                result = func(*args, **kwargs)
                self.set(cache_key, result, ttl_seconds)
                return result
            
            return wrapper
        return decorator

# Singleton global
cache_service = CacheService()
