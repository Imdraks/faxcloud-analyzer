#!/usr/bin/env python3
"""
Test COMPLET qui simule le web/app.py /api/upload
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from core.importer import FileImporter
from core.db_mysql import DatabaseMySQL
from uuid import uuid4
import json
from datetime import datetime

imports_dir = Path(__file__).parent / 'data' / 'imports'
csv_file = list(imports_dir.glob('*.csv'))[0]

print(f"\n📤 Test complet web/app.py simulation")
print(f"   Fichier: {csv_file.name}")

# Import
importer = FileImporter()
result = importer.import_file(str(csv_file))

if not result.get('success'):
    print(f"❌ Erreur: {result.get('errors')}")
    sys.exit(1)

entries = result.get('data', [])
print(f"✅ Importé: {len(entries)} entrées")

# Calculs
total_fax = len(entries)
fax_envoyes = sum(1 for e in entries if e.get('mode') == 'SF')
fax_recus = sum(1 for e in entries if e.get('mode') == 'RF')
erreurs_totales = sum(1 for e in entries if e.get('erreurs'))
taux_reussite = ((total_fax - erreurs_totales) / total_fax * 100) if total_fax > 0 else 0.0
pages_totales = sum(e.get('pages', 0) or 0 for e in entries if isinstance(e.get('pages'), (int, float)))
pages_sf = sum(e.get('pages', 0) or 0 for e in entries if e.get('mode') == 'SF')
pages_rf = sum(e.get('pages', 0) or 0 for e in entries if e.get('mode') == 'RF')

print(f"\n📊 Stats calculées:")
print(f"  Total FAX: {total_fax}")
print(f"  FAX: SF={fax_envoyes} RF={fax_recus}")
print(f"  Pages: SF={pages_sf} RF={pages_rf}")

# Sauvegarde
try:
    db = DatabaseMySQL()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    report_id = 'full_test_' + str(uuid4())[:8]
    
    # Insérer rapport (ligne 161 du web/app.py)
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
        json.dumps({'import': True})
    ))
    
    conn.commit()
    print(f"✅ Rapport créé: {report_id}")
    
    # Insérer les ENTRÉES FAX (ligne 189-211 du web/app.py)
    saved_count = 0
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
                1,
                entry.get('erreurs', '')
            ))
            saved_count += 1
        except Exception as e:
            print(f"⚠️  Erreur entrée: {e}")
    
    conn.commit()
    print(f"✅ Entrées sauvegardées: {saved_count}/{len(entries)}")
    
    # Vérifier
    cursor.execute("""
        SELECT SUM(CASE WHEN mode='SF' THEN pages ELSE 0 END) as sf_total,
               SUM(CASE WHEN mode='RF' THEN pages ELSE 0 END) as rf_total
        FROM fax_entries WHERE report_id = %s
    """, (report_id,))
    
    calc = cursor.fetchone()
    sf_calc = calc[0] or 0
    rf_calc = calc[1] or 0
    
    print(f"\n✅ Vérification:")
    print(f"  Pages calculées depuis entries:")
    print(f"    SF: {sf_calc}")
    print(f"    RF: {rf_calc}")
    print(f"  Pages sauvegardées en rapport:")
    print(f"    SF: {pages_sf}")
    print(f"    RF: {pages_rf}")
    print(f"  Match: {sf_calc == pages_sf and rf_calc == pages_rf}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()
