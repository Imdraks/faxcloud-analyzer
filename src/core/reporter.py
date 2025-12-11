"""
Module de génération des rapports et codes QR
Crée les rapports JSON et génère les QR codes pour accès mobile
"""

import logging
import json
import qrcode
from uuid import uuid4
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List

from .config import Config

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════
# CLASSE REPORT GENERATOR
# ═══════════════════════════════════════════════════════════════════════════

class ReportGenerator:
    """Généré les rapports et codes QR"""
    
    def __init__(self, db=None):
        """Initialise le générateur de rapports"""
        self.db = db
        Config.ensure_directories()
    
    @staticmethod
    def generate_report_id() -> str:
        """Génère un UUID pour le rapport"""
        return str(uuid4())
    
    def generate_qr_code(self, report_id: str, report_url: str) -> Optional[str]:
        """
        Génère un code QR pour un rapport
        Retourne le chemin du fichier PNG généré
        """
        try:
            # Créer le QR code
            qr = qrcode.QRCode(
                version=Config.QR_CODE_CONFIG['version'],
                error_correction=getattr(qrcode.constants, f"ERROR_CORRECT_{Config.QR_CODE_CONFIG['error_correction']}"),
                box_size=Config.QR_CODE_CONFIG['box_size'],
                border=Config.QR_CODE_CONFIG['border']
            )
            
            qr.add_data(report_url)
            qr.make(fit=True)
            
            # Créer l'image
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Sauvegarder
            qr_path = Config.REPORTS_QR_DIR / f"{report_id}.png"
            img.save(str(qr_path))
            
            logger.info(f"QR code généré: {qr_path}")
            return str(qr_path)
        
        except Exception as e:
            logger.error(f"Erreur lors de la génération du QR code: {e}")
            return None
    
    def save_report_json(self, report_data: Dict[str, Any]) -> str:
        """Sauvegarde le rapport en JSON"""
        try:
            report_id = report_data['rapport_id']
            json_path = Config.REPORTS_DIR / f"{report_id}.json"
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"Rapport JSON sauvegardé: {json_path}")
            return str(json_path)
        
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde du rapport JSON: {e}")
            raise
    
    def generate_report(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Génère un rapport complet (JSON + QR code)
        Retourne les informations du rapport généré
        """
        try:
            # Générer l'ID du rapport
            report_id = self.generate_report_id()
            
            # Construire le rapport
            report_data = {
                'rapport_id': report_id,
                'timestamp': datetime.now().isoformat(),
                'contract_id': analysis_data['contract_id'],
                'date_debut': analysis_data['date_debut'],
                'date_fin': analysis_data['date_fin'],
                'statistics': analysis_data['statistics'],
                'entries': analysis_data['entries'],
                'utilisateurs_stats': analysis_data.get('utilisateurs_stats', {}),
                'qr_path': None,
                'report_url': None
            }
            
            # Sauvegarder le JSON
            json_path = self.save_report_json(report_data)
            
            # Générer l'URL et le QR code
            report_url = f"{Config.BASE_REPORT_URL}/{report_id}"
            qr_path = self.generate_qr_code(report_id, report_url)
            
            # Mettre à jour le rapport
            report_data['qr_path'] = qr_path
            report_data['report_url'] = report_url
            
            # Sauvegarder dans la DB si disponible
            if self.db:
                self.db.save_report(report_data)
            
            logger.info(f"Rapport complet généré: {report_id}")
            
            return {
                'success': True,
                'rapport_id': report_id,
                'report_url': report_url,
                'qr_path': qr_path,
                'json_path': json_path,
                'message': f"Rapport {report_id} généré avec succès"
            }
        
        except Exception as e:
            logger.error(f"Erreur lors de la génération du rapport: {e}")
            return {
                'success': False,
                'message': str(e),
                'error': str(e)
            }
    
    @staticmethod
    def load_report_json(report_id: str) -> Optional[Dict[str, Any]]:
        """Charge un rapport JSON"""
        try:
            json_path = Config.REPORTS_DIR / f"{report_id}.json"
            
            if not json_path.exists():
                logger.warning(f"Rapport non trouvé: {json_path}")
                return None
            
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        except Exception as e:
            logger.error(f"Erreur lors de la lecture du rapport: {e}")
            return None
    
    @staticmethod
    def list_reports() -> List[Dict[str, Any]]:
        """Liste tous les rapports disponibles"""
        reports = []
        
        try:
            for json_file in sorted(Config.REPORTS_DIR.glob('*.json'), reverse=True):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    reports.append({
                        'id': data['rapport_id'],
                        'contract_id': data['contract_id'],
                        'timestamp': data['timestamp'],
                        'total_fax': data['statistics']['total_fax'],
                        'erreurs': data['statistics']['erreurs_totales'],
                        'taux_reussite': data['statistics']['taux_reussite']
                    })
                except Exception as e:
                    logger.warning(f"Erreur lors de la lecture de {json_file}: {e}")
        
        except Exception as e:
            logger.error(f"Erreur lors de la liste des rapports: {e}")
        
        return reports
    
    @staticmethod
    def generate_summary(report_data: Dict[str, Any]) -> str:
        """Génère un résumé textuel du rapport"""
        stats = report_data['statistics']
        
        summary = f"""
╔══════════════════════════════════════════════════════════════╗
║                    RÉSUMÉ DU RAPPORT                         ║
╚══════════════════════════════════════════════════════════════╝

📋 Informations Générales
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  • Rapport ID: {report_data['rapport_id']}
  • Contrat: {report_data['contract_id']}
  • Généré: {report_data['timestamp']}
  • Période: {report_data['date_debut']} à {report_data['date_fin']}

📊 Statistiques FAX
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  • Total FAX: {stats['total_fax']}
    - Envoyés (SF): {stats['fax_envoyes']}
    - Reçus (RF): {stats['fax_recus']}
  
  • Pages:
    - Totales: {stats['pages_totales']}
    - Envoyées: {stats['pages_envoyees']}
    - Reçues: {stats['pages_recues']}

⚠️  Erreurs et Qualité
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  • Erreurs détectées: {stats['erreurs_totales']}
  • Taux de réussite: {stats['taux_reussite']:.2f}%
  • Taux d'erreur: {100 - stats['taux_reussite']:.2f}%

"""
        
        # Ajouter les statistiques par utilisateur si disponibles
        if report_data.get('utilisateurs_stats'):
            summary += "👥 Statistiques par Utilisateur\n"
            summary += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            
            for utilisateur, stats_user in report_data['utilisateurs_stats'].items():
                total = stats_user['total']
                valides = stats_user['valides']
                taux = (valides / total * 100) if total > 0 else 0
                
                summary += f"  • {utilisateur}\n"
                summary += f"    - Total: {total} | Valides: {valides} | Erreurs: {stats_user['erreurs']}\n"
                summary += f"    - Réussite: {taux:.1f}%\n"
        
        return summary
