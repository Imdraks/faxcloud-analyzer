#!/usr/bin/env python3
import requests
import json

# Récupère les deux rapports
report1_id = "12aa43dc-a36f-4a40-ba4e-19d450e86538"
report2_id = "69b9c7b4-5ccd-4bd8-87d6-40fbb25b4578"

base_url = "http://192.168.10.132:8000"

for idx, report_id in enumerate([report1_id, report2_id], 1):
    try:
        r = requests.get(f"{base_url}/api/report/{report_id}", timeout=10)
        r.raise_for_status()
        data = r.json()
        
        print(f"\n{'='*60}")
        print(f"Rapport {idx} (ID: {report_id})")
        print(f"{'='*60}")
        print(f"Total FAX: {data.get('total_fax')}")
        print(f"Détection Asterisk activée: {data.get('asterisk_detection', {}).get('detection_enabled')}")
        
        if data.get('asterisk_detection'):
            det = data['asterisk_detection']
            print(f"\nStatistiques détection:")
            print(f"  - FAX détectés: {det.get('fax_detected')}")
            print(f"  - Téléphones détectés: {det.get('phone_detected')}")
            print(f"  - Inconnus: {det.get('unknown_detected')}")
            print(f"  - Erreurs: {det.get('detection_errors')}")
        
        if data.get('asterisk_stats'):
            stats = data['asterisk_stats']
            print(f"\nClassification SDA/Téléphone:")
            print(f"  - SDA: {stats.get('sda')}")
            print(f"  - SDA FAX: {stats.get('sda_fax')}")
            print(f"  - Téléphone: {stats.get('telephone')}")
            print(f"  - Mobile: {stats.get('mobile')}")
            print(f"  - International: {stats.get('international')}")
        
        # Affiche une première entrée enrichie
        if data.get('entries') and len(data['entries']) > 0:
            entry = data['entries'][0]
            print(f"\nPremière entrée (enrichissement Asterisk):")
            print(f"  - Numéro: {entry.get('numero_normalise')}")
            print(f"  - Type: {entry.get('numero_type_label')}")
            print(f"  - Détecté Asterisk: {entry.get('asterisk_detected', False)}")
            if entry.get('asterisk_detected'):
                print(f"  - Tonalité: {entry.get('asterisk_tone')}")
                print(f"  - FAX?: {entry.get('asterisk_is_fax')}")
                print(f"  - Durée: {entry.get('asterisk_duration_ms')} ms")
    except Exception as e:
        print(f"Erreur rapport {idx}: {e}")

print(f"\n{'='*60}")
print("✅ Test complet!")
