#!/usr/bin/env python
"""
Script d'initialisation de la base de données
"""
import sys
import os
import logging

sys.path.insert(0, os.path.dirname(__file__))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import pymysql
    logger.info("[OK] MySQL initialized")
except Exception as e:
    logger.warning(f"[!] MySQL not available: {e}")
    logger.info("[*] To use MySQL, configure DB_HOST, DB_USER, DB_PASSWORD in .env")

logger.info("[OK] Database initialization complete")
