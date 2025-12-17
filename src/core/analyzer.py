from __future__ import annotations

import logging
import re
import uuid
from datetime import datetime
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


def normalize_number(numero: str) -> str:
    digits = re.sub(r"\D", "", str(numero or ""))
    if digits.startswith("0") and len(digits) >= 1:
        digits = "33" + digits[1:]
    if digits.startswith("0033"):
        digits = "33" + digits[4:]
    if digits.startswith("+33"):
        digits = "33" + digits[3:]
    return digits


def validate_number(numero: str) -> Tuple[bool, str | None]:
    if not numero:
        return False, "Numéro vide"
    if len(numero) != 11:
        return False, "Longueur incorrecte"
    if not numero.startswith("33"):
        return False, "Indicatif invalide"
    if not numero.isdigit():
        return False, "Format invalide"
    return True, None


def _validate_pages(pages: int) -> Tuple[bool, str | None]:
    if pages is None:
        return False, "Pages manquantes"
    if pages < 1:
        return False, "Pages invalides"
    return True, None


def _normalize_row(row: Dict) -> Dict:
    numero_original = row.get("numero_appele")
    numero_normalise = normalize_number(numero_original)
    valide, erreur_num = validate_number(numero_normalise)

    pages_valide, erreur_pages = _validate_pages(row.get("pages", 0))
    erreurs = []
    if not valide and erreur_num:
        erreurs.append(erreur_num)
    if not pages_valide and erreur_pages:
        erreurs.append(erreur_pages)

    mode = row.get("mode", "").strip().upper()
    type_value = "send" if mode == "SF" else "receive"

    return {
        "id": str(uuid.uuid4()),
        "fax_id": row.get("fax_id"),
        "utilisateur": row.get("utilisateur"),
        "type": type_value,
        "numero_original": numero_original,
        "numero_normalise": numero_normalise,
        "valide": valide and pages_valide,
        "pages": row.get("pages", 0),
        "datetime": str(row.get("datetime")),
        "erreurs": erreurs,
    }


def analyze_data(rows: List[Dict], contract_id: str | None, date_debut: str | None, date_fin: str | None) -> Dict:
    logger.info("Analyse de %s lignes", len(rows))
    entries = [_normalize_row(row) for row in rows]

    total_fax = len(entries)
    fax_envoyes = sum(1 for e in entries if e["type"] == "send")
    fax_recus = total_fax - fax_envoyes
    pages_envoyees = sum(e["pages"] for e in entries if e["type"] == "send")
    pages_recues = sum(e["pages"] for e in entries if e["type"] == "receive")
    errors = [err for e in entries for err in e["erreurs"]]

    erreurs_totales = len(errors)
    taux_reussite = round(((total_fax - erreurs_totales) / total_fax) * 100, 2) if total_fax else 0.0

    erreur_counts: Dict[str, int] = {}
    for err in errors:
        erreur_counts[err] = erreur_counts.get(err, 0) + 1

    statistics = {
        "total_fax": total_fax,
        "fax_envoyes": fax_envoyes,
        "fax_recus": fax_recus,
        "pages_totales": pages_envoyees + pages_recues,
        "pages_envoyees": pages_envoyees,
        "pages_recues": pages_recues,
        "erreurs_totales": erreurs_totales,
        "taux_reussite": taux_reussite,
        "erreurs_par_type": erreur_counts,
    }

    return {
        "report_id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
        "contract_id": contract_id,
        "date_debut": date_debut,
        "date_fin": date_fin,
        "statistics": statistics,
        "entries": entries,
    }
