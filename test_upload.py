#!/usr/bin/env python3
"""
Test l'API /api/upload directement
"""
import requests
from pathlib import Path

# Trouver un CSV
imports_dir = Path(__file__).parent / 'data' / 'imports'
csv_file = list(imports_dir.glob('*.csv'))[0]

print(f"\n📤 Upload du fichier: {csv_file.name}")

# Préparer le fichier
with open(csv_file, 'rb') as f:
    files = {'file': (csv_file.name, f)}
    
    # Envoyer à l'API
    try:
        response = requests.post('http://localhost:5000/api/upload', files=files)
        data = response.json()
        
        print(f"\n✅ Réponse: {data}")
        
        if data.get('success'):
            report_id = data.get('report_id')
            print(f"\n📋 Report ID: {report_id}")
            
            # Maintenant récupérer les données du rapport
            import time
            time.sleep(1)
            
            resp2 = requests.get(f'http://localhost:5000/api/report/{report_id}/data')
            report_data = resp2.json()
            
            print(f"\n📊 Pages dans le rapport API:")
            print(f"  Pages SF: {report_data.get('pages_sf')}")
            print(f"  Pages RF: {report_data.get('pages_rf')}")
    
    except requests.exceptions.ConnectionError:
        print("❌ Erreur: Serveur non lancé")
        print("   Lance: python web/app.py")
    except Exception as e:
        print(f"❌ Erreur: {e}")
