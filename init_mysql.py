#!/usr/bin/env python3
"""
Script d'initialisation MySQL - FaxCloud Analyzer
Lance l'initialisation de la base de données MySQL
"""

import sys
import logging
from pathlib import Path

# Ajouter src au chemin Python
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Importer les modules
try:
    from core.config import Config
    from core.db_mysql import DatabaseMySQL
except ImportError as e:
    print(f"❌ Erreur d'import: {e}")
    print("Assurez-vous que vous êtes dans le répertoire du projet")
    sys.exit(1)

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_mysql_connection():
    """Teste la connexion à MySQL"""
    print("\n" + "="*60)
    print("🔍 Test de connexion MySQL")
    print("="*60)
    
    try:
        db = DatabaseMySQL()
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        print(f"✅ Connexion MySQL réussie!")
        print(f"   Version MySQL: {version}")
        return True
    except Exception as e:
        print(f"❌ Erreur connexion MySQL: {e}")
        return False

def init_mysql():
    """Initialise la base de données MySQL"""
    print("\n" + "="*60)
    print("🗄️  Initialisation de la base de données MySQL")
    print("="*60)
    
    try:
        db = DatabaseMySQL()
        db.initialize()
        print(f"\n✅ Base de données initialisée avec succès!")
        print(f"   - Tables créées: reports, fax_entries, analysis_history")
        return True
    except Exception as e:
        print(f"\n❌ Erreur initialisation: {e}")
        return False

def check_tables():
    """Vérifie les tables créées"""
    print("\n" + "="*60)
    print("📊 Vérification des tables")
    print("="*60)
    
    try:
        db = DatabaseMySQL()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Récupérer les tables
        cursor.execute("""
            SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_SCHEMA = %s
        """, (Config.MYSQL_CONFIG['database'],))
        
        tables = [row[0] for row in cursor.fetchall()]
        
        if tables:
            print(f"\n✅ Tables trouvées:")
            for table in tables:
                # Récupérer les colonnes
                cursor.execute(f"DESCRIBE {table}")
                columns = cursor.fetchall()
                print(f"\n   📌 Table: {table}")
                print(f"      Colonnes: {len(columns)}")
                for col in columns:
                    print(f"        - {col[0]} ({col[1]})")
        else:
            print(f"\n⚠️  Aucune table trouvée")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Erreur: {e}")

def main():
    """Fonction principale"""
    print("\n" + "█"*60)
    print("█" + " "*58 + "█")
    print("█  FaxCloud Analyzer - Initialisation MySQL" + " "*17 + "█")
    print("█" + " "*58 + "█")
    print("█"*60)
    
    # Test de connexion
    if not test_mysql_connection():
        print("\n⚠️  Vérifiez que WampServer est démarré et MySQL est actif")
        print("   Consultez phpMyAdmin pour vérifier: http://localhost/phpmyadmin")
        sys.exit(1)
    
    # Initialisation
    if not init_mysql():
        sys.exit(1)
    
    # Vérification des tables
    check_tables()
    
    # Statistiques
    print("\n" + "="*60)
    print("📈 Statistiques globales")
    print("="*60)
    
    try:
        db = DatabaseMySQL()
        stats = db.get_statistics()
        print(f"\n   Rapports: {stats.get('total_reports', 0)}")
        print(f"   FAX total: {stats.get('total_fax', 0)}")
        print(f"   Erreurs: {stats.get('total_errors', 0)}")
        print(f"   Taux réussite moyen: {stats.get('avg_success_rate', 0)}%")
        print(f"   Utilisateurs uniques: {stats.get('users_count', 0)}")
    except Exception as e:
        print(f"\n⚠️  Impossible de récupérer les statistiques: {e}")
    
    print("\n" + "█"*60)
    print("✅ Initialisation terminée avec succès!")
    print("█"*60 + "\n")

if __name__ == "__main__":
    main()
