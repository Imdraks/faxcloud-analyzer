#!/usr/bin/env python3
"""
Diagnostic: Compare les pages calculées du debug vs du web import
"""
from src.core.importer import FileImporter
from pathlib import Path

# Chercher le CSV
imports_dir = Path(__file__).parent / 'data' / 'imports'
csv_files = list(imports_dir.glob('*.csv'))

if csv_files:
    filepath = csv_files[0]
    print(f"\n📄 Test avec: {filepath.name}")
    
    importer = FileImporter()
    result = importer.import_file(str(filepath))
    
    if result.get('success'):
        entries = result.get('data', [])
        print(f"\n✅ Import réussi: {len(entries)} entrées")
        
        # Calcul pages
        total_fax = len(entries)
        fax_envoyes = sum(1 for e in entries if e.get('mode') == 'SF')
        fax_recus = sum(1 for e in entries if e.get('mode') == 'RF')
        
        # Vérifier le type des pages
        print(f"\n📊 Type des pages:")
        for i, e in enumerate(entries[:5]):
            page_val = e.get('pages')
            print(f"  Entry {i}: pages={page_val} (type={type(page_val).__name__})")
        
        # Calcul pages SF/RF
        pages_sf = sum(e.get('pages', 0) or 0 for e in entries if e.get('mode') == 'SF')
        pages_rf = sum(e.get('pages', 0) or 0 for e in entries if e.get('mode') == 'RF')
        
        print(f"\n📄 Stats:")
        print(f"  Total FAX: {total_fax}")
        print(f"  Envoyés: {fax_envoyes}")
        print(f"  Reçus: {fax_recus}")
        print(f"  Pages SF: {pages_sf}")
        print(f"  Pages RF: {pages_rf}")
    else:
        print(f"❌ Erreur: {result.get('errors')}")
