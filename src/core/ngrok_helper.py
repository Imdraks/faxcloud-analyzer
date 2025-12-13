"""
Module helper pour ngrok
Gère le tunnel public vers le serveur local
"""

import logging
import subprocess
import threading
import time
from typing import Optional
import os

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════
# NGROK HELPER
# ═══════════════════════════════════════════════════════════════════════════

class NgrokHelper:
    """Gère les tunnels ngrok"""
    
    _process = None
    _tunnel_url = None
    
    @staticmethod
    def start_tunnel_subprocess(port: int = 5000) -> Optional[str]:
        """Démarre ngrok en tant que subprocess"""
        try:
            # Lancer ngrok en subprocess
            cmd = ["ngrok", "http", str(port), "--log=stdout"]
            NgrokHelper._process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            logger.info(f"ngrok démarré (PID: {NgrokHelper._process.pid})")
            
            # Thread pour lire les logs de ngrok et trouver l'URL
            def read_ngrok_output():
                for line in NgrokHelper._process.stdout:
                    try:
                        logger.info(f"[ngrok] {line.strip()}")
                    except:
                        pass  # Ignore encoding issues
                    
                    if "url=" in line.lower() or "https://" in line:
                        try:
                            # Extraire l'URL
                            if "https://" in line:
                                start = line.find("https://")
                                end = line.find(" ", start)
                                if end == -1:
                                    end = line.find("\n", start)
                                url = line[start:end].strip()
                                NgrokHelper._tunnel_url = url
                                logger.info("=" * 60)
                                logger.info("SERVEUR ACCESSIBLE PUBLIQUEMENT!")
                                logger.info(f"URL PUBLIQUE: {url}")
                                logger.info("=" * 60)
                                logger.info("Partage ce lien avec tes clients!")
                                logger.info("")
                        except:
                            pass
            
            thread = threading.Thread(target=read_ngrok_output, daemon=True)
            thread.start()
            
            return "Ngrok démarré"
        
        except FileNotFoundError:
            logger.error("ngrok n'est pas installé ou n'est pas dans le PATH")
            logger.info("Installe ngrok: https://ngrok.com/download")
            return None
        
        except Exception as e:
            logger.error(f"Erreur au démarrage de ngrok: {e}")
            return None
    
    @staticmethod
    def get_public_url() -> Optional[str]:
        """Retourne l'URL publique du tunnel ngrok"""
        return NgrokHelper._tunnel_url
    
    @staticmethod
    def stop_tunnel():
        """Arrête le tunnel ngrok"""
        try:
            if NgrokHelper._process:
                NgrokHelper._process.terminate()
                NgrokHelper._process.wait(timeout=5)
                logger.info("Tunnel ngrok arrêté")
        except Exception as e:
            logger.warning(f"Erreur lors de l'arrêt du tunnel ngrok: {e}")
