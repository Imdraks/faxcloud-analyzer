# 🏗️ ARCHITECTURE TECHNIQUE - FaxCloud Analyzer

## 📌 Vue d'ensemble de l'architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         CLI / API                           │
│                      (main.py)                              │
└──────────────────────────┬──────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
    ┌───▼───┐         ┌───▼───┐         ┌───▼───┐
    │IMPORT │         │ANALYZE│         │REPORT │
    │       │         │       │         │       │
    │.py    │         │.py    │         │.py    │
    └───┬───┘         └───┬───┘         └───┬───┘
        │                 │                 │
    ┌───▼─────────────┬───▼──────┐    ┌────▼─────┐
    │  CSV/XLSX       │Validation│    │QR Code   │
    │  Normalized     │Statistics│    │JSON      │
    └───┬─────────────┴───┬──────┘    └────┬─────┘
        │                 │                 │
        └─────────────────┼─────────────────┘
                          │
                      ┌───▼───┐
                      │  DB   │
                      │ .py   │
                      └───┬───┘
                          │
                      ┌───▼──────┐
                      │ SQLite   │
                      │ Database │
                      └──────────┘
```

---

## 🔧 PILE TECHNOLOGIQUE

### Backend
- **Python 3.8+**: Langage principal
- **pandas 2.0**: Lecture CSV/XLSX
- **openpyxl**: Support Excel
- **qrcode 7.4**: Génération QR codes
- **pillow 10.0**: Traitement images
- **sqlite3**: Base de données (intégré)

### Frontend (Futur)
- **HTML5**: Markup
- **CSS3**: Styling responsive
- **Vanilla JavaScript**: Interactions
- **QR Scanner JS**: Lecture QR codes

### Infrastructure
- **Fichiers locaux**: Stockage JSON et QR codes
- **SQLite**: Persistance données
- **Logs**: Fichiers texte

---

## 📁 MODULES CORE

### 1. `config.py`
**Rôle**: Configuration centralisée

**Exporté**:
```python
# Chemins
DIRS = {
    'imports': ...,
    'reports_json': ...,
    'reports_qr': ...,
    'database': ...,
    'logs': ...
}
DATABASE_PATH = ...

# Configuration
WEB_HOST, WEB_PORT, BASE_URL
LOG_LEVEL, LOG_FORMAT
ACCEPTED_FORMATS
VALIDATION_RULES = {
    'phone_length': 11,
    'country_code': '33'
}
CSV_COLUMNS = {
    'fax_id': 0,
    'mode': 3,
    ...
}

# Fonctions
ensure_directories()
setup_logging()
```

---

### 2. `importer.py`
**Rôle**: Lecture et normalisation des fichiers

**Fonctions principales**:

```python
def import_faxcloud_export(file_path: str) -> Dict
    """Importe un fichier CSV/XLSX"""
    Retourne: {
        "success": bool,
        "rows": List[Dict],
        "total_rows": int,
        "errors": List[str]
    }

def validate_structure(df: pd.DataFrame) -> Dict
    """Valide la structure du fichier"""

def normalize_data(df: pd.DataFrame) -> List[Dict]
    """Normalise les données"""

def normalize_datetime(value) -> str
    """Normalise les dates"""
```

**Entrée**: Fichier CSV/XLSX
**Sortie**: Liste de dictionnaires normalisés

---

### 3. `analyzer.py`
**Rôle**: Analyse et validation des données

**Fonctions principales**:

```python
def normalize_number(raw_number: str) -> str
    """Normalise un numéro de téléphone"""
    Input: "0622334455", "+33622...", "INVALID"
    Output: "33622334455", ""

def validate_number(normalized: str) -> Dict
    """Valide un numéro normalisé"""
    Retourne: {
        "is_valid": bool,
        "normalized": str,
        "errors": List[str]
    }

def analyze_data(rows, contract_id, date_debut, date_fin) -> Dict
    """Analyse complète des données"""
    Retourne: {
        "entries": List[Dict],
        "statistics": Dict,
        "contract_id": str,
        "date_debut": str,
        "date_fin": str
    }
```

**Flux**:
1. Normaliser chaque numéro
2. Valider chaque numéro
3. Compter les statistiques globales
4. Compter par utilisateur
5. Calculer le taux de réussite

---

### 4. `reporter.py`
**Rôle**: Génération de rapports et QR codes

**Fonctions principales**:

```python
def generate_report(analysis: Dict) -> Dict
    """Génère un rapport complet"""
    Retourne: {
        "success": bool,
        "report_id": str,
        "report_url": str,
        "qr_path": str
    }

