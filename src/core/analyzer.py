"""
Module d'analyse des données FaxCloud
Responsabilités:
- Normalisation des numéros de téléphone (via validation_rules)
- Validation des numéros (via validation_rules)
- Analyse complète des données
- Génération des statistiques
"""

import re
import logging
import uuid
from typing import Dict, List, Tuple
from datetime import datetime
import validation_rules

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════
# NORMALISATION DES NUMÉROS (déléguée à validation_rules)
# ═══════════════════════════════════════════════════════════════════════════

def normalize_number(raw_number: str) -> str:
    """
    Normalise un numéro de téléphone
    
    Utilise la logique officielle de validation_rules.py
    
    Exemples:
        "0622334455" → "33622334455"
        "+33622334455" → "33622334455"
        "33 6 22 33 44 55" → "33622334455"
        "0033622334455" → "33622334455"
        "INVALID" → ""
        "" → ""
    
    Args:
        raw_number: Numéro brut
    
    Returns:
        Numéro normalisé (11 chiffres commençant par 33)
    """
    return validation_rules.normalize_number(raw_number)


# ═══════════════════════════════════════════════════════════════════════════
# VALIDATION DES NUMÉROS (déléguée à validation_rules)
# ═══════════════════════════════════════════════════════════════════════════

def validate_number(numero_brut: str) -> Tuple[bool, str]:
    """
    Valide un numéro (brut)
    
    Utilise la logique officielle de validation_rules.py
    
    Règles:
        - Normalisation: supprime caractères non-numériques
        - Conversion: 0X → 33X, 0033X → 33X
        - Longueur exacte: 11 chiffres
        - Commence par: 33
    
    Args:
        numero_brut: Numéro brut avec caractères spéciaux
    
    Returns:
        Tuple[bool, str]: (est_valide, message_erreur)
    """
    est_valide, numero_norm, erreur = validation_rules.analyze_number(numero_brut)
    return est_valide, erreur


# ═══════════════════════════════════════════════════════════════════════════
# ANALYSE COMPLÈTE
# ═══════════════════════════════════════════════════════════════════════════

def analyze_data(
    rows: List[Dict],
    contract_id: str,
    date_debut: str,
    date_fin: str
) -> Dict:
    """
    Analyse l'intégralité des données importées
    Génère les statistiques et valide chaque entrée
    
    Args:
        rows: Liste des lignes importées
        contract_id: ID du contrat
        date_debut: Date de début (YYYY-MM-DD)
        date_fin: Date de fin (YYYY-MM-DD)
    
    Returns:
        {
            "entries": List[Dict],  # Entrées analysées
            "statistics": Dict,     # Statistiques
            "contract_id": str,
            "date_debut": str,
            "date_fin": str
        }
    """
    logger.info(f"Début analyse: {len(rows)} lignes")
    
    # Initialiser les structures
    entries = []
    statistics = {
        "total_fax": 0,
        "fax_envoyes": 0,
        "fax_recus": 0,
        "pages_totales": 0,
        "erreurs_totales": 0,
        "taux_reussite": 0.0,
        "erreurs_par_type": {
            "numero_vide": 0,
            "longueur_incorrecte": 0,
            "ne_commence_pas_33": 0,
            "caracteres_invalides": 0
        },
        "envois_par_utilisateur": {},
        "erreurs_par_utilisateur": {}
    }
    
    # Parcourir chaque ligne
    for row in rows:
        try:
            # Extraire les données (colonnes par index)
            fax_id = row.get('A', '')
            utilisateur = row.get('B', '')
            mode = row.get('D', '').upper()
            datetime_str = row.get('F', '')
            numero_appele = row.get('H', '')
            pages = row.get('K', 0)
            
            # Normaliser le numéro appelé
            numero_normalise = normalize_number(numero_appele)
            validation = validate_number(numero_normalise)
            
            # Déterminer le type
            if mode == "SF":
                type_fax = "send"
            elif mode == "RF":
                type_fax = "receive"
            else:
                type_fax = "unknown"
            
            # Créer l'entrée
            entry = {
                "id": str(uuid.uuid4()),
                "fax_id": fax_id,
                "utilisateur": utilisateur,
                "type": type_fax,
                "numero_original": numero_appele,
                "numero_normalise": numero_normalise,
                "valide": validation["is_valid"],
                "pages": int(pages),
                "datetime": datetime_str,
                "erreurs": validation["errors"]
            }
            entries.append(entry)
            
            # Mettre à jour les statistiques globales
            statistics["total_fax"] += 1
            
            if type_fax == "send":
                statistics["fax_envoyes"] += 1
            elif type_fax == "receive":
                statistics["fax_recus"] += 1
            
            statistics["pages_totales"] += int(pages)
            
            # Gérer les erreurs
            if not validation["is_valid"]:
                statistics["erreurs_totales"] += 1
                
                # Compter par type d'erreur
                for error_msg in validation["errors"]:
                    if "vide" in error_msg.lower():
                        statistics["erreurs_par_type"]["numero_vide"] += 1
                    elif "longueur" in error_msg.lower():
                        statistics["erreurs_par_type"]["longueur_incorrecte"] += 1
                    elif "33" in error_msg:
                        statistics["erreurs_par_type"]["ne_commence_pas_33"] += 1
                    elif "invalides" in error_msg.lower():
                        statistics["erreurs_par_type"]["caracteres_invalides"] += 1
            
            # Compter par utilisateur
            if utilisateur not in statistics["envois_par_utilisateur"]:
                statistics["envois_par_utilisateur"][utilisateur] = 0
            statistics["envois_par_utilisateur"][utilisateur] += 1
            
            if not validation["is_valid"]:
                if utilisateur not in statistics["erreurs_par_utilisateur"]:
                    statistics["erreurs_par_utilisateur"][utilisateur] = 0
                statistics["erreurs_par_utilisateur"][utilisateur] += 1
        
        except Exception as e:
            logger.warning(f"Erreur analyse ligne: {str(e)}")
            continue
    
    # Calculer le taux de réussite
    if statistics["total_fax"] > 0:
        reussis = statistics["total_fax"] - statistics["erreurs_totales"]
        statistics["taux_reussite"] = (reussis / statistics["total_fax"]) * 100
    else:
        statistics["taux_reussite"] = 0.0
    
    logger.info(f"✓ Analyse complète: {statistics['total_fax']} FAX, "
                f"{statistics['erreurs_totales']} erreurs, "
                f"{statistics['taux_reussite']:.2f}% réussite")
    
    return {
        "entries": entries,
        "statistics": statistics,
        "contract_id": contract_id,
        "date_debut": date_debut,
        "date_fin": date_fin
    }


