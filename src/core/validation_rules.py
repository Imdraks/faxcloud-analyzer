"""
Validation - Regles de validation completes pour FAX FaxCloud

Regles appliquees:
1. Colonne D (Mode): SF = FAX envoye, RF = FAX recu (OBLIGATOIRE)
2. Colonne H (Numero appele): 
   - Doit commencer par 33
   - Doit avoir 11 chiffres exactement
   - 3e chiffre NE DOIT PAS etre 6 ou 7 (erreur sinon)
3. Colonne K (Pages): 
   - Si 0 pages = ERREUR
   - Doit etre numerique et > 0
"""
import logging
from typing import Tuple, Optional
import re

logger = logging.getLogger(__name__)

# Constantes de validation
PHONE_LENGTH = 11              # Longueur exacte du numero
COUNTRY_CODE = '33'            # Indicatif France
MIN_PAGES = 1                  # Pages minimum (0 = erreur)
VALID_FAX_MODES = ['SF', 'RF'] # Modes acceptes


def validate_fax_type(mode_brut: str) -> Tuple[bool, Optional[str]]:
    """
    Valide le type FAX (Colonne D)
    
    Accepte:
    - SF = Send Fax (FAX envoye)
    - RF = Receive Fax (FAX recu)
    
    Retour: (valide, message_erreur)
    """
    if not mode_brut:
        return False, "Mode FAX vide"
    
    mode = str(mode_brut).strip().upper()
    
    if mode not in VALID_FAX_MODES:
        return False, f"Mode invalide: '{mode}' (doit etre SF ou RF)"
    
    return True, None


def normalize_number(numero_brut: str) -> str:
    """
    Normalise un numero telephonique vers format 33XXXXXXXXXXX
    
    Formats acceptes:
    - 0145221134 → 33145221134 (0X -> 33X)
    - +33145221134 → 33145221134 (retirer +)
    - 00331 45 22 11 34 → 33145221134 (0033 -> 33)
    
    Retour: Numero normalise ou string vide si erreur
    """
    try:
        # Retirer tous les caracteres non-numeriques
        numero = re.sub(r'\D', '', str(numero_brut))
        
        # Format: 0033... → 33...
        if numero.startswith('0033'):
            numero = '33' + numero[4:]
        # Format: 0X... (10 chiffres) → 33X...
        elif numero.startswith('0') and not numero.startswith('00') and len(numero) == 10:
            numero = '33' + numero[1:]
        # Format: déjà 33... ou autre
        
        return numero
    except:
        return ''


def validate_number(numero_normalise: str) -> Tuple[bool, Optional[str]]:
    """
    Valide un numero normalise (Colonne H - Numero appele)
    
    Regles strictes:
    1. Doit commencer par 33 (indicatif France)
    2. Doit avoir exactement 11 chiffres
    3. 3e chiffre (index 2) NE DOIT PAS etre 6 ou 7 (ERREUR si oui)
    
    Retour: (valide, message_erreur)
    """
    # Verifier non-vide
    if not numero_normalise or len(numero_normalise) == 0:
        return False, "Numero vide"
    
    # Verifier que c'est uniquement des chiffres
    if not numero_normalise.isdigit():
        return False, "Numero contient caracteres non-numeriques"
    
    # Verifier longueur exacte: 11 chiffres
    if len(numero_normalise) != PHONE_LENGTH:
        return False, f"Longueur incorrecte: {len(numero_normalise)} chiffres (attendu {PHONE_LENGTH})"
    
    # Verifier commence par 33 (indicatif France)
    if not numero_normalise.startswith(COUNTRY_CODE):
        return False, f"Indicatif invalide: ne commence pas par {COUNTRY_CODE}"
    
    # REGLE STRICTE: 3e chiffre (index 2) NE DOIT PAS etre 6 ou 7
    troisieme_chiffre = numero_normalise[2]
    if troisieme_chiffre in ['6', '7']:
        return False, f"3e chiffre invalide: {troisieme_chiffre} (ne doit pas etre 6 ou 7)"
    
    # Numero valide
    return True, None


def analyze_number(numero_brut: str) -> Tuple[bool, str, Optional[str]]:
    """
    Combine normalisation et validation d'un numero
    
    Entree: numero brut (format quelconque)
    Retour: (valide, numero_normalise, message_erreur)
    """
    # Etape 1: Normaliser
    numero_normalise = normalize_number(numero_brut)
    
    # Etape 2: Valider
    est_valide, erreur = validate_number(numero_normalise)
    
    return est_valide, numero_normalise, erreur


def validate_pages(pages_brut: str) -> Tuple[bool, Optional[str]]:
    """
    Valide le nombre de pages reelles (Colonne K)
    
    Regles:
    - Doit etre numerique
    - DOIT ETRE > 0 (pages = 0 est une ERREUR)
    - Minimum: 1 page
    
    Retour: (valide, message_erreur)
    """
    # Verifier vide
    if not pages_brut:
        return False, "Pages vide"
    
    # Verifier numerique
    try:
        nb_pages = int(str(pages_brut).strip())
    except ValueError:
        return False, f"Pages invalides: '{pages_brut}' n'est pas numerique"
    
    # REGLE STRICTE: Pages = 0 est une ERREUR
    if nb_pages <= 0:
        return False, f"Pages invalide: {nb_pages} (doit etre >= {MIN_PAGES})"
    
    # Valide
    return True, None


def validate_entry(row: dict) -> dict:
    """
    Valide une ligne complete (toutes les colonnes critiques)
    
    Entree: row = {0: 'fax_id', 1: 'user', 3: 'SF', 7: '0145221134', 10: '5', ...}
    
    Retour: {
        'valide': True/False,
        'erreurs': [],
        'mode': 'SF' ou 'RF',
        'numero_original': '0145221134',
        'numero_normalise': '33145221134',
        'pages': '5',
        'details': {...}
    }
    """
    erreurs = []
    
    # Extraire les colonnes critiques
    mode_brut = str(row.get(3, '')).strip()
    numero_brut = str(row.get(7, '')).strip()
    pages_brut = str(row.get(10, '')).strip()
    
    # 1. VALIDER COLONNE D (Mode/Type FAX)
    mode_valide, erreur_mode = validate_fax_type(mode_brut)
    if not mode_valide:
        erreurs.append(erreur_mode)
    
    # 2. VALIDER COLONNE H (Numero appele)
    numero_valide, numero_norm, erreur_num = analyze_number(numero_brut)
    if not numero_valide:
        erreurs.append(erreur_num)
    
    # 3. VALIDER COLONNE K (Pages)
    pages_valide, erreur_pages = validate_pages(pages_brut)
    if not pages_valide:
        erreurs.append(erreur_pages)
    
    # Retourner resultat complet
    return {
        'valide': len(erreurs) == 0,
        'erreurs': erreurs,
        'mode': mode_brut if mode_valide else None,
        'numero_original': numero_brut,
        'numero_normalise': numero_norm if numero_valide else None,
        'pages': pages_brut,
        'details': {
            'mode_valide': mode_valide,
            'numero_valide': numero_valide,
            'pages_valide': pages_valide
        }
    }