def generate_qr_code(report_id: str, base_url: str) -> str
    """Génère un QR code PNG"""
    Retourne: chemin du fichier PNG

def save_report_json(report_id: str, report_json: Dict) -> bool
    """Sauvegarde le rapport JSON"""

def load_report_json(report_id: str) -> Optional[Dict]
    """Charge un rapport JSON"""

def list_reports() -> list
    """Liste tous les rapports"""

def generate_summary(report_json: Dict) -> str
    """Génère un résumé texte"""
```

**Sorties**:
- `data/reports/{report_id}.json`: Rapport structuré
- `data/reports_qr/{report_id}.png`: QR code image

---

### 5. `db.py`
**Rôle**: Gestion de la base de données SQLite

**Fonctions principales**:

```python
def init_database(db_path=None)
    """Initialise la base de données"""
    Crée les tables: reports, fax_entries

def insert_report_to_db(report_id, report_json, qr_path)
    """Insère un rapport et ses entrées"""

def get_all_reports() -> List[Dict]
    """Récupère tous les rapports"""

def get_report_by_id(report_id: str) -> Optional[Dict]
    """Récupère un rapport complet"""

def get_reports_by_contract(contract_id) -> List[Dict]
    """Récupère rapports d'un contrat"""

def get_statistics() -> Dict
    """Statistiques globales"""

def delete_report(report_id: str) -> bool
    """Supprime un rapport"""
```

**Tables**:

```sql
reports (
    id: TEXT PRIMARY KEY,
    date_rapport: TEXT,
    contract_id: TEXT,
    date_debut: TEXT,
    date_fin: TEXT,
    fichier_source: TEXT,
    total_fax: INTEGER,
    fax_envoyes: INTEGER,
    fax_recus: INTEGER,
    pages_totales: INTEGER,
    erreurs_totales: INTEGER,
    taux_reussite: REAL,
    qr_path: TEXT,
    url_rapport: TEXT,
    created_at: TEXT
)

fax_entries (
    id: TEXT PRIMARY KEY,
    report_id: TEXT FK,
    fax_id: TEXT,
    utilisateur: TEXT,
    type: TEXT (send/receive),
    numero_original: TEXT,
    numero_normalise: TEXT,
    valide: BOOLEAN,
    pages: INTEGER,
    datetime: TEXT,
    erreurs: TEXT (JSON)
)
```

---

### 6. `main.py`
**Rôle**: Orchestration et CLI

**Fonctions principales**:

```python
def process_export(file_path, contract_id, date_debut, date_fin) -> Dict
    """Traite un export complet"""
    Étapes:
    1. import_faxcloud_export()
    2. analyze_data()
    3. generate_report()
    4. insert_report_to_db()

def main()
    """Point d'entrée CLI"""
    Commandes: import, list, view, init
```

**Commandes CLI**:
- `import`: Traiter un fichier
- `list`: Lister les rapports
- `view`: Consulter un rapport
- `init`: Initialiser le projet

---

## 🔄 FLUX DE DONNÉES

### Import → Analyse → Rapport

```
Fichier CSV/XLSX
      │
      ▼
┌─────────────────────────┐
│ importer.py             │
├─────────────────────────┤
│ 1. Lire fichier         │
│ 2. Valider structure    │
│ 3. Normaliser données   │
└─────────────────────────┘
      │
      ▼
   [Rows]
 (List[Dict])
      │
      ▼
┌─────────────────────────┐
│ analyzer.py             │
├─────────────────────────┤
│ Pour chaque row:        │
│  1. normalize_number()  │
│  2. validate_number()   │
│  3. Compter stats       │
└─────────────────────────┘
      │
      ▼
[Analysis]
{entries + stats}
      │
      ▼
┌─────────────────────────┐
│ reporter.py             │
├─────────────────────────┤
│ 1. Générer UUID         │
│ 2. Créer QR code        │
│ 3. Formater JSON        │
│ 4. Sauvegarder fichiers │
└─────────────────────────┘
      │
      ├─────────────────────────┐
      │                         │
      ▼                         ▼
  [JSON]                   [PNG QR]
  Rapport                  Code
      │                         │
      └──────────────┬──────────┘
                     │
                     ▼
            ┌─────────────────────┐
            │ db.py               │
            ├─────────────────────┤
            │ insert_report_to_db │
            └─────────────────────┘
                     │
                     ▼
               [SQLite DB]
