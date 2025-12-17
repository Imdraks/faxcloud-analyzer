#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
FaxCloud Analyzer v3.0
Point d'entrée principal de l'application
"""
import os
import sys
import logging

# Ajouter le répertoire racine au path
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from config.settings import DEBUG, ENVIRONMENT

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    logger.info("="*60)
    logger.info("FaxCloud Analyzer v3.0 - Starting")
    logger.info(f"Environment: {ENVIRONMENT}")
    logger.info(f"Debug mode: {DEBUG}")
    logger.info("="*60)
    
    app = create_app()
    
    logger.info("[OK] Starting Flask server...")
    logger.info("[WEB] Access: http://127.0.0.1:5000")
    logger.info("[ADMIN] Admin: http://127.0.0.1:5000/admin")
    logger.info("[API] API Health: http://127.0.0.1:5000/api/health")
    logger.info("="*60)
    
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=DEBUG,
        use_reloader=False
    )
