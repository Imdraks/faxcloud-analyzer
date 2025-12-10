"""
Module de validation - Règles officielles FaxCloud
Centralise la logique de validation pour réutilisation en Python et JavaScript
"""

import re
from typing import Tuple, Dict, List, Optional

# ═══════════════════════════════════════════════════════════════════════════
# TYPES D'ERREURS
# ═══════════════════════════════════════════════════════════════════════════

ERROR_TYPES = {
    'empty': 'Numéro vide',
    'length': 'Longueur incorrecte',
    'prefix': 'Indicatif invalide',
    'format': 'Format invalide',
    'asterisk': 'Ligne détectée comme voix (Asterisk)',
}

# ═══════════════════════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════════════════════

PHONE_LENGTH = 11
COUNTRY_CODE = '33'

# ═══════════════════════════════════════════════════════════════════════════
# VALIDATION
# ═══════════════════════════════════════════════════════════════════════════

def normalize_number(numero_brut: str) -> str:
    """
    Étape 1: Normalisation du numéro
    
    Retire tous les caractères non-numériques.
    Convertit 0X → 33X (numéros français nationaux)
    Gère les formats internationaux +33 et 0033
    
    Exemples:
        "+33 1 45 22 11 34" → "33145221134"
        "01 45 22 11 34" → "33145221134"
        "0145221134" → "33145221134"
        "03.27.93.69.43" → "3327936943"
        "0033145221134" → "33145221134"
    
    Args:
        numero_brut (str): Numéro brut avec caractères spéciaux
    
    Returns:
        str: Numéro normalisé (chiffres uniquement)
    """
    try:
        # Étape 1a: Retirer tous les caractères non-numériques
        numero = re.sub(r'\D', '', str(numero_brut))
        
        # Étape 1b: Gérer les différents formats
        # Si commence par 0033, retirer les zéros initiaux
        if numero.startswith('0033'):
            numero = '33' + numero[4:]
        # Si commence par 0, convertir 0X → 33X
        elif numero.startswith('0') and not numero.startswith('00'):
            numero = '33' + numero[1:]
        
        return numero
    
    except Exception:
        return ''


def validate_number(numero_normalise: str) -> Tuple[bool, str]:
    """
    Valide un numéro normalisé selon les règles officielles.
    
    Vérifie (dans cet ordre):
    1. Non vide
    2. Longueur = 11
    3. Commence par 33
    
    Args:
        numero_normalise (str): Numéro déjà normalisé
    
    Returns:
        Tuple[bool, str]: (est_valide, message_erreur)
            - Si valide: (True, None)
            - Si erreur: (False, "Message d'erreur")
    
    Examples:
        >>> validate_number("33145221134")
        (True, None)
        
        >>> validate_number("")
        (False, "Numéro vide")
        
        >>> validate_number("0145221134")
        (False, "Longueur incorrecte")
        
        >>> validate_number("+1234567890")
        (False, "Indicatif invalide")
    """
    
    # Règle 1: Non vide
    if not numero_normalise or len(numero_normalise) == 0:
        return False, ERROR_TYPES['empty']
    
    # Règle 2: Longueur exacte 11
    if len(numero_normalise) != PHONE_LENGTH:
        return False, ERROR_TYPES['length']
    
    # Règle 3: Commence par 33
    if not numero_normalise.startswith(COUNTRY_CODE):
        return False, ERROR_TYPES['prefix']
    
    # Toutes les vérifications passées
    return True, None


def analyze_number(numero_brut: str) -> Tuple[bool, str, str]:
    """
    Analyse complète d'un numéro (normalisation + validation).
    
    C'est la fonction principale à utiliser.
    
    Args:
        numero_brut (str): Numéro brut (peut contenir caractères spéciaux)
    
    Returns:
        Tuple[bool, str, str]: (est_valide, numero_normalise, erreur)
    
    Examples:
        >>> analyze_number("+33 1 45 22 11 34")
        (True, "33145221134", None)
        
        >>> analyze_number("01 45 22 11 34")
        (True, "33145221134", None)
        
        >>> analyze_number("")
        (False, "", "Numéro vide")
        
        >>> analyze_number("🔥🎉🔥")
        (False, "", "Numéro vide")
    """
    
    try:
        # Normaliser
        numero_normalise = normalize_number(numero_brut)
        
        # Valider
        est_valide, erreur = validate_number(numero_normalise)
        
        if est_valide:
            return True, numero_normalise, None
        else:
            return False, numero_normalise, erreur
    
    except Exception as e:
        return False, '', ERROR_TYPES['format']


# ═══════════════════════════════════════════════════════════════════════════
# TEST SUITES
# ═══════════════════════════════════════════════════════════════════════════

# Cas de test pour validation
TEST_CASES = [
    # (input, expected_valid, expected_normalized, expected_error)
    
    # ✅ Cas valides
    ("33145221134", True, "33145221134", None),
    ("+33 1 45 22 11 34", True, "33145221134", None),
    ("01 45 22 11 34", True, "33145221134", None),
    ("0145221134", True, "33145221134", None),  # Conversion 0X → 33X
    ("+33(1)45221134", True, "33145221134", None),
    ("33-1-45-22-11-34", True, "33145221134", None),
    ("0033145221134", True, "33145221134", None),  # Conversion 0033 → 33
    
    # ❌ Cas invalides - Numéro vide
    ("", False, "", "Numéro vide"),
    ("   ", False, "", "Numéro vide"),
    ("---", False, "", "Numéro vide"),
    ("+++", False, "", "Numéro vide"),
    ("🔥🎉🔥", False, "", "Numéro vide"),
    
    # ❌ Cas invalides - Longueur incorrecte
    ("331452211", False, "331452211", "Longueur incorrecte"),     # 9 chiffres
    ("0145221134X", True, "33145221134", None),  # X est retiré (caractère non-numérique), résultat valide
    
    # ❌ Cas invalides - Indicatif invalide (11 chiffres mais mauvais indicatif)
    ("+1-212-555-1234", False, "12125551234", "Indicatif invalide"),  # USA - 11 chiffres mais indicatif 1
    ("+44 207946095", False, "44207946095", "Indicatif invalide"),  # UK - 11 chiffres mais indicatif 44
    ("+493012345678", False, "493012345678", "Longueur incorrecte"),  # Allemagne - 12 chiffres
]


