"""
Module d'analyse - Traitement complet des données FaxCloud
Responsabilités:
- Analyser chaque ligne (numéros, pages, type FAX)
- Valider contre les règles
- Calculer les statistiques
- Générer un rapport d'analyse
"""

import logging
from typing import Dict, List, Optional
from collections import defaultdict

import validation_rules

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════
# ANALYSE DE LIGNES
# ═══════════════════════════════════════════════════════════════════════════

def analyze_entry(row: Dict) -> Dict:
    """
    Analyse une ligne complète d'export FaxCloud
    
    Vérifie:
    1. Colonne H (Numéro appelé): valide
    2. Colonne K (Nombre de pages): valide
    3. Colonne D (Mode): SF ou RF
    
    Args:
        row: Dictionnaire avec indices 0-13
             0=FaxID, 1=User, 2=Reseller, 3=Mode, 4=Email,
             5=DateTime, 6=NumEnvoi, 7=NumAppele, 8=IntlCall,
             9=InternalCall, 10=Pages, 11=Duration, 12=BilledPages, 13=BillingType
    
    Returns:
        Dict avec résultat complet de l'analyse
    """
    erreurs = []
    
    # Colonne A: Fax ID (0)
    fax_id = row.get(0, "")
    
    # Colonne B: Utilisateur (1)
    utilisateur = row.get(1, "INCONNU")
    if not utilisateur or utilisateur.strip() == "":
        utilisateur = "INCONNU"
    else:
        utilisateur = utilisateur.strip()
    
    # Colonne D: Mode (3)
    mode_brut = row.get(3, "")
    mode_valid, mode_error = validation_rules.validate_fax_type(mode_brut)
    if not mode_valid:
        erreurs.append(mode_error)
        mode = None
    else:
        mode = mode_brut.strip().upper()
    
    # Colonne F: Date/Heure (5)
    datetime_str = row.get(5, "")
    
    # Colonne H: Numéro appelé (7)
    numero_brut = row.get(7, "")
    numero_normalise, numero_error = validation_rules.analyze_number(numero_brut)[:2]
    est_numero_valide = validation_rules.analyze_number(numero_brut)[0]
    if not est_numero_valide:
        erreur_numero = validation_rules.analyze_number(numero_brut)[2]
        erreurs.append(erreur_numero)
    
    # Colonne K: Nombre de pages (10)
    pages_brut = row.get(10, "")
    pages_valid, pages_error = validation_rules.validate_pages(pages_brut)
    try:
        nb_pages = int(str(pages_brut).strip()) if pages_valid else 0
    except ValueError:
        nb_pages = 0
    
    if not pages_valid:
        erreurs.append(pages_error)
    
    # Déterminer si la ligne est valide globalement
    est_valide = len(erreurs) == 0 and est_numero_valide and mode_valid and pages_valid
    
    return {
        "fax_id": fax_id,
        "utilisateur": utilisateur,
        "mode": mode,
        "datetime": datetime_str,
        "numero_original": numero_brut,
        "numero_normalise": numero_normalise,
        "pages": nb_pages,
        "valide": est_valide,
        "erreurs": erreurs,
        "erreur_msg": "; ".join(erreurs) if erreurs else ""
    }


# ═══════════════════════════════════════════════════════════════════════════
# ANALYSE GLOBALE
# ═══════════════════════════════════════════════════════════════════════════

