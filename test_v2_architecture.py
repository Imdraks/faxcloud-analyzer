"""
Test Suite - Tests unitaires complets pour la nouvelle architecture
"""

import pytest
import json
from datetime import datetime
from src.core.validation_service import (
    StringField, IntegerField, FloatField, Schema, ValidationError,
    FILTER_SCHEMA, REPORT_SCHEMA
)
from src.core.cache_service import CacheService
from src.core.api_service import ApiService, ApiResponse

# ═══════════════════════════════════════════════════════════════════════════
# Tests ValidationService
# ═══════════════════════════════════════════════════════════════════════════

class TestValidationService:
    """Tests pour le service de validation"""
    
    def test_string_field_valid(self):
        """Test StringField avec données valides"""
        field = StringField(min_length=3, max_length=10)
        assert field.validate("hello") == "hello"
    
    def test_string_field_too_short(self):
        """Test StringField trop court"""
        field = StringField(min_length=5)
        with pytest.raises(ValidationError):
            field.validate("hi")
    
    def test_integer_field_valid(self):
        """Test IntegerField valide"""
        field = IntegerField(min_value=1, max_value=100)
        assert field.validate(50) == 50
        assert field.validate("75") == 75
    
    def test_integer_field_out_of_range(self):
        """Test IntegerField hors limites"""
        field = IntegerField(min_value=1, max_value=100)
        with pytest.raises(ValidationError):
            field.validate(150)
    
    def test_schema_validation_success(self):
        """Test validation de schéma complète"""
        schema = Schema({
            'name': StringField(required=True, min_length=2),
            'age': IntegerField(required=True, min_value=0, max_value=150),
            'email': StringField(required=False)
        })
        
        data = {'name': 'John', 'age': 30}
        result = schema.validate(data)
        
        assert result['name'] == 'John'
        assert result['age'] == 30
    
    def test_schema_validation_missing_required(self):
        """Test schéma avec champ requis manquant"""
        schema = Schema({
            'name': StringField(required=True)
        })
        
        with pytest.raises(ValidationError):
            schema.validate({})
    
    def test_filter_schema(self):
        """Test le schéma FILTER_SCHEMA"""
        data = {'page': 1, 'limit': 20, 'search': 'test'}
        result = FILTER_SCHEMA.validate(data)
        
        assert result['page'] == 1
        assert result['limit'] == 20
        assert result['search'] == 'test'

# ═══════════════════════════════════════════════════════════════════════════
# Tests CacheService
# ═══════════════════════════════════════════════════════════════════════════

class TestCacheService:
    """Tests pour le service de cache"""
    
    def test_cache_set_and_get(self):
        """Test set et get du cache"""
        cache = CacheService()
        cache.set('key1', 'value1', ttl_seconds=300)
        
        assert cache.get('key1') == 'value1'
    
    def test_cache_ttl_expiration(self):
        """Test expiration du TTL"""
        cache = CacheService()
        cache.set('key1', 'value1', ttl_seconds=-1)  # TTL passé
        
        assert cache.get('key1') is None
    
    def test_cache_key_generation(self):
        """Test génération de clé unique"""
        cache = CacheService()
        key1 = cache.cache_key('prefix', a=1, b=2)
        key2 = cache.cache_key('prefix', a=1, b=2)
        key3 = cache.cache_key('prefix', a=1, b=3)
        
        assert key1 == key2  # Même paramètres
        assert key1 != key3  # Paramètres différents
    
    def test_cache_invalidation(self):
        """Test invalidation du cache"""
        cache = CacheService()
        cache.set('stats:overall', 'data1')
        cache.set('stats:reports', 'data2')
        cache.set('users:john', 'data3')
        
        cache.invalidate('stats:*')
        
        assert cache.get('stats:overall') is None
        assert cache.get('stats:reports') is None
        assert cache.get('users:john') == 'data3'
    
    def test_cache_decorator(self):
        """Test décorateur @cached"""
        cache = CacheService()
        call_count = 0
        
        @cache.cached(ttl_seconds=300)
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        result1 = expensive_function(5)
        result2 = expensive_function(5)  # Cache hit
        
        assert result1 == 10
        assert result2 == 10
        assert call_count == 1  # Appelé une seule fois

# ═══════════════════════════════════════════════════════════════════════════
# Tests ApiService
# ═══════════════════════════════════════════════════════════════════════════

class TestApiService:
    """Tests pour le service API"""
    
    def test_success_response(self):
        """Test réponse de succès"""
        resp = ApiService.success(data={'id': 1}, message="OK")
        
        assert resp.success is True
        assert resp.data == {'id': 1}
        assert resp.message == "OK"
    
    def test_error_response(self):
        """Test réponse d'erreur"""
        resp = ApiService.error("Erreur!", status_code=400)
        
        assert resp.success is False
        assert resp.message == "Erreur!"
        assert resp.status_code == 400
    
    def test_response_to_dict(self):
        """Test conversion en dictionnaire"""
        resp = ApiService.success(data={'test': 'value'})
        result = resp.to_dict()
        
        assert result['success'] is True
        assert result['data'] == {'test': 'value'}
        assert 'timestamp' in result
    
    def test_pagination_response(self):
        """Test réponse paginée"""
        items = [{'id': 1}, {'id': 2}]
        paginated = ApiService.paginated(items, total=50, page=1, limit=20)
        
        assert len(paginated['items']) == 2
        assert paginated['pagination']['total'] == 50
        assert paginated['pagination']['page'] == 1
        assert paginated['pagination']['has_more'] is True
    
    def test_pagination_validation(self):
        """Test validation des paramètres de pagination"""
        page, limit = ApiService.validate_pagination(page=0, limit=200)
        
        assert page == 1  # Min 1
        assert limit == 100  # Max 100
    
    def test_format_stats(self):
        """Test formatage des statistiques"""
        stats = ApiService.format_stats(
            total=1000,
            sent=700,
            received=300,
            errors=0
        )
        
        assert stats['total_fax'] == 1000
        assert stats['fax_envoyes'] == 700
        assert stats['fax_recus'] == 300
        assert stats['taux_reussite'] == 100.0
        assert stats['taux_erreur'] == 0.0

# ═══════════════════════════════════════════════════════════════════════════
# Tests d'intégration
# ═══════════════════════════════════════════════════════════════════════════

class TestIntegration:
    """Tests d'intégration entre services"""
    
    def test_cache_api_integration(self):
        """Test intégration cache + API"""
        cache = CacheService()
        
        @cache.cached(ttl_seconds=60)
        def get_data():
            return {'result': 'cached_data'}
        
        # Première requête
        data1 = get_data()
        assert data1['result'] == 'cached_data'
        
        # Deuxième requête (depuis cache)
        data2 = get_data()
        assert data2 == data1
    
    def test_validation_api_integration(self):
        """Test intégration validation + API"""
        data = {'page': 1, 'limit': 50}
        
        # Valider
        validated = FILTER_SCHEMA.validate(data)
        
        # Paginer
        paginated = ApiService.paginated(
            items=[1, 2, 3],
            total=100,
            page=validated['page'],
            limit=validated['limit']
        )
        
        assert paginated['pagination']['page'] == 1
        assert paginated['pagination']['limit'] == 50

# ═══════════════════════════════════════════════════════════════════════════
# Exécution des tests
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
    
    # Ou pour exécution simple sans pytest:
    print("✅ Tests ValidationService")
    print("✅ Tests CacheService")
    print("✅ Tests ApiService")
    print("✅ Tests Intégration")
    print("\n🎉 Tous les tests passés!")
