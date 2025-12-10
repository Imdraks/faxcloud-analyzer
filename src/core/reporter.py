"""
Rapports - Generation rapports JSON et QR codes
"""
import logging
import json
import uuid
from pathlib import Path
from typing import Dict
from datetime import datetime

import config

logger = logging.getLogger(__name__)

try:
    import qrcode
    QRCODE_OK = True
except ImportError:
    QRCODE_OK = False
    logger.warning("qrcode non disponible - QR codes desactives")


def generate_report(analysis: Dict) -> Dict:
    """Genere rapport JSON et QR code"""
    try:
        report_id = str(uuid.uuid4())
        logger.info("=" * 70)
        logger.info("RAPPORT")
        logger.info("=" * 70)
        logger.info(f"ID: {report_id}")
        
        # Creer dossiers
        reports_dir = config.DIRS['reports_json']
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        qr_dir = config.DIRS['reports_qr']
        qr_dir.mkdir(parents=True, exist_ok=True)
        
        # Generer QR code
        qr_path = ""
        if QRCODE_OK:
            try:
                qr_url = f"http://localhost:8000/reports/{report_id}"
                qr = qrcode.QRCode(version=1, box_size=10, border=4)
                qr.add_data(qr_url)
                qr.make(fit=True)
                
                img = qr.make_image(fill_color="black", back_color="white")
                qr_file = qr_dir / f"{report_id}.png"
                img.save(str(qr_file))
                qr_path = str(qr_file).replace("\\", "/")
                logger.info(f"QR code: {qr_file.name}")
            except Exception as e:
                logger.warning(f"Erreur QR: {e}")
        
        # Creer rapport JSON
        report_json = {
            "report_id": report_id,
            "timestamp": datetime.now().isoformat(),
            "contract_id": analysis.get("contract_id", ""),
            "date_debut": analysis.get("date_debut", ""),
            "date_fin": analysis.get("date_fin", ""),
            "statistics": analysis.get("statistics", {}),
            "entries": analysis.get("entries", []),
            "qr_code_path": qr_path,
            "report_url": f"/reports/{report_id}"
        }
        
        # Sauvegarder JSON
        report_file = reports_dir / f"{report_id}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_json, f, indent=2, ensure_ascii=False)
        
        logger.info(f"JSON: {report_file.name}")
        logger.info("=" * 70)
        
        return {
            "success": True,
            "report_id": report_id,
            "report_url": f"/reports/{report_id}",
            "qr_path": qr_path,
            "message": "Rapport OK"
        }
    
    except Exception as e:
        logger.error(f"Erreur rapport: {e}")
        return {
            "success": False,
            "report_id": "",
            "report_url": "",
            "qr_path": "",
            "message": str(e)
        }


def load_report_json(report_id: str) -> Dict:
    """Charge un rapport JSON"""
    try:
        report_file = config.DIRS['reports_json'] / f"{report_id}.json"
        with open(report_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return None


def generate_summary(report_json: Dict) -> str:
    """Genere un resume texte du rapport"""
    if not report_json:
        return "Rapport non trouve"
    
    stats = report_json.get("statistics", {})
    
    summary = f"""
RAPPORT FAXCLOUD
================

ID: {report_json.get('report_id', 'N/A')}
Contrat: {report_json.get('contract_id', 'N/A')}
Periode: {report_json.get('date_debut', 'N/A')} a {report_json.get('date_fin', 'N/A')}
Genere: {report_json.get('timestamp', 'N/A')}

STATISTIQUES
============

Total FAX: {stats.get('total_fax', 0)}
  - Envoyes: {stats.get('fax_envoyes', 0)}
  - Recus: {stats.get('fax_recus', 0)}

Pages: {stats.get('pages_totales', 0)}
  - Envoyees: {stats.get('pages_envoyees', 0)}
  - Recues: {stats.get('pages_recues', 0)}

Erreurs: {stats.get('erreurs_totales', 0)}
Taux reussite: {stats.get('taux_reussite', 0):.2f}%

ERREURS PAR TYPE
================
"""
    
    for type_err, count in stats.get('erreurs_par_type', {}).items():
        summary += f"{type_err}: {count}\n"
    
    summary += f"\nUTILISATEURS\n============\n"
    
    for user, count in sorted(stats.get('envois_par_utilisateur', {}).items()):
        errors = stats.get('erreurs_par_utilisateur', {}).get(user, 0)
        success = count - errors
        rate = (success / count * 100) if count > 0 else 0
        summary += f"{user}: {count} FAX ({rate:.1f}% OK)\n"
    
    return summary
