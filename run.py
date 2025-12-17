#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FaxCloud Analyzer v3.0 - Entry Point
"""
import logging
import sys
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Print banner
print("\n" + "="*60)
print("FaxCloud Analyzer v3.0 - Starting")
print("="*60 + "\n")

try:
    from app import create_app
    
    logger.info("Creating Flask application...")
    app = create_app()
    
    logger.info("[OK] Application initialized successfully")
    logger.info("[OK] Starting Flask server...")
    logger.info("[WEB] Access: http://127.0.0.1:5000")
    logger.info("[ADMIN] Admin: http://127.0.0.1:5000/admin")
    logger.info("[API] API Health: http://127.0.0.1:5000/api/health")
    logger.info("="*60)
    
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=True,
        use_reloader=True
    )
    
except Exception as e:
    logger.error(f"Error: {e}", exc_info=True)
    sys.exit(1)