```

---

## 📊 STRUCTURE JSON RAPPORT

```json
{
  "report_id": "UUID",
  "timestamp": "ISO8601",
  "contract_id": "CONTRACT_001",
  "date_debut": "YYYY-MM-DD",
  "date_fin": "YYYY-MM-DD",
  
  "statistics": {
    "total_fax": 20,
    "fax_envoyes": 12,
    "fax_recus": 8,
    "pages_totales": 97,
    "erreurs_totales": 3,
    "taux_reussite": 85.0,
    
    "erreurs_par_type": {
      "numero_vide": 1,
      "longueur_incorrecte": 1,
      "ne_commence_pas_33": 0,
      "caracteres_invalides": 1
    },
    
    "envois_par_utilisateur": {
      "Jean Dupont": 5,
      "Marie Martin": 5
    },
    
    "erreurs_par_utilisateur": {
      "Jean Dupont": 0,
      "Marie Martin": 1
    }
  },
  
  "entries": [
    {
      "id": "UUID",
      "fax_id": "FAX001",
      "utilisateur": "Jean Dupont",
      "type": "send|receive",
      "numero_original": "0622334455",
      "numero_normalise": "33622334455",
      "valide": true,
      "pages": 5,
      "datetime": "ISO8601",
      "erreurs": []
    }
  ],
  
  "qr_code_url": "/reports_qr/{report_id}.png",
  "report_url": "/reports/{report_id}"
}
```

---

## 🔐 SÉCURITÉ

### Points d'entrée validés
- ✓ Chemin fichier (Path exists check)
- ✓ Format fichier (Extension check)
- ✓ Structure données (Colonne check)
- ✓ Types données (Type conversion)

### Injection prévenue
- ✓ Pas d'exécution code
- ✓ Paramètres escapés en DB
- ✓ Pas de chemins absolus en entrée

### Données sensibles
- ✓ Logs filtrés (pas de données sensibles)
- ✓ Base locale seulement
- ✓ Pas de transmission réseau

---

## 🚀 EXTENSIBILITÉ

### Points d'extension futur

**1. Détecteur Asterisk**
```python
# src/detectors/asterisk_detector.py
def detect_fax_vs_voice(numero: str) -> bool
    """Vérifie si c'est un FAX ou une voix"""
```

**2. API REST**
```python
# web/api.py
@app.route('/api/reports', methods=['GET'])
def get_reports():
    """API pour récupérer les rapports"""
```

**3. Export PDF**
```python
# reporter.py
def export_to_pdf(report_json: Dict) -> Path
    """Exporte un rapport en PDF"""
```

**4. Notifications Email**
```python
# notifier.py
def send_report_email(report_id: str, recipients: List[str])
    """Envoie un rapport par email"""
```

---

## 📈 PERFORMANCE

### Complexité

- **Normalisation/Validation**: O(n)
- **Analyse complète**: O(n)
- **Sauvegarde DB**: O(n)
- **Global**: O(n) où n = nombre de lignes

### Mémoire

- Stockage rows: O(n)
- Stockage entries: O(n)
- Global: O(n)

### Optimisations possibles

- [ ] Batch insert en base
- [ ] Streaming pour gros fichiers
- [ ] Cache des rapports
- [ ] Indexation multi-colonnes

---

## 🧪 TESTS

### Tests unitaires

```python
# test_analyzer.py
def test_normalize_number():
    assert normalize_number("0622334455") == "33622334455"
    assert normalize_number("INVALID") == ""

def test_validate_number():
    result = validate_number("33622334455")
    assert result["is_valid"] == True
    assert result["errors"] == []
```

### Tests d'intégration

```python
# test_integration.py
def test_complete_workflow():
    # Import
    # Analyze
    # Report
    # DB
```

---

## 📝 CONVENTIONS

### Nommage
- `snake_case` pour fonctions/variables
- `PascalCase` pour classes
- Prefix `_` pour privé

### Docstrings
```python
def fonction(param1: str, param2: int) -> Dict:
    """
    Description brève
    
    Args:
        param1: Description
        param2: Description
    
    Returns:
        Dict avec clés et valeurs
    """
```

### Imports
```python
# Standards
import json
import logging
from pathlib import Path

# Tiers
import pandas as pd

# Locaux
import config
```

---

**Version**: 1.0.0
**Dernière mise à jour**: 2024-12-10
