#!/usr/bin/env python3
"""
Script d'initialisation MySQL - FaxCloud Analyzer
Lance l'initialisation de la base de données MySQL
"""

import sys
import logging
from pathlib import Path

# Ajouter src au chemin Python
sys.path.insert(0, str(Path(__file__).parent / 'src' / 'core'))

# Importer les modules
try:
    import config
    import db
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
        print(f"   Hôte: {config.MYSQL_CONFIG['host']}")
        print(f"   Port: {config.MYSQL_CONFIG['port']}")
        print(f"   Utilisateur: {config.MYSQL_CONFIG['user']}")
        return False

def init_mysql():
    """Initialise la base de données MySQL"""
    print("\n" + "="*60)
    print("🗄️  Initialisation de la base de données MySQL")
    print("="*60)
    
    print(f"\n📋 Configuration:")
    print(f"   Hôte: {config.MYSQL_CONFIG['host']}")
    print(f"   Port: {config.MYSQL_CONFIG['port']}")
    print(f"   Utilisateur: {config.MYSQL_CONFIG['user']}")
    print(f"   Base de données: {config.MYSQL_CONFIG['database']}")
    
    try:
        db.init_database()
        print(f"\n✅ Base de données initialisée avec succès!")
        print(f"   - Base créée: {config.MYSQL_CONFIG['database']}")
        print(f"   - Tables créées: reports, fax_entries")
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
        conn = db.get_db_connection()
        cursor = conn.cursor()
        
        # Récupérer les tables
        cursor.execute("""
            SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_SCHEMA = %s
        """, (config.MYSQL_CONFIG['database'],))
        
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
    
    stats = db.get_statistics()
    print(f"\n   Rapports: {stats['total_reports']}")
    print(f"   FAX total: {stats['total_fax']}")
    print(f"   Erreurs: {stats['total_errors']}")
    print(f"   Taux réussite moyen: {stats['avg_success_rate']}%")
    print(f"   Utilisateurs uniques: {stats['users_count']}")
    
    print("\n" + "█"*60)
    print("✅ Initialisation terminée avec succès!")
    print("█"*60 + "\n")

if __name__ == "__main__":
    main()
