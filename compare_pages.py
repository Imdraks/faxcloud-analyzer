#!/usr/bin/env python3
from src.core.db_mysql import DatabaseMySQL

db = DatabaseMySQL()
conn = db.get_connection()
cursor = conn.cursor(dictionary=True)

# Vérifier TOUS les rapports et leurs pages dans les entrées FAX
cursor.execute('''
SELECT id, fichier_source, 
       (SELECT SUM(CASE WHEN mode="SF" THEN pages ELSE 0 END) FROM fax_entries WHERE report_id=reports.id) as sf_calc,
       (SELECT SUM(CASE WHEN mode="RF" THEN pages ELSE 0 END) FROM fax_entries WHERE report_id=reports.id) as rf_calc,
       pages_envoyees, pages_recues
FROM reports 
ORDER BY date_rapport DESC 
LIMIT 5
''')

rows = cursor.fetchall()
print(f"\n📊 Comparaison: BD vs Calcul FAX entries\n")

for r in rows:
    print(f"Rapport: {r['id']}")
    print(f"  Fichier: {r['fichier_source']}")
    print(f"  BD: SF={r['pages_envoyees']} RF={r['pages_recues']}")
    print(f"  Calc: SF={r['sf_calc'] or 0} RF={r['rf_calc'] or 0}")
    print(f"  Match: {r['pages_envoyees'] == (r['sf_calc'] or 0) and r['pages_recues'] == (r['rf_calc'] or 0)}")
    print()

cursor.close()
conn.close()
