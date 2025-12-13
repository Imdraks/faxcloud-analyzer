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
from .db import Database
from .ngrok_helper import NgrokHelper

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
        Génère un rapport complet et le sauvegarde en BDD
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
            
            # Générer l'URL et le QR code
            # Le QR code sera généré dynamiquement par l'endpoint /qrcode/<report_id>
            # Cela permet d'utiliser l'URL ngrok actuelle au moment où on l'accède
            
            # L'URL du rapport pour la page HTML
            report_url = f"{Config.BASE_REPORT_URL}/{report_id}"
            
            # Mettre à jour le rapport (QR code sera généré à la demande)
            report_data['qr_path'] = None  # Pas encore généré
            report_data['report_url'] = report_url
            
            # Sauvegarder dans la DB (principal)
            if self.db:
                self.db.save_report(report_data)
                logger.info(f"Rapport {report_id} sauvegardé en BDD")
                
                # Sauvegarder aussi dans l'historique des analyses
                try:
                    self.db.save_analysis(report_data)
                    logger.info(f"Analyse {report_id} sauvegardée en historique")
                except Exception as e:
                    logger.warning(f"Erreur lors de la sauvegarde de l'analyse en historique: {e}")
            
            logger.info(f"Rapport complet généré: {report_id}")
            
            return {
                'success': True,
                'rapport_id': report_id,
                'report_url': report_url,
                'qr_path': None,  # QR code généré dynamiquement
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
        """Charge un rapport depuis la base de données"""
        try:
            # Essayer de charger depuis la BDD d'abord
            db = Database()
            report = db.get_report(report_id)
            if report:
                return report
            
            # Fallback vers JSON pour compatibilité avec anciens rapports
            json_path = Config.REPORTS_DIR / f"{report_id}.json"
            
            if not json_path.exists():
                logger.warning(f"Rapport non trouvé: {json_path}")
                return None
            
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        except Exception as e:
            logger.error(f"Erreur lors de la lecture du rapport: {e}")
            return None
    
    def list_reports(self) -> List[Dict[str, Any]]:
        """Liste tous les rapports disponibles depuis la BDD"""
        if not self.db:
            logger.warning("Base de données non disponible")
            return []
        
        return self.db.list_reports()
    
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