def analyze_data(
    rows: List[Dict],
    contract_id: str,
    date_debut: str,
    date_fin: str
) -> Dict:
    """
    Analyse complète de toutes les lignes
    Génère les statistiques globales et par utilisateur
    
    Args:
        rows: Liste des lignes normalisées
        contract_id: ID du contrat
        date_debut: Date de début (YYYY-MM-DD)
        date_fin: Date de fin (YYYY-MM-DD)
    
    Returns:
        Dict avec structure complète d'analyse
    """
    logger.info("=" * 70)
    logger.info("📊 ANALYSE DES DONNÉES")
    logger.info("=" * 70)
    
    # Analyseurs
    entries = []
    
    # Statistiques
    total_fax = 0
    fax_envoyes = 0
    fax_recus = 0
    pages_envoyees = 0
    pages_recues = 0
    pages_totales = 0
    erreurs_totales = 0
    
    # Dictionnaires pour statistiques détaillées
    envois_par_utilisateur = defaultdict(int)
    erreurs_par_utilisateur = defaultdict(int)
    erreurs_par_type = defaultdict(int)
    pages_par_utilisateur = defaultdict(int)
    
    # Analyser chaque ligne
    logger.info(f"\nTraitement de {len(rows)} lignes...")
    
    for idx, row in enumerate(rows, 1):
        if idx % 50 == 0:
            logger.info(f"  Traitement ligne {idx}/{len(rows)}...")
        
        # Analyser la ligne
        entry = analyze_entry(row)
        entries.append(entry)
        
        utilisateur = entry["utilisateur"]
        
        # Compter les FAX
        total_fax += 1
        
        # Compter par utilisateur
        envois_par_utilisateur[utilisateur] += 1
        
        # Compter par mode
        if entry["valide"]:
            if entry["mode"] == "SF":
                fax_envoyes += 1
                pages_envoyees += entry["pages"]
            elif entry["mode"] == "RF":
                fax_recus += 1
                pages_recues += entry["pages"]
            
            pages_totales += entry["pages"]
            pages_par_utilisateur[utilisateur] += entry["pages"]
        
        # Compter les erreurs
        if not entry["valide"]:
            erreurs_totales += 1
            erreurs_par_utilisateur[utilisateur] += 1
            
            # Compter les erreurs par type
            for erreur in entry["erreurs"]:
                # Normaliser les types d'erreurs
                if "vide" in erreur.lower():
                    erreurs_par_type["Numéro vide"] += 1
                elif "longueur" in erreur.lower():
                    erreurs_par_type["Longueur incorrecte"] += 1
                elif "indicatif" in erreur.lower() or "commence" in erreur.lower():
                    erreurs_par_type["Indicatif invalide"] += 1
                elif "type de fax" in erreur.lower():
                    erreurs_par_type["Type de FAX invalide"] += 1
                elif "pages" in erreur.lower():
                    erreurs_par_type["Pages invalides"] += 1
                else:
                    erreurs_par_type["Autre erreur"] += 1
    
    # Calculer le taux de réussite
    taux_reussite = (100 * (total_fax - erreurs_totales) / total_fax) if total_fax > 0 else 0
    
    # Construire le dictionnaire de statistiques
    statistics = {
        "total_fax": total_fax,
        "fax_envoyes": fax_envoyes,
        "fax_recus": fax_recus,
        "pages_envoyees": pages_envoyees,
        "pages_recues": pages_recues,
        "pages_totales": pages_totales,
        "erreurs_totales": erreurs_totales,
        "taux_reussite": taux_reussite,
        "erreurs_par_type": dict(erreurs_par_type),
        "envois_par_utilisateur": dict(envois_par_utilisateur),
        "erreurs_par_utilisateur": dict(erreurs_par_utilisateur),
        "pages_par_utilisateur": dict(pages_par_utilisateur),
    }
    
    # Log des résultats
    logger.info(f"\n✓ Analyse terminée")
    logger.info(f"  • Total FAX: {total_fax}")
    logger.info(f"  • Valides: {total_fax - erreurs_totales}")
    logger.info(f"  • Erreurs: {erreurs_totales}")
    logger.info(f"  • Taux réussite: {taux_reussite:.2f}%")
    logger.info(f"  • Pages totales: {pages_totales}")
    logger.info(f"    - Envoyées: {pages_envoyees}")
    logger.info(f"    - Reçues: {pages_recues}")
    logger.info(f"  • Utilisateurs: {len(envois_par_utilisateur)}")
    
    logger.info("=" * 70)
    
    return {
        "contract_id": contract_id,
        "date_debut": date_debut,
        "date_fin": date_fin,
        "statistics": statistics,
        "entries": entries
    }


# ═══════════════════════════════════════════════════════════════════════════
# TEST
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys
    from pathlib import Path
    
    logging.basicConfig(level=logging.INFO)
    
    # Test avec des données simulées
    print("📊 Module d'analyse prêt")
    
    test_rows = [
        {
            0: "FAX001",
            1: "Jean Dupont",
            2: "Revendeur A",
            3: "SF",
            4: "jean@example.com",
            5: "2024-12-01 10:00",
            6: "0123456789",
            7: "+33 1 45 22 11 34",
            8: "",
            9: "",
            10: "5",
            11: "120",
            12: "5",
            13: "Standard"
        },
        {
            0: "FAX002",
            1: "Marie Martin",
            2: "Revendeur B",
            3: "RF",
            4: "marie@example.com",
            5: "2024-12-01 11:00",
            6: "0123456789",
            7: "01 45 22 11 34",
            8: "",
            9: "",
            10: "3",
            11: "90",
            12: "3",
            13: "Standard"
        },
        {
            0: "FAX003",
            1: "Pierre Leblanc",
            2: "Revendeur A",
            3: "SF",
            4: "pierre@example.com",
            5: "2024-12-01 12:00",
            6: "0123456789",
            7: "",  # Numéro vide
            8: "",
            9: "",
            10: "2",
            11: "60",
            12: "2",
            13: "Standard"
        },
    ]
    
    result = analyze_data(test_rows, "CONTRACT_TEST", "2024-12-01", "2024-12-31")
    print(f"\nRésultat:\n{result}")
