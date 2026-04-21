#!/usr/bin/env python3
import requests
import json

reports = {
    'Sans détection': 'ef7f0411-ff7c-4b80-93d4-78286ea8bfaf',
    'Avec détection': 'e4611dd3-382b-496b-9f3c-24846fadb074'
}

for name, report_id in reports.items():
    try:
        r = requests.get(f'http://192.168.10.132:8000/api/report/{report_id}', timeout=10)
        r.raise_for_status()
        data = r.json()
        
        print(f'\n{"="*60}')
        print(f'Rapport: {name}')
        print(f'{"="*60}')
        print(f'Total FAX: {data.get("total_fax")}')
        
        det = data.get('asterisk_detection', {})
        print(f'Détection activée: {det.get("detection_enabled")}')
        
        if det:
            print(f'\nStatistiques détection:')
            print(f'  - FAX détectés: {det.get("fax_detected")}')
            print(f'  - Téléphones détectés: {det.get("phone_detected")}')
            print(f'  - Inconnus: {det.get("unknown_detected")}')
            print(f'  - Erreurs: {det.get("detection_errors")}')
        
        if data.get('entries') and len(data['entries']) > 0:
            entry = data['entries'][0]
            print(f'\nPremière entrée:')
            print(f'  - Numéro: {entry.get("numero_normalise")}')
            print(f'  - Type: {entry.get("numero_type_label")}')
            if entry.get('asterisk_detected'):
                print(f'  - Tonalité Asterisk: {entry.get("asterisk_tone")}')
                print(f'  - FAX?: {entry.get("asterisk_is_fax")}')
                print(f'  - Durée: {entry.get("asterisk_duration_ms")} ms')
    except Exception as e:
        print(f'Erreur: {e}')

print(f'\n{"="*60}')
print('✅ Tests complétés!')
