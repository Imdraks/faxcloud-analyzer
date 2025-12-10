# 🚀 COMMANDES RAPIDES

## Démarrage Rapide

### Windows
```bash
run.bat
```

### Linux/Mac
```bash
python main.py --help
```

---

## 📋 Commandes Principales

### 1. Initialiser la base de données
```bash
python main.py init
```
Crée la structure SQLite et les répertoires.

### 2. Importer un fichier
```bash
python main.py import \
    --file exports/Consommation_CHU_NICE_20251104_104525.csv \
    --contract CONTRACT_CHU_NICE \
    --start 2024-11-01 \
    --end 2024-11-30
```
Traite un fichier CSV/XLSX et génère un rapport complet.

### 3. Lister les rapports
```bash
python main.py list
```
Affiche tous les rapports générés avec les statistiques.

### 4. Consulter un rapport
```bash
python main.py view --report-id <UUID>
```
Affiche les détails complets d'un rapport.

### 5. Aide
```bash
python main.py --help
```

---

## 🔧 Installation des Dépendances

```bash
pip install -r requirements.txt
```

Packages requis:
- pandas (lecture CSV/XLSX)
- openpyxl (Excel)
- qrcode (QR codes)
- pillow (images PNG)
- flask (API future)
- requests (HTTP)
- python-dateutil (dates)

---

## 📁 Structure Fichiers

```
faxcloud-analyzer/
├── main.py                    # Point d'entrée
├── requirements.txt           # Dépendances
├── run.bat                    # Démarrage Windows
├── PROJECT_STRUCTURE.md       # Structure projet
├── QUICK_START.md             # Ceci
│
├── src/core/                  # Code source
│   ├── config.py
│   ├── db.py
│   ├── importer.py
│   ├── analyzer.py
│   └── reporter.py
│
├── docs/                      # Documentation
│   ├── README.md
│   ├── DOCUMENTATION.md
│   ├── PSEUDOCODE.md
│   ├── ARCHITECTURE.md
│   └── SYNTHESE.md
│
├── web/                       # Interface web
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── data/                      # Données générées
│   ├── imports/
│   ├── reports/
│   └── reports_qr/
│
├── database/                  # Base SQLite
├── logs/                      # Logs
└── exports/                   # Fichiers source
```

---

## 📊 Flux de Données

```
1. Importer CSV/XLSX
   ↓
2. Valider & Normaliser
   ↓
3. Analyser & Compter
   ↓
4. Générer Rapport + QR Code
   ↓
5. Sauvegarder en SQLite
   ↓
6. Fichiers:
   - data/reports/{UUID}.json
   - data/reports_qr/{UUID}.png
   - database/faxcloud.db
   - logs/analyzer.log
```

---

## 🧪 Test avec Données Exemple

```bash
# Initialiser
python main.py init

# Importer l'export d'exemple
python main.py import \
    --file exports/Consommation_CHU_NICE_20251104_104525.csv \
    --contract TEST_001

# Lister les rapports créés
python main.py list

# Consulter le rapport (copier UUID de la liste)
python main.py view --report-id <UUID>
```

---

## 🔍 Sortie Console

### Import
```
✓ Fichier importé: 20 lignes
✓ Données validées et normalisées
✓ Analyse complète:
  - Total FAX: 20
  - FAX Envoyés: 10
  - FAX Reçus: 10
  - Pages totales: 85
  - Taux réussite: 85%
✓ Rapport généré: UUID-1234-5678
✓ QR Code créé: data/reports_qr/UUID-1234-5678.png
✓ Données sauvegardées en base
```

### Liste
```
ID                                   | Timestamp          | Contract    | FAX | Errors | Rate
1234-5678-...                       | 2024-12-10 14:30   | TEST_001    | 20  | 3      | 85%
```

### Rapport
```
═══════════════════════════════════════════════════════
RAPPORT D'ANALYSE FAX
═══════════════════════════════════════════════════════
UUID: 1234-5678-abcd-efgh
Date: 2024-12-10 14:30:00
Contrat: TEST_001

STATISTIQUES GLOBALES:
├─ Total FAX: 20
├─ FAX Envoyés: 10
├─ FAX Reçus: 10
├─ Pages: 85
├─ Erreurs: 3
└─ Taux réussite: 85%

DÉTAIL ERREURS:
└─ Numéro invalide: 3

QR CODE: data/reports_qr/1234-5678.png
```

---

## 🛠️ Configuration

Voir `src/core/config.py` pour personnaliser:
- Répertoires
- Validation (longueur numéro, code pays)
- Logging
- URLs web

---

## 📞 Support

- Voir `docs/README.md` pour guide complet
- Voir `docs/ARCHITECTURE.md` pour détails techniques
- Voir `docs/PSEUDOCODE.md` pour algorithmes

---

**Version**: 1.0.0  
**Statut**: ✅ Production-ready
