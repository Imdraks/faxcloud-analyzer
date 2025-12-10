"""
Module de génération de rapports et QR codes
Responsabilités:
- Génération UUID pour les rapports
- Création des QR codes PNG
- Formatage des rapports JSON
- Sauvegarde des fichiers
"""

import json
import logging
import uuid
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

import config

logger = logging.getLogger(__name__)

# Essayer d'importer qrcode, sinon le signaler
try:
    import qrcode
    from PIL import Image
    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False
    logger.warning("⚠️  qrcode/Pillow non installé - QR codes désactivés")

# ═══════════════════════════════════════════════════════════════════════════
# GÉNÉRATION RAPPORT
# ═══════════════════════════════════════════════════════════════════════════

def generate_report(analysis: Dict) -> Dict:
    """
    Génère un rapport complet avec tous les fichiers associés
    
    Args:
        analysis: Résultats de l'analyse
    
    Returns:
        {
            "success": bool,
            "report_id": str,
            "report_url": str,
            "qr_path": str,
            "message": str
        }
    """
    try:
        # Générer l'UUID du rapport
        report_id = str(uuid.uuid4())
        logger.info(f"Génération rapport: {report_id}")
        
        # Créer le dossier reports si nécessaire
        reports_dir = config.DIRS['reports_json']
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Générer le QR code
        qr_path = ""
        if QRCODE_AVAILABLE:
            qr_path = generate_qr_code(
                report_id,
                base_url=config.REPORTS_BASE_URL
            )
            logger.info(f"✓ QR code généré: {qr_path}")
        else:
            logger.warning("⚠️  QR code non généré (qrcode non installé)")
        
        # Formater le rapport JSON
        report_json = {
            "report_id": report_id,
            "timestamp": datetime.now().isoformat(),
            "contract_id": analysis.get("contract_id", ""),
            "date_debut": analysis.get("date_debut", ""),
            "date_fin": analysis.get("date_fin", ""),
            "statistics": analysis.get("statistics", {}),
            "entries": analysis.get("entries", []),
            "qr_code_url": f"/reports_qr/{report_id}.png" if qr_path else "",
            "report_url": f"/reports/{report_id}"
        }
        
        # Sauvegarder le rapport JSON
        report_file = reports_dir / f"{report_id}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_json, f, indent=2, ensure_ascii=False)
        logger.info(f"✓ Rapport JSON sauvegardé: {report_file}")
        
        # Importer le module db seulement si nécessaire
        try:
            import db
            db.insert_report_to_db(report_id, report_json, qr_path)
            logger.info(f"✓ Rapport inséré en base de données")
        except Exception as e:
            logger.warning(f"⚠️  Base de données non disponible: {e}")
        
        return {
            "success": True,
            "report_id": report_id,
            "report_url": f"/reports/{report_id}",
            "qr_path": qr_path,
            "message": f"Rapport généré avec succès: {report_id}"
        }
    
    except Exception as e:
        error_msg = f"Erreur génération rapport: {str(e)}"
        logger.error(error_msg)
        return {
            "success": False,
            "report_id": "",
            "report_url": "",
            "qr_path": "",
            "message": error_msg
        }


# ═══════════════════════════════════════════════════════════════════════════
# GÉNÉRATION QR CODE
# ═══════════════════════════════════════════════════════════════════════════

def generate_qr_code(
    report_id: str,
    base_url: str = config.REPORTS_BASE_URL
) -> str:
    """
    Génère un QR code PNG pour un rapport
    
    Args:
        report_id: UUID du rapport
        base_url: URL de base (défaut: http://localhost:8000/reports)
    
    Returns:
        Chemin du fichier PNG généré
        Exemple: "reports_qr/a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6.png"
    """
    if not QRCODE_AVAILABLE:
        logger.warning("qrcode non disponible")
        return ""
    
    try:
        # Créer le dossier
        qr_dir = config.DIRS['reports_qr']
        qr_dir.mkdir(parents=True, exist_ok=True)
        
        # Construire l'URL cible
        target_url = f"{base_url}/{report_id}"
        logger.info(f"Génération QR pour URL: {target_url}")
        
        # Créer le QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=config.QR_CONFIG.get('box_size', 10),
            border=config.QR_CONFIG.get('border', 4),
        )
        
        qr.add_data(target_url)
        qr.make(fit=True)
        
        # Créer l'image
        img = qr.make_image(
            fill_color=config.QR_CONFIG.get('fill_color', 'black'),
            back_color=config.QR_CONFIG.get('back_color', 'white')
        )
        
        # Sauvegarder le fichier
        file_path = qr_dir / f"{report_id}.png"
        img.save(str(file_path))
        
        logger.info(f"✓ QR code créé: {file_path}")
        
        # Retourner le chemin relatif
        return str(file_path).replace("\\", "/")
    
    except Exception as e:
        logger.error(f"✗ Erreur génération QR: {str(e)}")
        return ""


# ═══════════════════════════════════════════════════════════════════════════
# SAUVEGARDE ET EXPORT
# ═══════════════════════════════════════════════════════════════════════════

def save_report_json(report_id: str, report_json: Dict) -> bool:
    """
    Sauvegarde un rapport au format JSON
    """
    try:
        reports_dir = config.DIRS['reports_json']
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = reports_dir / f"{report_id}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(report_json, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✓ Rapport JSON sauvegardé: {file_path}")
        return True
    
    except Exception as e:
        logger.error(f"✗ Erreur sauvegarde JSON: {e}")
        return False