def run_tests():
    """Exécute la suite de tests"""
    print("\n" + "="*70)
    print("[TEST] Suite de validation des numeros")
    print("="*70)
    
    passed = 0
    failed = 0
    
    for numero_input, expected_valid, expected_norm, expected_error in TEST_CASES:
        est_valide, numero_norm, erreur = analyze_number(numero_input)
        
        # Vérifier les résultats
        valid_ok = est_valide == expected_valid
        norm_ok = numero_norm == expected_norm
        error_ok = erreur == expected_error
        
        if valid_ok and norm_ok and error_ok:
            status = "OK"
            passed += 1
        else:
            status = "ERREUR"
            failed += 1
        
        print(f"\n[{status}] Input: {repr(numero_input)}")
        
        if not valid_ok:
            print(f"    Valide: attendu {expected_valid}, obtenu {est_valide}")
        if not norm_ok:
            print(f"    Normalise: attendu {expected_norm}, obtenu {numero_norm}")
        if not error_ok:
            print(f"    Erreur: attendu {expected_error}, obtenu {erreur}")
    
    print("\n" + "="*70)
    print("[RESULTATS] " + str(passed) + " OK | " + str(failed) + " ERREURS | Total: " + str(passed + failed))
    print("="*70 + "\n")
    
    return failed == 0


# ═══════════════════════════════════════════════════════════════════════════
# UTILISATION EN ANALYSE
# ═══════════════════════════════════════════════════════════════════════════

def analyze_entry(entry: Dict) -> Dict:
    """
    Analyse une entrée FAX complète.
    
    Args:
        entry (Dict): Dictionnaire avec les clés:
            - 'numero_appele': Le numéro à analyser
            - 'fax_id': ID du FAX (pour traçage)
            - 'utilisateur': Nom de l'utilisateur
            - 'mode': SF ou RF
            - 'pages': Nombre de pages
    
    Returns:
        Dict: Résultat d'analyse avec:
            - 'numero_original': Le numéro brut
            - 'numero_normalise': Le numéro normalisé
            - 'valide': True/False
            - 'erreurs': Liste des erreurs (vide si valide)
    """
    numero_brut = entry.get('numero_appele', '')
    
    est_valide, numero_norm, erreur = analyze_number(numero_brut)
    
    return {
        'numero_original': numero_brut,
        'numero_normalise': numero_norm,
        'valide': est_valide,
        'erreurs': [erreur] if erreur else [],
        'utilisateur': entry.get('utilisateur', ''),
        'mode': entry.get('mode', ''),
        'pages': entry.get('pages', 0),
    }


# ═══════════════════════════════════════════════════════════════════════════
# VALIDATION PAGES ET TYPE FAX
# ═══════════════════════════════════════════════════════════════════════════

def validate_pages(nombre_pages_brut: str) -> Tuple[bool, Optional[str]]:
    """
    Valide le nombre de pages (colonne K)
    
    Règles:
    - Doit être numérique
    - Doit être >= 1
    
    Args:
        nombre_pages_brut: Valeur brute du champ pages
    
    Returns:
        Tuple[bool, Optional[str]]: (est_valide, message_erreur)
            - Si valide: (True, None)
            - Si erreur: (False, "Message d'erreur")
    """
    try:
        # Convertir en nombre
        try:
            nb_pages = int(str(nombre_pages_brut).strip())
        except ValueError:
            return False, "Nombre de pages invalide"
        
        # Vérifier >= 1
        if nb_pages < 1:
            return False, "Nombre de pages doit être >= 1"
        
        return True, None
    
    except Exception:
        return False, "Nombre de pages invalide"


def validate_fax_type(mode_brut: str) -> Tuple[bool, Optional[str]]:
    """
    Valide le type de FAX (colonne D)
    
    Règles:
    - SF = Fax envoyé (Send Fax)
    - RF = Fax reçu (Receive Fax)
    - Autre valeur = erreur
    
    Args:
        mode_brut: Valeur brute du champ Mode
    
    Returns:
        Tuple[bool, Optional[str]]: (est_valide, message_erreur)
    """
    mode = str(mode_brut).strip().upper()
    
    if mode in ['SF', 'RF']:
        return True, None
    else:
        return False, f"Type de FAX invalide: {mode}"


# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Exécuter les tests
    success = run_tests()
    
    # Afficher des exemples
    print("\n" + "="*70)
    print("[EXEMPLES] Utilisation pratique")
    print("="*70)
    
    exemples = [
        "+33 1 45 22 11 34",
        "01 45 22 11 34",
        "0145221134",
        "",
        "+1-212-555-1234",
    ]
    
    for numero in exemples:
        est_valide, numero_norm, erreur = analyze_number(numero)
        print(f"\nInput: {repr(numero)}")
        print(f"  -> Normalise: {numero_norm}")
        print(f"  -> Valide: {'OUI' if est_valide else 'NON'}")
        if erreur:
            print(f"  -> Erreur: {erreur}")
    
    print("\n")
