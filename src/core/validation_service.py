"""
Validation Service - Validation robuste des données avec schémas
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
import re

class ValidationError(Exception):
    """Exception de validation"""
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"{field}: {message}")

class Schema:
    """Schéma de validation simple mais puissant"""
    
    def __init__(self, fields: Dict[str, 'Field']):
        self.fields = fields
    
    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Valide les données contre le schéma"""
        errors = {}
        validated = {}
        
        for field_name, field in self.fields.items():
            value = data.get(field_name)
            
            # Vérifier si le champ est requis
            if field.required and value is None:
                errors[field_name] = f"Requis"
                continue
            
            if value is None and not field.required:
                validated[field_name] = field.default
                continue
            
            # Valider le type
            try:
                validated[field_name] = field.validate(value)
            except ValidationError as e:
                errors[field_name] = e.message
        
        # Vérifier les champs supplémentaires
        extra_fields = set(data.keys()) - set(self.fields.keys())
        if extra_fields:
            errors['_extra'] = f"Champs non reconnus: {', '.join(extra_fields)}"
        
        if errors:
            raise ValidationError('schema', str(errors))
        
        return validated

class Field:
    """Classe de base pour les champs"""
    
    def __init__(self, required: bool = False, default: Any = None):
        self.required = required
        self.default = default
    
    def validate(self, value: Any) -> Any:
        raise NotImplementedError

class StringField(Field):
    """Champ chaîne de caractères"""
    
    def __init__(self, min_length: int = 0, max_length: int = None, 
                 pattern: str = None, **kwargs):
        super().__init__(**kwargs)
        self.min_length = min_length
        self.max_length = max_length
        self.pattern = pattern
    
    def validate(self, value: Any) -> str:
        if not isinstance(value, str):
            raise ValidationError(None, f"Doit être une chaîne, reçu {type(value).__name__}")
        
        if len(value) < self.min_length:
            raise ValidationError(None, f"Doit avoir au moins {self.min_length} caractères")
        
        if self.max_length and len(value) > self.max_length:
            raise ValidationError(None, f"Doit avoir au maximum {self.max_length} caractères")
        
        if self.pattern and not re.match(self.pattern, value):
            raise ValidationError(None, f"Format invalide")
        
        return value.strip()

class IntegerField(Field):
    """Champ entier"""
    
    def __init__(self, min_value: int = None, max_value: int = None, **kwargs):
        super().__init__(**kwargs)
        self.min_value = min_value
        self.max_value = max_value
    
    def validate(self, value: Any) -> int:
        try:
            val = int(value)
        except (ValueError, TypeError):
            raise ValidationError(None, f"Doit être un entier")
        
        if self.min_value is not None and val < self.min_value:
            raise ValidationError(None, f"Doit être >= {self.min_value}")
        
        if self.max_value is not None and val > self.max_value:
            raise ValidationError(None, f"Doit être <= {self.max_value}")
        
        return val

class FloatField(Field):
    """Champ nombre flottant"""
    
    def __init__(self, min_value: float = None, max_value: float = None, **kwargs):
        super().__init__(**kwargs)
        self.min_value = min_value
        self.max_value = max_value
    
    def validate(self, value: Any) -> float:
        try:
            val = float(value)
        except (ValueError, TypeError):
            raise ValidationError(None, f"Doit être un nombre")
        
        if self.min_value is not None and val < self.min_value:
            raise ValidationError(None, f"Doit être >= {self.min_value}")
        
        if self.max_value is not None and val > self.max_value:
            raise ValidationError(None, f"Doit être <= {self.max_value}")
        
        return val

class BooleanField(Field):
    """Champ booléen"""
    
    def validate(self, value: Any) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'on')
        return bool(value)

class EmailField(StringField):
    """Champ email"""
    
    def __init__(self, **kwargs):
        super().__init__(
            pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            **kwargs
        )

class PhoneField(StringField):
    """Champ téléphone normalisé"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def validate(self, value: Any) -> str:
        val = super().validate(value)
        # Normaliser le numéro: supprimer espaces, tirets, etc.
        normalized = re.sub(r'[\s\-\(\)\.]+', '', val)
        if not normalized.isdigit():
            raise ValidationError(None, f"Le numéro doit contenir uniquement des chiffres")
        return normalized

class ListField(Field):
    """Champ liste"""
    
    def __init__(self, item_type: Field = None, **kwargs):
        super().__init__(**kwargs)
        self.item_type = item_type or StringField()
    
    def validate(self, value: Any) -> List[Any]:
        if not isinstance(value, list):
            raise ValidationError(None, f"Doit être une liste")
        
        return [self.item_type.validate(item) for item in value]

class DictField(Field):
    """Champ dictionnaire"""
    
    def __init__(self, value_type: Field = None, **kwargs):
        super().__init__(**kwargs)
        self.value_type = value_type or StringField()
    
    def validate(self, value: Any) -> Dict[str, Any]:
        if not isinstance(value, dict):
            raise ValidationError(None, f"Doit être un dictionnaire")
        
        return {k: self.value_type.validate(v) for k, v in value.items()}

class DateTimeField(Field):
    """Champ date/heure"""
    
    def __init__(self, format: str = "%Y-%m-%d %H:%M:%S", **kwargs):
        super().__init__(**kwargs)
        self.format = format
    
    def validate(self, value: Any) -> datetime:
        if isinstance(value, datetime):
            return value
        
        if isinstance(value, str):
            try:
                return datetime.strptime(value, self.format)
            except ValueError:
                raise ValidationError(None, f"Format invalide, attendu {self.format}")
        
        raise ValidationError(None, f"Doit être une date/heure")

# Schémas couramment utilisés
REPORT_SCHEMA = Schema({
    'report_id': StringField(required=True),
    'date_rapport': DateTimeField(required=False),
    'fichier_source': StringField(required=True, max_length=255),
    'total_fax': IntegerField(required=True, min_value=0),
    'fax_envoyes': IntegerField(required=True, min_value=0),
    'fax_recus': IntegerField(required=True, min_value=0),
    'erreurs_totales': IntegerField(required=True, min_value=0),
    'taux_reussite': FloatField(required=True, min_value=0, max_value=100),
})

FILTER_SCHEMA = Schema({
    'page': IntegerField(required=False, default=1, min_value=1),
    'limit': IntegerField(required=False, default=20, min_value=1, max_value=100),
    'search': StringField(required=False, max_length=255),
    'sort_by': StringField(required=False),
    'sort_order': StringField(required=False),
})
