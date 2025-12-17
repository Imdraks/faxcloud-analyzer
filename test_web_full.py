#!/usr/bin/env python3
"""
Test complet du web: Upload CSV via HTTP POST et vérification du rapport
"""
import subprocess
import time
from pathlib import Path

# D'abord installe requests si manquant
try:
    import requests
except ImportError:
    print("📦 Installation de requests...")
    subprocess.check_call(['.venv\\Scripts\\pip.exe', 'install', 'requests'])
    import requests

imports_dir = Path(__file__).parent / 'data' / 'imports'
csv_file = list(imports_dir.glob('*.csv'))[0]

print(f"\n🚀 TEST WEB COMPLET")
print(f"   Fichier: {csv_file.name}")
print(f"   URL: http://localhost:5000")

# 1. Upload via HTTP POST
print(f"\n📤 Étape 1: Upload du CSV...")
try:
    with open(csv_file, 'rb') as f:
        files = {'file': (csv_file.name, f)}
        response = requests.post('http://localhost:5000/api/upload', files=files, timeout=60)
        
    if response.status_code == 200:
        result = response.json()
        if result.get('success'):
            report_id = result.get('report_id')
            print(f"✅ Upload réussi!")
            print(f"   Report ID: {report_id}")
            
            # 2. Attendre un peu puis récupérer le rapport
            print(f"\n⏳ Étape 2: Récupération du rapport...")
            time.sleep(1)
            
            resp2 = requests.get(f'http://localhost:5000/api/report/{report_id}/data', timeout=10)
            
            if resp2.status_code == 200:
                report = resp2.json()
                print(f"✅ Rapport récupéré!")
                print(f"\n   📊 Statistiques:")
                print(f"   Total FAX: {report.get('total', 0)}")
                print(f"   Envoyés (SF): {report.get('sent', 0)}")
                print(f"   Reçus (RF): {report.get('received', 0)}")
                print(f"   Pages SF: {report.get('pages_sf', 0)}")
                print(f"   Pages RF: {report.get('pages_rf', 0)}")
                print(f"   Taux réussite: {report.get('success_rate', 0):.2f}%")
                print(f"   Entrées: {report.get('entries_count', 0)}")
                
                # Vérifier que tout est correct
                if report.get('pages_sf', 0) > 0 and report.get('pages_rf', 0) > 0:
                    print(f"\n✅ SUCCÈS! Les pages SF/RF s'affichent correctement!")
                else:
                    print(f"\n⚠️  Attention: Pages SF/RF manquantes!")
            else:
                print(f"❌ Erreur rapport: {resp2.status_code}")
        else:
            print(f"❌ Upload échoué: {result.get('error')}")
    else:
        print(f"❌ Erreur HTTP: {response.status_code}")
        print(f"   {response.text}")

except requests.exceptions.ConnectionError:
    print(f"❌ Impossible de se connecter à http://localhost:5000")
    print(f"   Assurez-vous que le serveur est lancé:")
    print(f"   python web/app.py")
except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()

print(f"\n🌐 Ouvrez le navigateur: http://localhost:5000/reports")
