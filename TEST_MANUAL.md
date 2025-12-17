📋 MANUEL DE TEST - FaxCloud Analyzer

🌐 Accès à l'application:
   http://127.0.0.1:5000

✅ PAGE D'ACCUEIL:
   1. Ouvre http://127.0.0.1:5000 
   2. Tu dois voir:
      - Titre: "FaxCloud Analyzer"
      - Une zone d'upload "Sélectionner un fichier CSV"
      - Statistiques globales (Total FAX, Envoyés, Reçus, etc.)

✅ TEST D'UPLOAD:
   1. Clique sur "Sélectionner un fichier"
   2. Choisis: data/imports/Consommation_CHU_NICE_20251104_104525.csv
   3. Clique "Importer"
   4. Attends que l'import se termine (~10 secondes)
   5. Tu dois voir: "✅ Rapport créé avec succès!"

✅ VÉRIFIER LES PAGES SF/RF:
   1. Après l'import, clique sur "Voir les rapports"
   2. Ou va directement: http://127.0.0.1:5000/reports
   3. Tu dois voir une liste de rapports
   4. Clique sur le dernier rapport créé
   5. Sur la page du rapport, tu dois voir:
      
      📊 STATISTIQUES:
      - Total FAX: 25958
      - FAX Envoyés: 8996
      - FAX Reçus: 16962
      - Pages SF: 13901  ✅ (IMPORTANT!)
      - Pages RF: 47214  ✅ (IMPORTANT!)
      - Taux de Réussite: 100.00%

✅ DÉTAILS:
   1. Scroll vers le bas
   2. Tu dois voir une section "📋 Détails"
   3. Il y a des filtres: Tous, Envoyés, Reçus, Erreurs
   4. Clique sur "📤 Envoyés" pour voir uniquement les FAX envoyés
   5. Clique sur "📥 Reçus" pour voir uniquement les FAX reçus

✅ TÉLÉCHARGER PDF:
   1. Sur la page du rapport, clique "📥 Télécharger PDF"
   2. Un rapport PDF devrait se télécharger

🎯 CRITÈRES DE SUCCÈS:
   ✅ Upload fonctionne
   ✅ Pages SF/RF s'affichent dans les statistiques
   ✅ Les nombres matchent: SF=13901, RF=47214
   ✅ Filtres fonctionnent
   ✅ PDF se télécharge

🚀 COMMANDES UTILES:
   
   # Lancer le serveur:
   python web/app.py
   
   # Debug script (sans web):
   python debug_import.py
   
   # Test complet:
   python test_full_web.py
   
   # Vérifier les données en BD:
   python check_db.py
   python compare_pages.py

📞 Si tu as des problèmes:
   - Vérifie que MySQL tourne
   - Vérifiez les logs: logs/faxcloud_analyzer.log
   - Relance le serveur: python web/app.py
