#!/usr/bin/env python3
"""
Script de DEBUG - Test d'import et calculs des pages SF/RF
Lance directement sans la partie web Flask
"""

import sys
from pathlib import Path
from datetime import datetime

# Ajouter src au chemin
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from core.config import Config
from core.importer import FileImporter
from core.db_mysql import DatabaseMySQL

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION LOGGING
# ═══════════════════════════════════════════════════════════════════════════

Config.ensure_directories()
Config.setup_logging()
logger = Config.get_logger(__name__)

# ═══════════════════════════════════════════════════════════════════════════
# FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def print_header(title):
    """Affiche un header formaté"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def test_import(filepath):
    """Teste l'import d'un fichier"""
    print_header("🔄 TEST D'IMPORT")
    
    try:
        importer = FileImporter()
        result = importer.import_file(filepath)
        
        if not result.get('success'):
            print(f"❌ Erreur import: {result.get('errors')}")
            return None
        
        entries = result.get('data', [])
        print(f"✅ Import réussi: {len(entries)} entrées")
        return entries
    
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        return None

def analyze_entries(entries):
    """Analyse les entrées et affiche les stats"""
    print_header("📊 ANALYSE DES DONNEES")
    
    if not entries:
        print("❌ Aucune entrée à analyser")
        return None
    
    # Statistiques basiques
    total = len(entries)
    sf_count = sum(1 for e in entries if e.get('mode') == 'SF')
    rf_count = sum(1 for e in entries if e.get('mode') == 'RF')
    other_count = total - sf_count - rf_count
    
    print(f"\n📈 Compteurs:")
    print(f"   Total: {total}")
    print(f"   Envoyés (SF): {sf_count}")
    print(f"   Reçus (RF): {rf_count}")
    print(f"   Autres: {other_count}")
    
    # Pages
    pages_sf = sum(e.get('pages', 0) or 0 for e in entries if e.get('mode') == 'SF')
    pages_rf = sum(e.get('pages', 0) or 0 for e in entries if e.get('mode') == 'RF')
    pages_total = pages_sf + pages_rf
    
    print(f"\n📄 Pages:")
    print(f"   Pages SF (envoyées): {pages_sf}")
    print(f"   Pages RF (reçues): {pages_rf}")
    print(f"   Total pages: {pages_total}")
    
    # Erreurs
    errors = sum(1 for e in entries if e.get('erreurs'))
    success_rate = ((total - errors) / total * 100) if total > 0 else 0
    
    print(f"\n✔️  Erreurs:")
    print(f"   Erreurs: {errors}")
    print(f"   Taux réussite: {success_rate:.2f}%")
    
    # Quelques exemples
    print(f"\n📋 Exemples d'entrées:")
    for i, entry in enumerate(entries[:3]):
        print(f"\n   Entrée {i+1}:")
        print(f"      FAX ID: {entry.get('fax_id', 'N/A')}")
        print(f"      Mode: {entry.get('mode', 'N/A')}")
        print(f"      Pages: {entry.get('pages', 0)}")
        print(f"      Numero: {entry.get('numero', 'N/A')}")
        print(f"      Utilisateur: {entry.get('utilisateur', 'N/A')}")
    
    return {
        'total': total,
        'sf': sf_count,
        'rf': rf_count,
        'pages_sf': pages_sf,
        'pages_rf': pages_rf,
        'errors': errors,
        'success_rate': success_rate
    }

def save_to_db(entries, filename):
    """Sauvegarde les entrées en base de données"""
    print_header("💾 SAUVEGARDE EN BASE DE DONNEES")
    
    try:
        db = DatabaseMySQL()
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Créer rapport
        from uuid import uuid4
        import json
        
        report_id = 'debug_' + str(uuid4())[:12]
        
        # Calculs
        total_fax = len(entries)
        fax_envoyes = sum(1 for e in entries if e.get('mode') == 'SF')
        fax_recus = sum(1 for e in entries if e.get('mode') == 'RF')
        erreurs_totales = sum(1 for e in entries if e.get('erreurs'))
        taux_reussite = ((total_fax - erreurs_totales) / total_fax * 100) if total_fax > 0 else 0.0
        pages_sf = sum(e.get('pages', 0) or 0 for e in entries if e.get('mode') == 'SF')
        pages_rf = sum(e.get('pages', 0) or 0 for e in entries if e.get('mode') == 'RF')
        pages_totales = pages_sf + pages_rf
        
        print(f"\n📝 Insertion du rapport:")
        print(f"   Report ID: {report_id}")
        print(f"   Fichier: {filename}")
        print(f"   Total FAX: {total_fax}")
        print(f"   Envoyés: {fax_envoyes}")
        print(f"   Reçus: {fax_recus}")
        print(f"   Pages SF: {pages_sf}")
        print(f"   Pages RF: {pages_rf}")
        print(f"   Taux réussite: {taux_reussite:.2f}%")
        
        # Insérer rapport
        cursor.execute("""
            INSERT INTO reports (
                id, date_rapport, contract_id, date_debut, date_fin,
                fichier_source, total_fax, fax_envoyes, fax_recus,
                pages_totales, pages_envoyees, pages_recues,
                erreurs_totales, taux_reussite, donnees_json
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            report_id,
            datetime.now(),
            'DEBUG',
            datetime.now().date(),
            datetime.now().date(),
            filename,
            total_fax,
            fax_envoyes, fax_recus, pages_totales, pages_sf, pages_rf,
            erreurs_totales, taux_reussite,
            json.dumps({'debug': True, 'stats': {
                'total': total_fax, 'sent': fax_envoyes, 'received': fax_recus,
                'pages_sf': pages_sf, 'pages_rf': pages_rf,
                'errors': erreurs_totales, 'success_rate': taux_reussite
            }})
        ))
        
        conn.commit()
        print(f"\n✅ Rapport créé: {report_id}")
        
        # Insérer entrées
        saved_count = 0
        failed_count = 0
        
        for entry in entries:
            try:
                entry_id = str(uuid4())
                cursor.execute("""
                    INSERT INTO fax_entries (
                        id, report_id, fax_id, utilisateur, mode, date_heure,
                        numero_original, numero_normalise, pages, valide, erreurs
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    entry_id,
                    report_id,
                    entry.get('fax_id') or '-',
                    entry.get('utilisateur') or 'N/A',
                    entry.get('mode') or '-',
                    entry.get('date_heure'),
                    entry.get('numero_envoi') or '-',
                    entry.get('numero') or '-',
                    entry.get('pages') or 0,
                    1,  # valide
                    entry.get('erreurs', '')
                ))
                saved_count += 1
            except Exception as e:
                failed_count += 1
                print(f"   ⚠️  Erreur entrée: {e}")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"\n✅ Entrées sauvegardées: {saved_count}/{len(entries)}")
        if failed_count > 0:
            print(f"   ⚠️  Échecs: {failed_count}")
        
        return report_id
    
    except Exception as e:
        print(f"❌ Erreur sauvegarde: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Fonction principale"""
    print("\n" + "█"*70)
    print("█" + " "*68 + "█")
    print("█  FaxCloud Analyzer - DEBUG SCRIPT (Sans Web)" + " "*23 + "█")
    print("█" + " "*68 + "█")
    print("█"*70)
    
    # Chercher un fichier CSV dans le dossier imports
    imports_dir = Path(__file__).parent / 'data' / 'imports'
    
    if not imports_dir.exists():
        print(f"\n❌ Dossier imports non trouvé: {imports_dir}")
        return
    
    csv_files = list(imports_dir.glob('*.csv'))
    
    if not csv_files:
        print(f"❌ Aucun fichier CSV trouvé dans {imports_dir}")
        return
    
    # Utiliser le premier fichier
    filepath = csv_files[0]
    print(f"\n📁 Fichier sélectionné: {filepath.name}")
    
    # 1. Test import
    entries = test_import(str(filepath))
    if not entries:
        return
    
    # 2. Analyse
    stats = analyze_entries(entries)
    if not stats:
        return
    
    # 3. Sauvegarde
    report_id = save_to_db(entries, filepath.name)
    
    # Résumé
    print_header("✅ RESUME FINAL")
    print(f"\n   Report ID: {report_id}")
    print(f"   Total FAX: {stats['total']}")
    print(f"   Envoyés: {stats['sf']} ({stats['pages_sf']} pages)")
    print(f"   Reçus: {stats['rf']} ({stats['pages_rf']} pages)")
    print(f"   Taux réussite: {stats['success_rate']:.2f}%")
    print("\n" + "█"*70 + "\n")

if __name__ == "__main__":
    main()
