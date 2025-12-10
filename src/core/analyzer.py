"""
Analyse - Traitement des donnees et calcul des statistiques
"""
import logging
from typing import Dict, List
from collections import defaultdict
import validation_rules

logger = logging.getLogger(__name__)


def analyze_entry(row: Dict) -> Dict:
    """Analyse une ligne: valide numero (col 7), pages (col 10), mode (col 3)"""
    erreurs = []
    
    # Colonne 0: Fax ID
    fax_id = row.get(0, "")
    
    # Colonne 1: Utilisateur
    utilisateur = row.get(1, "INCONNU").strip() or "INCONNU"
    
    # Colonne 3: Mode
    mode_brut = row.get(3, "")
    mode_valid, mode_error = validation_rules.validate_fax_type(mode_brut)
    if not mode_valid:
        erreurs.append(mode_error)
        mode = None
    else:
        mode = mode_brut.strip().upper()
    
    # Colonne 7: Numero appele
    numero_brut = row.get(7, "")
    est_numero_valide, numero_normalise, numero_error = validation_rules.analyze_number(numero_brut)
    if not est_numero_valide:
        erreurs.append(numero_error)
    
    # Colonne 10: Pages
    pages_brut = row.get(10, "")
    pages_valid, pages_error = validation_rules.validate_pages(pages_brut)
    try:
        nb_pages = int(str(pages_brut).strip()) if pages_valid else 0
    except:
        nb_pages = 0
    
    if not pages_valid:
        erreurs.append(pages_error)
    
    # Valide si pas d'erreurs
    est_valide = len(erreurs) == 0 and est_numero_valide and mode_valid and pages_valid
    
    return {
        "fax_id": fax_id,
        "utilisateur": utilisateur,
        "mode": mode,
        "numero_original": numero_brut,
        "numero_normalise": numero_normalise,
        "pages": nb_pages,
        "valide": est_valide,
        "erreurs": erreurs
    }


def analyze_data(rows: List[Dict], contract_id: str, date_debut: str, date_fin: str) -> Dict:
    """Analyse toutes les lignes et calcule les stats"""
    logger.info("=" * 70)
    logger.info("ANALYSE")
    logger.info("=" * 70)
    
    entries = []
    total_fax = 0
    fax_envoyes = 0
    fax_recus = 0
    pages_envoyees = 0
    pages_recues = 0
    pages_totales = 0
    erreurs_totales = 0
    
    envois_par_utilisateur = defaultdict(int)
    erreurs_par_utilisateur = defaultdict(int)
    erreurs_par_type = defaultdict(int)
    pages_par_utilisateur = defaultdict(int)
    
    logger.info(f"Traitement {len(rows)} lignes...")
    
    for idx, row in enumerate(rows, 1):
        if idx % 1000 == 0:
            logger.info(f"  {idx}/{len(rows)}...")
        
        entry = analyze_entry(row)
        entries.append(entry)
        
        utilisateur = entry["utilisateur"]
        total_fax += 1
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
        
        # Compter erreurs
        if not entry["valide"]:
            erreurs_totales += 1
            erreurs_par_utilisateur[utilisateur] += 1
            
            for erreur in entry["erreurs"]:
                if "vide" in erreur.lower():
                    erreurs_par_type["Numero vide"] += 1
                elif "longueur" in erreur.lower():
                    erreurs_par_type["Longueur incorrecte"] += 1
                elif "indicatif" in erreur.lower():
                    erreurs_par_type["Indicatif invalide"] += 1
                elif "mode" in erreur.lower():
                    erreurs_par_type["Mode invalide"] += 1
                elif "pages" in erreur.lower():
                    erreurs_par_type["Pages invalides"] += 1
                else:
                    erreurs_par_type["Autre"] += 1
    
    taux_reussite = (100 * (total_fax - erreurs_totales) / total_fax) if total_fax > 0 else 0
    
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
    
    logger.info(f"Analyse OK: {total_fax} FAX, {erreurs_totales} erreurs, {taux_reussite:.1f}% reussite")
    logger.info("=" * 70)
    
    return {
        "contract_id": contract_id,
        "date_debut": date_debut,
        "date_fin": date_fin,
        "statistics": statistics,
        "entries": entries
    }
