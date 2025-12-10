# 📑 INDEX COMPLET DU PROJET

## 🎯 Fichiers Clés (Racine)

| Fichier | Purpose | Usage |
|---------|---------|-------|
| `main.py` | Point d'entrée CLI | `python main.py --help` |
| `requirements.txt` | Dépendances Python | `pip install -r requirements.txt` |
| `run.bat` | Démarrage rapide Windows | Double-clic ou `run.bat` |
| `QUICK_START.md` | Commandes rapides | Lire pour démarrer |
| `PROJECT_STRUCTURE.md` | Explication structure | Lire pour comprendre |

---

## 📚 Documentation (docs/)

### Pour Commencer
- **QUICK_START.md** → Commandes rapides (3 min)
- **docs/README.md** → Guide d'utilisation (10 min)

### Pour Approfondir
- **docs/DOCUMENTATION.md** → Spécifications complètes (30 min)
- **docs/PSEUDOCODE.md** → Algorithmes détaillés (20 min)
- **docs/ARCHITECTURE.md** → Architecture technique (15 min)
- **docs/SYNTHESE.md** → Récapitulatif projet (5 min)

---

## 🐍 Code Source (src/core/)

| Module | Responsabilité | Fonction Principale |
|--------|-----------------|-------------------|
| **config.py** | Configuration | `ensure_directories()` |
| **importer.py** | Import fichiers | `import_faxcloud_export()` |
| **analyzer.py** | Analyse données | `analyze_data()` |
| **reporter.py** | Génération rapports | `generate_report()` |
| **db.py** | Base de données | `init_database()` |

### Dépendances Internes
```
main.py
 ├── config.py (configuration)
 ├── importer.py (import CSV/XLSX)
 ├── analyzer.py (analyse)
 ├── reporter.py (rapports)
 └── db.py (SQLite)
```

---

## 🌐 Interface Web (web/)

| Fichier | Contenu | Technologie |
|---------|---------|-------------|
| **index.html** | Structure | HTML5 sémantique |
| **style.css** | Design | CSS3 responsive |
| **script.js** | Logique | JavaScript vanilla |

### Sections
1. **Dashboard** : Statistiques globales
2. **Import** : Formulaire d'importation
3. **Rapports** : Listing des rapports
4. **Statistiques** : Graphiques détails

---

## 💾 Données (data/)

