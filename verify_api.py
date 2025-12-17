#!/usr/bin/env python3
"""
Vérife que l'API retourne bien les pages SF/RF
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.core.db_mysql import DatabaseMySQL

db = DatabaseMySQL()
conn = db.get_connection()
cursor = conn.cursor(dictionary=True)

# Récupérer le dernier rapport créé
cursor.execute("""
    SELECT id, fichier_source, total_fax, fax_envoyes, fax_recus,
           pages_envoyees, pages_recues
    FROM reports 
    ORDER BY date_rapport DESC 
    LIMIT 1
""")

report = cursor.fetchone()

if report:
    report_id = report['id']
    print(f"\n📋 Dernier rapport: {report_id}")
    print(f"   Fichier: {report['fichier_source']}")
    print(f"   FAX: {report['fax_envoyes']} SF / {report['fax_recus']} RF")
    print(f"   Pages: {report['pages_envoyees']} SF / {report['pages_recues']} RF")
    
    # Récupérer les entrées FAX
    cursor.execute("""
        SELECT id, fax_id, mode, pages
        FROM fax_entries
        WHERE report_id = %s
        LIMIT 5
    """, (report_id,))
    
    entries = cursor.fetchall()
    print(f"\n📄 Exemple d'entrées (5 premières):")
    for e in entries:
        print(f"   ID={e['fax_id']} Mode={e['mode']} Pages={e['pages']}")
    
    # Calcul côté API
    cursor.execute("""
        SELECT SUM(CASE WHEN mode='SF' THEN pages ELSE 0 END) as sf_total,
               SUM(CASE WHEN mode='RF' THEN pages ELSE 0 END) as rf_total
        FROM fax_entries
        WHERE report_id = %s
    """, (report_id,))
    
    calc = cursor.fetchone()
    print(f"\n✅ Calcul côté API:")
    print(f"   Pages SF: {calc['sf_total'] or 0}")
    print(f"   Pages RF: {calc['rf_total'] or 0}")
else:
    print("❌ Aucun rapport trouvé")

cursor.close()
conn.close()