# ═══════════════════════════════════════════════════════════════════════════
# STATISTIQUES PAR UTILISATEUR
# ═══════════════════════════════════════════════════════════════════════════

def get_user_stats(analysis: Dict) -> Dict:
    """
    Génère des statistiques détaillées par utilisateur
    """
    user_stats = {}
    
    for entry in analysis["entries"]:
        utilisateur = entry["utilisateur"]
        
        if utilisateur not in user_stats:
            user_stats[utilisateur] = {
                "total": 0,
                "envoyes": 0,
                "recus": 0,
                "pages": 0,
                "erreurs": 0,
                "valides": 0,
                "taux_reussite": 0.0
            }
        
        user_stats[utilisateur]["total"] += 1
        
        if entry["type"] == "send":
            user_stats[utilisateur]["envoyes"] += 1
        elif entry["type"] == "receive":
            user_stats[utilisateur]["recus"] += 1
        
        user_stats[utilisateur]["pages"] += entry["pages"]
        
        if entry["valide"]:
            user_stats[utilisateur]["valides"] += 1
        else:
            user_stats[utilisateur]["erreurs"] += 1
        
        # Calculer le taux
        if user_stats[utilisateur]["total"] > 0:
            user_stats[utilisateur]["taux_reussite"] = (
                user_stats[utilisateur]["valides"] / 
                user_stats[utilisateur]["total"] * 100
            )
    
    return user_stats


# ═══════════════════════════════════════════════════════════════════════════
# DÉTAILS DES ERREURS
# ═══════════════════════════════════════════════════════════════════════════

def get_error_details(analysis: Dict) -> Dict:
    """
    Retourne les détails des erreurs
    """
    errors = {
        "total": analysis["statistics"]["erreurs_totales"],
        "par_type": analysis["statistics"]["erreurs_par_type"],
        "entrees_invalides": [
            entry for entry in analysis["entries"]
            if not entry["valide"]
        ]
    }
    
    return errors


# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Exemples de test
    print("=== Tests de normalisation ===")
    tests = [
        "0622334455",
        "+33622334455",
        "33 6 22 33 44 55",
        "INVALID",
        "",
        "0133445566"
    ]
    
    for test in tests:
        normalized = normalize_number(test)
        validation = validate_number(normalized)
        print(f"'{test}' → '{normalized}' → Valide: {validation['is_valid']}")
        if validation['errors']:
            print(f"  Erreurs: {validation['errors']}")
