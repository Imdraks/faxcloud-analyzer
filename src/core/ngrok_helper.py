"""
Module helper pour ngrok
Gère le tunnel public vers le serveur local
"""

import logging
from typing import Optional
import os

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════
# NGROK HELPER
# ═══════════════════════════════════════════════════════════════════════════

class NgrokHelper:
    """Gère les tunnels ngrok"""
    
    _tunnel_url = None
    
    @staticmethod
    def start_tunnel(port: int = 5000) -> Optional[str]:
        """Démarre un tunnel ngrok et retourne l'URL publique"""
        try:
            from pyngrok import ngrok
            
            # Vérifier si ngrok est déjà installé/disponible
            ngrok_path = os.environ.get('NGROK_PATH')
            if ngrok_path:
                ngrok.set_ngrok_path(ngrok_path)
            
            # Démarrer le tunnel
            public_url = ngrok.connect(port, "http")
            NgrokHelper._tunnel_url = str(public_url)
            
            logger.info(f"🌐 Tunnel ngrok démarré: {NgrokHelper._tunnel_url}")
            logger.info(f"✅ Serveur accessible publiquement!")
            logger.info(f"📱 Partage ce lien avec tes clients: {NgrokHelper._tunnel_url}")
            
            return NgrokHelper._tunnel_url
        
        except ImportError:
            logger.warning("pyngrok non installé. Pour accès public: pip install pyngrok")
            return None
        
        except Exception as e:
            logger.warning(f"Impossible de démarrer ngrok: {e}")
            logger.info("Le serveur est accessible en local uniquement: http://127.0.0.1:5000")
            return None
    
    @staticmethod
    def get_public_url() -> Optional[str]:
        """Retourne l'URL publique du tunnel ngrok"""
        return NgrokHelper._tunnel_url
    
    @staticmethod
    def stop_tunnel():
        """Arrête le tunnel ngrok"""
        try:
            from pyngrok import ngrok
            ngrok.kill()
            logger.info("Tunnel ngrok arrêté")
        except Exception as e:
            logger.warning(f"Erreur lors de l'arrêt du tunnel ngrok: {e}")