def load_report_json(report_id: str) -> Optional[Dict]:
    """
    Charge un rapport JSON depuis le disque
    """
    try:
        reports_dir = config.DIRS['reports_json']
        file_path = reports_dir / f"{report_id}.json"
        
        if not file_path.exists():
            logger.warning(f"Rapport non trouvé: {file_path}")
            return None
        
        with open(file_path, 'r', encoding='utf-8') as f:
            report_json = json.load(f)
        
        return report_json
    
    except Exception as e:
        logger.error(f"✗ Erreur lecture rapport: {e}")
        return None


def list_reports() -> list:
    """
    Liste tous les rapports générés
    """
    try:
        reports_dir = config.DIRS['reports_json']
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        reports = []
        for file in reports_dir.glob("*.json"):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    report = json.load(f)
                    reports.append({
                        "id": report.get("report_id", ""),
                        "timestamp": report.get("timestamp", ""),
                        "contract_id": report.get("contract_id", ""),
                        "total_fax": report.get("statistics", {}).get("total_fax", 0),
                        "erreurs": report.get("statistics", {}).get("erreurs_totales", 0),
                        "taux_reussite": report.get("statistics", {}).get("taux_reussite", 0.0)
                    })
            except Exception as e:
                logger.warning(f"Erreur lecture rapport {file}: {e}")
                continue
        
        # Trier par timestamp (plus récent en premier)
        reports.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        return reports
    
    except Exception as e:
        logger.error(f"✗ Erreur listing rapports: {e}")
        return []


# ═══════════════════════════════════════════════════════════════════════════
# GÉNÉRATION DE RÉSUMÉS
# ═══════════════════════════════════════════════════════════════════════════

def generate_summary(report_json: Dict) -> str:
    """
    Génère un résumé texte d'un rapport
    """
    stats = report_json.get("statistics", {})
    
    summary = f"""
╔════════════════════════════════════════════════════════════════╗
║                   RAPPORT FaxCloud                            ║
╚════════════════════════════════════════════════════════════════╝

ID Rapport:           {report_json.get('report_id', 'N/A')}
Contrat:              {report_json.get('contract_id', 'N/A')}
Période:              {report_json.get('date_debut', 'N/A')} à {report_json.get('date_fin', 'N/A')}
Généré:               {report_json.get('timestamp', 'N/A')}

─────────────────────────────────────────────────────────────────

STATISTIQUES GLOBALES

Total FAX:            {stats.get('total_fax', 0)}
  ├─ Envoyés:        {stats.get('fax_envoyes', 0)}
  └─ Reçus:          {stats.get('fax_recus', 0)}

Pages totales:        {stats.get('pages_totales', 0)}

Erreurs:              {stats.get('erreurs_totales', 0)}
Taux de réussite:     {stats.get('taux_reussite', 0.0):.2f}%

─────────────────────────────────────────────────────────────────

ERREURS PAR TYPE

Numéros vides:        {stats.get('erreurs_par_type', {}).get('numero_vide', 0)}
Longueur incorrecte:  {stats.get('erreurs_par_type', {}).get('longueur_incorrecte', 0)}
Ne commence pas 33:   {stats.get('erreurs_par_type', {}).get('ne_commence_pas_33', 0)}
Caractères invalides: {stats.get('erreurs_par_type', {}).get('caracteres_invalides', 0)}

─────────────────────────────────────────────────────────────────

UTILISATEURS

Total utilisateurs:   {len(stats.get('envois_par_utilisateur', {}))}

"""
    
    if stats.get('envois_par_utilisateur'):
        summary += "\nEnvois par utilisateur:\n"
        for user, count in sorted(stats['envois_par_utilisateur'].items()):
            errors = stats.get('erreurs_par_utilisateur', {}).get(user, 0)
            success = count - errors
            success_rate = (success / count * 100) if count > 0 else 0
            summary += f"  • {user}: {count} FAX ({success_rate:.1f}% réussite)\n"
    
    summary += "\n" + "═" * 63 + "\n"
    
    return summary


# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    config.ensure_directories()
    
    print("✅ Module reporter prêt")
    
    # Exemple de test
    test_analysis = {
        "contract_id": "CONTRACT_001",
        "date_debut": "2024-12-01",
        "date_fin": "2024-12-10",
        "statistics": {
            "total_fax": 150,
            "fax_envoyes": 95,
            "fax_recus": 55,
            "pages_totales": 412,
            "erreurs_totales": 12,
            "taux_reussite": 92.0,
            "erreurs_par_type": {
                "numero_vide": 2,
                "longueur_incorrecte": 5,
                "ne_commence_pas_33": 3,
                "caracteres_invalides": 2
            },
            "envois_par_utilisateur": {
                "Jean Dupont": 45,
                "Marie Martin": 38,
                "Pierre Leblanc": 67
            },
            "erreurs_par_utilisateur": {
                "Jean Dupont": 2,
                "Marie Martin": 4,
                "Pierre Leblanc": 6
            }
        },
        "entries": []
    }
    
    result = generate_report(test_analysis)
    print(f"\nRésultat: {result}")