### Répertoires
- **data/imports/** : Fichiers CSV/XLSX importés (archive)
- **data/reports/** : Rapports JSON générés
- **data/reports_qr/** : QR codes PNG

### Base de Données (database/)
- **database/faxcloud.db** : SQLite créée au premier `init`

---

## 📊 Fichiers Exemple (exports/)

- **exports/Consommation_CHU_NICE_*.csv** : Données réelles pour test

---

## 📝 Fichiers Logs (logs/)

- **logs/analyzer.log** : Logs détaillés de l'application

---

## 🔄 Flux de Travail Complet

```
1. PRÉPARATION
   ├─ Lire: QUICK_START.md
   ├─ Installer: pip install -r requirements.txt
   └─ Lancer: python main.py init

2. IMPORT
   ├─ Placer fichier CSV/XLSX dans exports/
   ├─ Exécuter: python main.py import --file exports/...
   └─ Voir logs/analyzer.log pour détails

3. ANALYSE
   ├─ Fichier normalisé
   ├─ Numéros validés
   ├─ Statistiques calculées
   └─ Rapport généré

4. RÉSULTATS
   ├─ Fichier: data/reports/{UUID}.json
   ├─ QR Code: data/reports_qr/{UUID}.png
   ├─ Base: database/faxcloud.db
   └─ Logs: logs/analyzer.log

5. CONSULTATION
   ├─ Lister: python main.py list
   ├─ Consulter: python main.py view --report-id <UUID>
   └─ Web: Ouvrir web/index.html
```

---

## 🎓 Apprentissage Progressif

### Niveau 1 - Utilisateur (15 min)
1. Lire: QUICK_START.md
2. Exécuter: `python main.py init`
3. Exécuter: `python main.py import --file exports/...`
4. Exécuter: `python main.py list`

### Niveau 2 - Intégrateur (1 heure)
1. Lire: docs/README.md
2. Lire: docs/ARCHITECTURE.md
3. Explorer: src/core/
4. Modifier: src/core/config.py

### Niveau 3 - Développeur (3 heures)
1. Lire: docs/DOCUMENTATION.md
2. Lire: docs/PSEUDOCODE.md
3. Étudier: Tous les modules Python
4. Modifier: Logique business

### Niveau 4 - Expert (8 heures)
1. Étude complète: docs/ARCHITECTURE.md
2. Tests: Tester tous les cas d'erreur
3. Performance: Optimiser pour gros volumes
4. Extension: Ajouter features nouvelles

---

## 🚀 Commandes Essentielles

### Installation
```bash
pip install -r requirements.txt
```

### Initialisation
```bash
python main.py init
```

### Import Basique
```bash
python main.py import --file exports/data.csv --contract CONTRACT_001
```

### Import Avancé
```bash
python main.py import \
    --file exports/data.csv \
    --contract CONTRACT_001 \
    --start 2024-11-01 \
    --end 2024-11-30
```

### Listing
```bash
python main.py list
```

### Détail
```bash
python main.py view --report-id <UUID-from-list>
```

### Aide
```bash
python main.py --help
python main.py import --help
```

---

## 📦 Arborescence Complète

```
faxcloud-analyzer/
├── 📄 main.py                    [Point d'entrée]
├── 📄 requirements.txt           [Dépendances]
├── 📄 run.bat                    [Démarrage Windows]
├── 📄 QUICK_START.md             [Commandes rapides]
├── 📄 PROJECT_STRUCTURE.md       [Structure détails]
├── 📄 INDEX.md                   [Ce fichier]
├── 📄 .gitignore                 [Fichiers ignorés]
│
├── 📁 src/
│   ├── __init__.py
│   └── core/
│       ├── __init__.py
│       ├── config.py             [Configuration]
│       ├── importer.py           [Import CSV/XLSX]
│       ├── analyzer.py           [Analyse données]
│       ├── reporter.py           [Rapports]
│       └── db.py                 [SQLite]
│
├── 📁 docs/
│   ├── README.md                 [Guide utilisateur]
│   ├── DOCUMENTATION.md          [Spécifications]
│   ├── PSEUDOCODE.md             [Algorithmes]
│   ├── ARCHITECTURE.md           [Architecture]
│   └── SYNTHESE.md               [Récapitulatif]
│
├── 📁 web/
│   ├── index.html                [Interface HTML]
│   ├── style.css                 [Styles CSS]
│   └── script.js                 [Logique JS]
│
├── 📁 data/
│   ├── imports/                  [Fichiers importés]
│   ├── reports/                  [Rapports JSON]
│   └── reports_qr/               [QR codes PNG]
│
├── 📁 database/
│   └── faxcloud.db               [SQLite]
│
├── 📁 exports/
│   └── Consommation_*.csv        [Données source]
│
└── 📁 logs/
    └── analyzer.log              [Fichier logs]
```

---

## ⚡ Raccourcis Navigation

**Si vous êtes...**

- 👤 **Utilisateur** → QUICK_START.md
- 📊 **Analyseur** → docs/README.md
- 🏗️ **Architecte** → docs/ARCHITECTURE.md
- 🧑‍💻 **Développeur** → docs/DOCUMENTATION.md + src/
- 🔬 **Chercheur** → docs/PSEUDOCODE.md

---

## 🎯 Prochaines Étapes

1. **Immédiate** : Lire QUICK_START.md (3 min)
2. **Court terme** : Exécuter `python main.py init` (1 min)
3. **Moyen terme** : Importer premier fichier (5 min)
4. **Long terme** : Lire ARCHITECTURE.md (15 min)

---

## 📞 Besoin d'Aide?

- Questions simples ? → QUICK_START.md
- Questions utilisation ? → docs/README.md
- Questions techniques ? → docs/ARCHITECTURE.md
- Questions algorithmes ? → docs/PSEUDOCODE.md

---

**Version**: 1.0.0  
**Dernière mise à jour**: 2024-12-10  
**Statut**: ✅ Complet

---

*Index généré automatiquement - consultez-le avant toute autre documentation!*
