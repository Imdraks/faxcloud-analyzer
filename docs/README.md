# 📊 FaxCloud Analyzer - Documentation Complète

**Analyseur professionnel de fichiers FAX avec validation, normalisation et statistiques**

> Version: **1.0** | Python 3.13 | Windows PowerShell | Production-Ready

---

## 📑 Table des Matières

1. [Vue d'ensemble](#vue-densemble)
2. [Installation rapide](#installation-rapide)
3. [Utilisation](#utilisation)
4. [Conditions d'analyse](#conditions-danalyse)
5. [Architecture technique](#architecture-technique)
6. [Structure du projet](#structure-du-projet)
7. [Configuration](#configuration)
8. [Modules principaux](#modules-principaux)
9. [Statistiques générées](#statistiques-générées)
10. [Types d'erreurs](#types-derreurs)
11. [Dépannage](#dépannage)
12. [FAQ](#faq)
13. [Index navigation](#index-navigation)

---

## 🎯 Vue d'ensemble

### Objectif
Analyser automatiquement les exports FaxCloud pour:
- ✅ Normaliser les numéros de téléphone
- ✅ Valider les données
- ✅ Générer des statistiques complètes
- ✅ Créer des rapports JSON avec UUID
- ✅ Générer des codes QR

### Fonctionnalités
- 📤 **Import** - CSV/XLSX avec détection automatique (séparateur, encodage)
- 🔍 **Validation** - Numéros, pages, types FAX
- 📊 **Analyse** - Statistiques globales, par utilisateur, par erreur
- 📝 **Rapports** - JSON structuré avec UUID unique
- 🔗 **QR Codes** - Génération PNG (optionnel)
- 🗄️ **Persistance** - Sauvegarde JSON sur disque
- 🎛️ **CLI** - Interface ligne de commande complète

### Technologies
- **Python 3.13.9**
- **pandas** - Lecture CSV/XLSX
- **openpyxl** - Support Excel
- **qrcode** - Génération codes QR (optionnel)
- **Windows PowerShell v5.1**

---

## 🚀 Installation rapide

### Préalables
- Python 3.8+ installé
- Accès aux fichiers CSV/XLSX

### Étapes

**1. Installer les dépendances:**
```bash
pip install -r requirements.txt
```

**2. Vérifier l'installation:**
```bash
python main.py --help
```

**3. Tester avec un fichier:**
```bash
python main.py import --file "exports/Consommation_CHU NICE_20251104_104525 - Copie.csv" --contract "CHU_NICE" --start "2024-11-01" --end "2024-12-31"
```

---

## 💻 Utilisation

### Interface en Ligne de Commande (CLI)

#### Importer un fichier
```bash
python main.py import \
  --file "exports/data.csv" \
  --contract "CONTRACT_001" \
  --start "2024-01-01" \
  --end "2024-12-31"
```

**Arguments:**
- `--file` (obligatoire) - Chemin du fichier CSV/XLSX
- `--contract` (optionnel) - ID du contrat (défaut: "UNKNOWN")
- `--start` (optionnel) - Date début YYYY-MM-DD (défaut: "2024-01-01")
- `--end` (optionnel) - Date fin YYYY-MM-DD (défaut: "2024-12-31")

**Sortie:**
```
IMPORT FAXCLOUD: 25957 lignes successfully parsed
ANALYSE: 97.5% reussite
RAPPORT: ID 2c37d596-509f-4cf8-b74f-3248248e7b5d
```

#### Initialiser (optionnel)
```bash
python main.py init
```
Crée les répertoires nécessaires.

### Utilisation Python

```python
from src.core import importer, analyzer, reporter, config

# Configurer
config.ensure_directories()
config.setup_logging()

# 1. IMPORTER
result = importer.import_faxcloud_export('exports/data.csv')
if not result['success']:
    print(f"Erreur: {result['message']}")
    exit(1)

print(f"✓ {result['count']} lignes importées")

# 2. ANALYSER
analysis = analyzer.analyze_data(
    result['rows'],
    'CHU_NICE',
    '2024-11-01',
    '2024-12-31'
)

# 3. GÉNÉRER RAPPORT
report = reporter.generate_report(analysis)

if report['success']:
    print(f"✓ Rapport: {report['report_id']}")
    print(f"  JSON: data/reports/{report['report_id']}.json")
    if report['qr_path']:
        print(f"  QR Code: {report['qr_path']}")
```

---

## 📋 Conditions d'analyse

### Normalisation des numéros (Colonne H)

| Format | Résultat | Exemple |
|--------|----------|---------|
| `+33X XXXXXXXXX` | `33XXXXXXXXXXX` | +33 1 45 22 11 34 → 33145221134 |
| `0X XXXXXXXXX` | `33XXXXXXXXXXX` | 0145221134 → 33145221134 |
| `0033X XXXXXX` | `33XXXXXXXXXXX` | 00331 45 22 11 34 → 33145221134 |

### Validation des numéros
- ✅ Longueur exacte: **11 chiffres**
- ✅ Indicatif: **commence par 33** (France)
- ❌ Vide: erreur "Numero vide"
- ❌ Mauvaise longueur: erreur "Longueur incorrecte"
- ❌ Mauvais indicatif: erreur "Indicatif invalide"

### Validation des pages (Colonne K)
- ✅ Type: **entier numérique**
- ✅ Valeur: **>= 1**
- ❌ Non-numérique: erreur "Pages invalides"
- ❌ Valeur < 1: erreur "Pages doit etre >= 1"

### Validation du type FAX (Colonne D)
- ✅ **SF** = FAX envoyé (Send Fax)
- ✅ **RF** = FAX reçu (Receive Fax)
- ❌ Autre: erreur "Mode invalide"

### Colonnes attendues (A-N)

| Col | Nom | Index |
|-----|-----|-------|
| A | Fax ID | 0 |
| B | Nom et prénom utilisateur | 1 |
| C | Revendeur | 2 |
| D | Mode (SF/RF) | 3 |
| E | Adresse de messagerie | 4 |
| F | Date et heure du fax | 5 |
| G | Numéro d'envoi | 6 |
| H | Numéro appelé (À VALIDER) | 7 |
| I | Appel international | 8 |
| J | Appel interne | 9 |
| K | Nombre de pages réel (À VALIDER) | 10 |
| L | Durée | 11 |
| M | Pages facturées | 12 |
| N | Type facturation | 13 |

---

## 🏗️ Architecture technique

### Workflow complet

```
Fichier CSV/XLSX
        ↓
importer.import_faxcloud_export()
  • Détection format (CSV/XLSX)
  • Multi-encoding (UTF-8, Latin-1, CP1252)
  • Multi-séparateur (;, ,, \t)
  • Normalisation colonnes 0-13
  • Validation 14 colonnes
        ↓
analyzer.analyze_data()
  • Valide chaque ligne:
    - Colonne 7 (H): numéro
    - Colonne 10 (K): pages
    - Colonne 3 (D): type FAX
  • Calcule statistiques:
    - Total, envoyés, reçus
    - Pages par type
    - Erreurs par type
    - Stats par utilisateur
        ↓
reporter.generate_report()
  • Génère UUID unique
  • Crée QR code PNG (si dispo)
  • Sauvegarde JSON complet
  • Retourne report_id
        ↓
Fichiers générés:
  ├─ data/reports/{UUID}.json
  ├─ data/reports_qr/{UUID}.png (optionnel)
  └─ logs/analyzer.log
```

### Modules

**importer.py** (95 lignes)
```python
def import_faxcloud_export(file_path: str) -> Dict
```
- Lit CSV/XLSX
- Détecte format et séparateur
- Normalise 14 colonnes
- Retourne `{success, rows[], count, message}`

**validation_rules.py** (60 lignes)
```python
def normalize_number(numero_brut: str) -> str
def validate_number(numero_normalise: str) -> Tuple[bool, Optional[str]]
def analyze_number(numero_brut: str) -> Tuple[bool, str, Optional[str]]
def validate_pages(pages_brut: str) -> Tuple[bool, Optional[str]]
def validate_fax_type(mode_brut: str) -> Tuple[bool, Optional[str]]
```

**analyzer.py** (150 lignes)
```python
def analyze_entry(row: Dict) -> Dict
def analyze_data(rows: List[Dict], contract_id: str, date_debut: str, date_fin: str) -> Dict
```
- Valide chaque ligne
- Agrège statistiques
- Compte erreurs par type
- Retourne `{statistics, entries[]}`

**reporter.py** (130 lignes)
```python
def generate_report(analysis: Dict) -> Dict
def load_report_json(report_id: str) -> Dict
def generate_summary(report_json: Dict) -> str
```
- Crée UUID
- Génère QR code
- Sauvegarde JSON
- Retourne `{report_id, report_url, qr_path}`

**config.py** (150 lignes)
- Configuration chemins
- Setup logging
- Création répertoires

**main.py** (290 lignes)
- CLI orchestratrice
- Workflow complet
- Logging détaillé

---

## 📁 Structure du projet

```
faxcloud-analyzer/
│
├── 🐍 main.py                    # Point d'entrée CLI
├── 📄 requirements.txt           # Dépendances Python
├── 📘 README.md                  # Cet document (documentation unifiée)
│
├── 📁 src/core/                 # Code source
│   ├── __init__.py
│   ├── config.py                # Configuration
│   ├── importer.py              # Import CSV/XLSX
│   ├── validation_rules.py      # Règles validation
│   ├── analyzer.py              # Analyse logique
│   └── reporter.py              # Génération rapports
│
├── 📁 data/                     # Données générées
│   ├── imports/                 # (Historique)
│   ├── reports/                 # Rapports JSON
│   └── reports_qr/              # QR codes PNG
│
├── 📁 exports/                  # Fichiers à analyser
│   └── Consommation_CHU NICE_*.csv
│
├── 📁 logs/                     # Fichiers journaux
│   └── analyzer.log
│
└── 📁 web/                      # Interface web (futur)
    ├── index.html
    ├── style.css
    └── script.js
```

---

## 🔧 Configuration

### config.py

```python
# Chemins
DIRS = {
    'imports': Path('data/imports'),
    'reports_json': Path('data/reports'),
    'reports_qr': Path('data/reports_qr'),
    'exports': Path('exports'),
    'logs': Path('logs')
}

# Validation
PHONE_LENGTH = 11          # Longueur numéro
COUNTRY_CODE = '33'        # Indicatif France
MIN_PAGES = 1             # Pages minimum

# Logging
LOG_LEVEL = logging.INFO
LOG_FORMAT = '[%(asctime)s] %(levelname)s - %(name)s - %(message)s'
```

### requirements.txt

```
pandas>=2.0.0
openpyxl>=3.1.0
qrcode>=7.4.0
pillow>=10.0.0
```

**Installation:**
```bash
pip install -r requirements.txt
```

---

## 📦 Modules principaux

### 1. importer.py

**Fonction principale:**
```python
def import_faxcloud_export(file_path: str) -> Dict
```

**Retour:**
```python
{
    "success": True,
    "rows": [
        {0: "fax_id", 1: "user", 3: "SF", 7: "0112345678", 10: "5", ...},
        ...
    ],
    "count": 25957,
    "message": "Import OK: 25957 lignes"
}
```

**Caractéristiques:**
- Auto-détecte CSV vs XLSX
- Essaie multi-séparateurs: `;`, `,`, `\t`
- Essaie multi-encodages: UTF-8, Latin-1, CP1252
- Normalise indices 0-13
- Valide 14 colonnes minimum

### 2. validation_rules.py

**Fonctions:**

```python
normalize_number("+33 1 45 22 11 34")
# → "33145221134"

validate_number("33145221134")
# → (True, None)

validate_pages("5")
# → (True, None)

validate_fax_type("SF")
# → (True, None)

analyze_number("0145221134")
# → (True, "33145221134", None)
```

### 3. analyzer.py

**Fonction principale:**
```python
def analyze_data(rows: List[Dict], contract_id: str, 
                 date_debut: str, date_fin: str) -> Dict
```

**Retour:**
```python
{
    "contract_id": "CHU_NICE",
    "date_debut": "2024-11-01",
    "date_fin": "2024-12-31",
    "statistics": {
        "total_fax": 25957,
        "fax_envoyes": 8350,
        "fax_recus": 16962,
        "pages_totales": 60942,
        "pages_envoyees": 13728,
        "pages_recues": 47214,
        "erreurs_totales": 645,
        "taux_reussite": 97.52,
        "erreurs_par_type": {
            "Pages invalides": 538,
            "Longueur incorrecte": 294,
            "Indicatif invalide": 116
        }
    }
}
```

### 4. reporter.py

**Fonction principale:**
```python
def generate_report(analysis: Dict) -> Dict
```

**Retour:**
```python
{
    "success": True,
    "report_id": "2c37d596-509f-4cf8-b74f-3248248e7b5d",
    "report_url": "/reports/2c37d596-509f-4cf8-b74f-3248248e7b5d",
    "qr_path": "data/reports_qr/2c37d596-509f-4cf8-b74f-3248248e7b5d.png",
    "message": "Rapport OK"
}
```

**Fichiers générés:**
- `data/reports/{report_id}.json` - Rapport complet
- `data/reports_qr/{report_id}.png` - QR code

---

## 📊 Statistiques générées

### Globales
- `total_fax` - Nombre total de FAX
- `fax_envoyes` - FAX mode SF
- `fax_recus` - FAX mode RF
- `pages_totales` - Somme de toutes les pages
- `pages_envoyees` - Pages mode SF
- `pages_recues` - Pages mode RF
- `erreurs_totales` - Nombre d'erreurs
- `taux_reussite` - Pourcentage (0-100)

### Par type d'erreur
- Nombre d'erreurs de chaque type
- Pourcentage du total

### Par utilisateur
- Nombre d'envois par utilisateur
- Nombre d'erreurs par utilisateur
- Taux de réussite par utilisateur
- Pages par utilisateur

### Exemple complet

```
RAPPORT FAXCLOUD
================

ID: 2c37d596-509f-4cf8-b74f-3248248e7b5d
Contrat: CHU_NICE
Periode: 2024-11-01 a 2024-12-31

STATISTIQUES
============

Total FAX: 25957
  - Envoyes: 8350
  - Recus: 16962

Pages: 60942
  - Envoyees: 13728
  - Recues: 47214

Erreurs: 645
Taux reussite: 97.52%
```

---

## 🔴 Types d'erreurs

### 1. Numero vide
**Cause:** Colonne H vide ou caractères non-numériques

### 2. Longueur incorrecte
**Cause:** Numéro ≠ 11 chiffres

### 3. Indicatif invalide
**Cause:** Numéro ne commence pas par 33

### 4. Pages invalides
**Cause:** Colonne K non-numérique ou < 1

### 5. Mode invalide
**Cause:** Colonne D ≠ SF ou RF

---

## 🐛 Dépannage

### ❌ "Fichier non trouve"
**Solution:** Vérifiez le chemin, utilisez chemin absolu

### ❌ "Format non reconnu"
**Solution:** Accepte `.csv` ou `.xlsx` seulement

### ❌ "Colonnes insuffisantes"
**Solution:** Le fichier doit avoir exactement 14 colonnes (A-N)

### ❌ "CSV parsing error"
**Solution:** Vérifiez le séparateur CSV (`;` vs `,`)

### ❌ "UnicodeEncodeError" (Windows)
**Solution:** Problème d'affichage logs seulement, données traitées correctement

---

## ❓ FAQ

**Q: Combien de lignes peut traiter le système?**
A: Testé jusqu'à 25,957 lignes sans problème (~4 secondes).

**Q: Les QR codes sont obligatoires?**
A: Non, optionnels. Si qrcode/pillow non installés, saute cette étape.

**Q: Où sont sauvegardés les rapports?**
A: `data/reports/{UUID}.json` sur disque

**Q: Support Asterisk?**
A: Pas encore, prévu pour v2.0.

---

## 📑 Index navigation

### Fichiers Clés

| Fichier | Utilité |
|---------|---------|
| `main.py` | Point d'entrée CLI |
| `requirements.txt` | Dépendances Python |
| `README.md` | Documentation unifiée (CE FICHIER) |

### Code Source (src/core/)

| Module | Fonction principale |
|--------|-------------------|
| **config.py** | `ensure_directories()` |
| **importer.py** | `import_faxcloud_export()` |
| **analyzer.py** | `analyze_data()` |
| **reporter.py** | `generate_report()` |
| **validation_rules.py** | `validate_number()` |

### Commandes Essentielles

```bash
pip install -r requirements.txt
python main.py init
python main.py import --file exports/data.csv --contract CONTRACT_001
python main.py list
python main.py --help
```

---

## 📈 Résultats de test

- **CSV:** 25,957 lignes
- **Temps:** 4 secondes total
- **Taux réussite:** 97.52%
- **Utilisateurs:** 193 tracés
- **Rapport:** JSON complet généré

---

## ✅ Fonctionnalités

- [x] Import CSV/XLSX multi-encodage
- [x] Validation numéros France
- [x] Validation pages
- [x] Validation type FAX
- [x] Statistiques complètes
- [x] Rapports JSON UUID
- [x] QR codes PNG
- [x] CLI complète
- [x] Logging détaillé

---

## 🚀 Prochaines étapes
1. ✅ Système fonctionne complètement
2. 🔜 Interface web
3. 🔜 Export PDF/Excel
4. 🔜 Validation Asterisk (v2.0)

---

**Généré:** 10 Décembre 2025  
**Version:** 1.0.0  
**Statut:** ✅ Production-Ready

*Consultation unifiée de toute la documentation en un seul fichier*
