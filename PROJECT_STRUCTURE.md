# 📁 Structure du Projet FaxCloud Analyzer

```
faxcloud-analyzer/
│
├── 📄 main.py                    # Point d'entrée principal (CLI)
├── 📄 requirements.txt           # Dépendances Python
├── 📄 .gitignore               # Fichiers à ignorer (Git)
├── 📄 PROJECT_STRUCTURE.md     # Cette structure
│
├── 📁 src/                      # Code source du projet
│   ├── __init__.py             # Package root
│   └── core/                   # Modules principaux
│       ├── __init__.py
│       ├── config.py           # Configuration et chemins
│       ├── db.py               # Base de données SQLite
│       ├── importer.py         # Import CSV/XLSX
│       ├── analyzer.py         # Analyse données
│       └── reporter.py         # Génération rapports
│
├── 📁 docs/                     # Documentation complète
│   ├── README.md               # Guide d'utilisation
│   ├── DOCUMENTATION.md        # Spécifications complètes
│   ├── PSEUDOCODE.md           # Pseudocode détaillé
│   ├── ARCHITECTURE.md         # Architecture technique
│   └── SYNTHESE.md             # Récapitulatif projet
│
├── 📁 web/                      # Interface web
│   ├── index.html              # Page principale
│   ├── style.css               # Styles CSS
│   └── script.js               # JavaScript interactif
│
├── 📁 data/                     # Données du projet
│   ├── imports/                # Fichiers importés (vide au démarrage)
│   ├── reports/                # Rapports JSON générés
│   └── reports_qr/             # QR codes PNG générés
│
├── 📁 database/                 # Base de données
│   └── faxcloud.db             # SQLite (créé au premier démarrage)
│
├── 📁 exports/                  # Fichiers export à analyser
│   └── sample_export_2024_12.csv # Exemple de données
│
├── 📁 logs/                     # Fichiers logs
│   └── analyzer.log            # Logs application
│
└── 📁 .git/                     # Repository Git
```

---

## 🎯 Description des Répertoires

### `src/` - Code Source
**Contient** tous les modules Python du projet
- **core/** : Modules de base (config, db, importer, analyzer, reporter)
- Structure modulaire et extensible

### `docs/` - Documentation
**Contient** toute la documentation du projet
- README.md : Guide d'utilisation pour l'utilisateur
- DOCUMENTATION.md : Spécifications techniques complètes (1200 lignes)
- PSEUDOCODE.md : Pseudocode avec exemples (800 lignes)
- ARCHITECTURE.md : Architecture système (600 lignes)
- SYNTHESE.md : Résumé du projet (500 lignes)

### `web/` - Interface Web
**Contient** l'interface utilisateur
- index.html : Structure HTML responsive
- style.css : Styles mobiles et desktop
- script.js : Logique JavaScript (mock data)

### `data/` - Données
**Contient** les fichiers de travail
- imports/ : Fichiers CSV/XLSX importés (archive)
- reports/ : Rapports JSON générés
- reports_qr/ : QR codes PNG généré

### `database/` - Base de Données
**Contient** la base SQLite
- faxcloud.db : Créée automatiquement au premier `init`
- Tables : reports, fax_entries

### `exports/` - Exports à Traiter
**Contient** les fichiers source
- sample_export_2024_12.csv : Données d'exemple

### `logs/` - Logs
**Contient** les fichiers journaux
- analyzer.log : Logs du programme

---

## 🚀 Utilisation

### 1️⃣ Initialisation
```bash
python main.py init
```
Crée la base de données et les répertoires nécessaires.

### 2️⃣ Importer un fichier
```bash
python main.py import \
    --file exports/sample_export_2024_12.csv \
    --contract CONTRACT_001 \
    --start 2024-12-01 \
    --end 2024-12-31
```
Analyse le fichier et génère un rapport.

### 3️⃣ Lister les rapports
```bash
python main.py list
```
Affiche tous les rapports générés.

### 4️⃣ Consulter un rapport
```bash
python main.py view --report-id <UUID>
```
Affiche le détail d'un rapport.

---

## 📊 Fichiers Clés

| Fichier | Rôle | Contenu |
|---------|------|---------|
| main.py | Orchestrateur | CLI et workflow principal |
| src/core/config.py | Configuration | Chemins, paramètres, logging |
| src/core/db.py | Persistance | SQLite CRUD et statistiques |
| src/core/importer.py | Import | Lecture CSV/XLSX et normalisation |
| src/core/analyzer.py | Analyse | Validation numéros et stats |
| src/core/reporter.py | Rapports | QR codes, JSON, résumés |
| web/index.html | Interface | Dashboard HTML responsive |
| docs/README.md | Guide | Documentation utilisateur |

---

## 🔄 Flux de Données

```
exports/
    ↓
main.py import
    ↓
importer.py (lecture + normalisation)
    ↓
analyzer.py (validation + statistiques)
    ↓
reporter.py (rapports + QR codes)
    ↓
database/ (SQLite)
data/reports/ (JSON)
data/reports_qr/ (PNG)
logs/ (tracking)
```

---

## ✅ Checklist Installation

- [x] Structure répertoires créée
- [x] Fichiers organisés
- [x] Imports corrigés
- [x] .gitignore configuré
- [x] Package __init__.py
- [x] main.py testé

---

## 📦 Dépendances

```
pandas==2.0.0
openpyxl==3.10.0
qrcode==7.4.2
pillow==10.0.0
flask==3.0.0
requests==2.31.0
python-dateutil==2.8.2
```

Installer avec : `pip install -r requirements.txt`

---

**Généré** : 2025-12-10  
**Version** : 1.0.0  
**Statut** : ✅ Prêt à l'emploi
