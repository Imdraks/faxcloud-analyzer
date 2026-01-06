#!/usr/bin/env python
"""
Script d'initialisation de la base de données
Crée les tables nécessaires dans MySQL ou SQLite
"""
import sys
import os
import logging

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def init_mysql():
    """Initialiser la base MySQL"""
    try:
        from src.core.db_mysql import DatabaseMySQL
        db = DatabaseMySQL()
        db.initialize()
        logger.info("✓ Base de données MySQL initialisée avec succès")
        return True
    except Exception as e:
        logger.warning(f"⚠ MySQL non disponible: {e}")
        return False


def init_sqlite():
    """Initialiser la base SQLite (fallback)"""
    try:
        from src.core.db import Database
        db = Database()
        db.init_database()
        logger.info("✓ Base de données SQLite initialisée avec succès")
        return True
    except Exception as e:
        logger.error(f"✗ Erreur SQLite: {e}")
        return False


def main():
    """Point d'entrée principal"""
    logger.info("=" * 50)
    logger.info("FaxCloud Analyzer - Initialisation BD")
    logger.info("=" * 50)
    
    # Essayer MySQL d'abord
    if init_mysql():
        logger.info("Mode: MySQL")
    else:
        # Fallback vers SQLite
        logger.info("Basculement vers SQLite...")
        if init_sqlite():
            logger.info("Mode: SQLite")
        else:
            logger.error("✗ Aucune base de données disponible")
            sys.exit(1)
    
    logger.info("=" * 50)
    logger.info("✓ Initialisation terminée")
    logger.info("=" * 50)


if __name__ == '__main__':
    main()
