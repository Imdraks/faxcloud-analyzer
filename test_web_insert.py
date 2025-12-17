#!/usr/bin/env python3
"""
Test direct le code web app pour l'upload
"""
import sys
from pathlib import Path

# Ajouter src et web au chemin
sys.path.insert(0, str(Path(__file__).parent / 'src'))
sys.path.insert(0, str(Path(__file__).parent / 'web'))

# Importer les dépendances du web app
from core.importer import FileImporter
from core.db_mysql import DatabaseMySQL
from uuid import uuid4
import json
from datetime import datetime

# Cherche un CSV
imports_dir = Path(__file__).parent / 'data' / 'imports'
csv_file = list(imports_dir.glob('*.csv'))[0]

print(f"\n📤 Simulation de l'upload web: {csv_file.name}")

# 1. Import le fichier
importer = FileImporter()
result = importer.import_file(str(csv_file))

if not result.get('success'):
    print(f"❌ Erreur import: {result.get('errors')}")
    sys.exit(1)

entries = result.get('data', [])
print(f"✅ Importé: {len(entries)} entrées")

# 2. Calcule les stats (comme le web app)
total_fax = len(entries)
fax_envoyes = sum(1 for e in entries if e.get('mode') == 'SF')
fax_recus = sum(1 for e in entries if e.get('mode') == 'RF')
erreurs_totales = sum(1 for e in entries if e.get('erreurs'))
taux_reussite = ((total_fax - erreurs_totales) / total_fax * 100) if total_fax > 0 else 0.0
pages_totales = sum(e.get('pages', 0) or 0 for e in entries if isinstance(e.get('pages'), (int, float)))
pages_sf = sum(e.get('pages', 0) or 0 for e in entries if e.get('mode') == 'SF')
pages_rf = sum(e.get('pages', 0) or 0 for e in entries if e.get('mode') == 'RF')

print(f"\n📊 Calculs du web app:")
print(f"  Total FAX: {total_fax}")
print(f"  Envoyés: {fax_envoyes}")
print(f"  Reçus: {fax_recus}")
print(f"  Pages totales: {pages_totales}")
print(f"  Pages SF: {pages_sf}")
print(f"  Pages RF: {pages_rf}")

print(f"\n💾 Insertion en base...")

# 3. Sauvegarde en BD (comme le web app)
try:
    db = DatabaseMySQL()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    report_id = 'test_web_' + str(uuid4())[:8]
    
    # INSERT exactement comme le web app
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
        'IMPORT',
        datetime.now().date(),
        datetime.now().date(),
        csv_file.name,
        total_fax,
        fax_envoyes, fax_recus, pages_totales, pages_sf, pages_rf,
        erreurs_totales, taux_reussite,
        json.dumps({'import': True, 'stats': {
            'total': total_fax, 'sent': fax_envoyes, 'received': fax_recus,
            'errors': erreurs_totales, 'success_rate': taux_reussite,
            'pages_sf': pages_sf, 'pages_rf': pages_rf
        }})
    ))
    
    conn.commit()
    print(f"✅ Rapport inséré: {report_id}")
    
    # Vérifier ce qui a été sauvegardé
    cursor.execute("""
        SELECT id, fichier_source, total_fax, fax_envoyes, fax_recus,
               pages_totales, pages_envoyees, pages_recues
        FROM reports WHERE id = %s
    """, (report_id,))
    
    saved = cursor.fetchone()
    if saved:
        print(f"\n✅ Vérification BD:")
        print(f"  ID: {saved[0]}")
        print(f"  Fichier: {saved[1]}")
        print(f"  Total FAX: {saved[2]}")
        print(f"  FAX: SF={saved[3]} RF={saved[4]}")
        print(f"  Pages totales: {saved[5]}")
        print(f"  Pages envoyees (col11): {saved[6]}")
        print(f"  Pages recues (col12): {saved[7]}")
    else:
        print("❌ Rapport non trouvé!")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()
