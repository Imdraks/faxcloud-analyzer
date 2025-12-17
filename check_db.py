#!/usr/bin/env python3
from src.core.db_mysql import DatabaseMySQL

db = DatabaseMySQL()
conn = db.get_connection()
cursor = conn.cursor(dictionary=True)

cursor.execute('''
SELECT id, fichier_source, total_fax, fax_envoyes, fax_recus, 
       pages_envoyees, pages_recues 
FROM reports 
ORDER BY date_rapport DESC 
LIMIT 3
''')

rows = cursor.fetchall()
print(f"\n📊 Total rapports: {len(rows)}\n")

for r in rows:
    print(f"ID: {r['id']}")
    print(f"  Fichier: {r['fichier_source']}")
    print(f"  FAX: {r['total_fax']} (SF={r['fax_envoyes']} / RF={r['fax_recus']})")
    print(f"  Pages: {r['pages_envoyees']} SF / {r['pages_recues']} RF")
    print()

cursor.close()
conn.close()
