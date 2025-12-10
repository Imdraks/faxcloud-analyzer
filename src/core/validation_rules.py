"""
Validation - Regles de validation des numeros, pages, type FAX
"""
import logging
from typing import Tuple, Optional
import re

logger = logging.getLogger(__name__)

PHONE_LENGTH = 11
COUNTRY_CODE = '33'


def normalize_number(numero_brut: str) -> str:
    """Normalise un numero: 0X->33X, +33->33, 0033->33"""
    try:
        numero = re.sub(r'\D', '', str(numero_brut))
        
        if numero.startswith('0033'):
            numero = '33' + numero[4:]
        elif numero.startswith('0') and not numero.startswith('00'):
            numero = '33' + numero[1:]
        
        return numero
    except:
        return ''


def validate_number(numero_normalise: str) -> Tuple[bool, Optional[str]]:
    """Valide un numero normalise: longueur=11, commence par 33"""
    if not numero_normalise or len(numero_normalise) == 0:
        return False, "Numero vide"
    
    if len(numero_normalise) != PHONE_LENGTH:
        return False, "Longueur incorrecte"
    
    if not numero_normalise.startswith(COUNTRY_CODE):
        return False, "Indicatif invalide"
    
    return True, None


def analyze_number(numero_brut: str) -> Tuple[bool, str, Optional[str]]:
    """Normalise et valide un numero - retourne (valide, normalise, erreur)"""
    numero_norm = normalize_number(numero_brut)
    est_valide, erreur = validate_number(numero_norm)
    return est_valide, numero_norm, erreur


def validate_pages(pages_brut: str) -> Tuple[bool, Optional[str]]:
    """Valide nombre de pages: numerique et >= 1"""
    try:
        nb = int(str(pages_brut).strip())
        if nb < 1:
            return False, "Pages doit etre >= 1"
        return True, None
    except:
        return False, "Pages invalides"


def validate_fax_type(mode_brut: str) -> Tuple[bool, Optional[str]]:
    """Valide type FAX: SF ou RF"""
    mode = str(mode_brut).strip().upper()
    if mode in ['SF', 'RF']:
        return True, None
    return False, f"Mode invalide: {mode}"
