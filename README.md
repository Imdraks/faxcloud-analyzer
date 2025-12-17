# 📊 FaxCloud Analyzer - Documentation Complète

**Analyseur intelligent et complet pour fichiers d'export FAX FaxCloud**

> **Version:** 1.0.0 | **Statut:** ✅ Production-Ready | **Python:** 3.13.9 | **Dernière mise à jour:** 11 Décembre 2025

---

## 📑 Table des Matières

1. [À quoi sert ce projet?](#à-quoi-sert-ce-projet)
2. [Prérequis et configuration](#prérequis-et-configuration)
3. [Installation complète](#installation-complète)
4. [Utilisation rapide](#utilisation-rapide)
5. [Commandes principales](#commandes-principales)
6. [Architecture technique](#architecture-technique)
7. [Format des données](#format-des-données)
8. [Règles de validation](#règles-de-validation)
9. [Statistiques et rapports](#statistiques-et-rapports)
10. [Modules détaillés](#modules-détaillés)
11. [Structure de base de données](#structure-de-base-de-données)
12. [Flux de données](#flux-de-données)
13. [Dépannage](#dépannage)
14. [Prochaines étapes](#prochaines-étapes)

---

## 🎯 À quoi sert ce projet?

### Le Problème
Vous avez des fichiers d'export FAX provenant de la plateforme **FaxCloud** (format CSV/XLSX) contenant:
- Des milliers de lignes de données FAX
- Des numéros mal formatés (0X, +33X, 0033X)
- Des données incomplètes ou erronées
- Besoin de statistiques détaillées
- Besoin de validation automatique

### La Solution
**FaxCloud Analyzer** automatise complètement le processus:

```
CSV/XLSX brut → Import → Validation → Normalisation → Analyse → Rapport JSON
```

### Objectifs principaux
1. **Importer** des fichiers CSV/XLSX automatiquement
2. **Normaliser** les numéros de téléphone (tous formats → 33XXXXXXXXXX)
3. **Valider** chaque ligne selon des règles strictes
4. **Analyser** les données pour extraire des statistiques
5. **Générer** des rapports JSON avec UUID unique
6. **Tracer** erreurs et anomalies avec catégorisation
7. **Persister** les résultats sur disque et base SQLite

### Cas d'usage réels
- ✅ Audit de consommation FAX (CHU NICE)
- ✅ Facturation FAX par utilisateur
- ✅ Détection anomalies numéros
- ✅ Statistiques appels internationaux
- ✅ Reporting automatisé

### Technologies utilisées
- **Python 3.13.9** - Langage principal
- **pandas** - Traitement données CSV/XLSX
- **openpyxl** - Support fichiers Excel natif
- **qrcode/pillow** - Génération codes QR
- **SQLite** - Base de données locale
- **JSON** - Format rapports standard
- **logging** - Traçabilité complète

---

## 🔧 Prérequis et configuration

### Système d'exploitation
- **Windows 10+** (avec PowerShell 5.1+) ✅ **RECOMMANDÉ**
- Linux/Mac (en théorie compatible)

### Accès réseau/fichiers
- ✅ Accès lecture/écriture au répertoire du projet
- ✅ Accès fichiers source CSV/XLSX
- ✅ Espace disque: 500 MB minimum

### Logiciels requis
1. **Python 3.8+** (testé avec 3.13.9)
   - Télécharger: https://www.python.org/
   - Vérifier: `python --version`

2. **pip** (gestionnaire paquets Python)
   - Inclus avec Python 3.4+
   - Vérifier: `pip --version`

3. **Git** (optionnel, pour versionner)
   - Télécharger: https://git-scm.com/

### Vérification prérequis

```bash
# Vérifier Python
python --version
# Résultat attendu: Python 3.8.0+

# Vérifier pip
pip --version
# Résultat attendu: pip 21.0+
```

## 🧾 Journal d'audit (traçabilité)

Une table SQLite `audit_log` enregistre automatiquement des événements (best-effort):
- `upload` (import via web)
- `export_csv`, `export_json`
- `delete_report`

Champs principaux: `ts`, `user`, `action`, `report_id`, `ip`, `user_agent`, `meta_json`.


---

## 🚀 Installation complète

### Étape 1: Cloner/télécharger le projet

**Option A - Via Git:**
```bash
git clone https://github.com/your-repo/faxcloud-analyzer.git
cd faxcloud-analyzer
```

**Option B - Télécharger ZIP:**
1. Télécharger le ZIP du projet
2. Extraire dans `C:\Users\VotreUser\Documents\Projet\`
3. Ouvrir PowerShell dans ce dossier

### Étape 2: Créer un environnement virtuel (IMPORTANT!)

**Pourquoi?** Isoler les dépendances du projet de votre Python système.

```bash
# Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Vérifier activation (le prompt commence par "(venv)")
(venv) PS C:\Users\VOXCL\Documents\Projet\faxcloud-analyzer>
```

**Troubleshoot si erreur "ExecutionPolicy":**
```bash
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
# Puis refaire: .\venv\Scripts\Activate.ps1
```

### Étape 3: Installer les dépendances

```bash
# Mettre à jour pip
pip install --upgrade pip

# Installer les dépendances du projet
pip install -r requirements.txt

# Vérifier installation
pip list
# Vous devez voir: pandas, openpyxl, qrcode, pillow
```

### Étape 4: Initialiser les répertoires

```bash
# Cette commande crée les dossiers manquants
python main.py init

# Résultat attendu:
# ✓ Répertoire /data/imports créé
# ✓ Répertoire /data/reports créé
# ✓ Répertoire /data/reports_qr créé
# ✓ Répertoire /logs créé
```

### Étape 5: Test de configuration

```bash
# Afficher l'aide
python main.py --help

# Résultat attendu: Menu avec commandes
```

---

## 💻 Utilisation rapide

### Commandes essentielles

#### 1. Initialiser la base de données
```bash
python main.py init
```
Crée la structure SQLite et les répertoires nécessaires.

#### 2. Importer un fichier
```bash
python main.py import \
    --file exports/Consommation_CHU_NICE_20251104_104525.csv \
    --contract CONTRACT_CHU_NICE \
    --start 2024-11-01 \
    --end 2024-11-30
```
Traite un fichier CSV/XLSX et génère un rapport complet.

**Paramètres détaillés:**

| Paramètre | Obligatoire | Format | Exemple |
|-----------|------------|--------|---------|
| `--file` | OUI | Chemin fichier | `exports/data.csv` |
| `--contract` | NON | Texte libre | `CHU_NICE` |
| `--start` | NON | YYYY-MM-DD | `2024-11-01` |
| `--end` | NON | YYYY-MM-DD | `2024-12-31` |

#### 3. Lister les rapports
```bash
python main.py list
```
Affiche tous les rapports générés avec les statistiques.

#### 4. Consulter un rapport
```bash
python main.py view --report-id <UUID>
```
Affiche les détails complets d'un rapport.

#### 5. Aide
```bash
python main.py --help
```

#### 6. Activer le mode debug
```bash
python main.py --debug import --file exports/data.csv --contract TEST
```
Le flag `--debug` augmente la verbosité des logs (console + `logs/analyzer.log`).

#### 7. Lancer l'interface web statique (Windows)
```bat
run_web.bat 8000
```
Ouvre un serveur HTTP local sur le dossier `web` (port optionnel, défaut 8000).

---

## 🔄 Étapes de fonctionnement

### Étape 0: Préparation

```bash
# 1. Activer l'environnement virtuel
cd C:\Users\VOXCL\Documents\Projet\faxcloud-analyzer
.\venv\Scripts\Activate.ps1

# 2. Placer le fichier CSV dans exports/
# Exemple: exports/Consommation_CHU NICE_20251104_104525.csv
```

### Étape 1: IMPORTER

```bash
python main.py import \
  --file "exports/Consommation_CHU NICE_20251104_104525.csv" \
  --contract "CHU_NICE" \
  --start "2024-11-01" \
  --end "2024-12-31"
```

**Que se passe-t-il?**
1. Lit le fichier CSV
2. Détecte séparateur (`;`)
3. Essaie encodage UTF-8 → Latin-1
4. Charge les lignes en mémoire
5. Affiche: `✓ XXXX lignes importées`

### Étape 2: ANALYSER

Automatiquement après import, le système:

1. **Valide chaque ligne**:
   - Normalise le numéro: `0145221134` → `33145221134`
   - Valide le numéro: longueur=11, indicatif=33
   - Valide les pages: >= 1, numérique
   - Valide type FAX: SF ou RF

2. **Calcule statistiques**:
   - Total FAX
   - Envoyés vs Reçus
   - Pages par type
   - Erreurs par type et utilisateur
   - Taux de réussite

### Étape 3: GÉNÉRER RAPPORT

```
RAPPORT GÉNÉRÉ
==============

ID: 2c37d596-509f-4cf8-b74f-3248248e7b5d
Contrat: CHU_NICE
Période: 2024-11-01 à 2024-12-31

STATISTIQUES
============

Total FAX: 25,957
  ├─ Envoyés (SF): 8,350
  └─ Reçus (RF): 16,962

Pages: 60,942
  ├─ Envoyées: 13,728
  └─ Reçues: 47,214

Erreurs: 645 (2.48%)
  ├─ Pages invalides: 538
  ├─ Longueur incorrecte: 294
  └─ Indicatif invalide: 116

Taux réussite: 97.52%
```

### Étape 4: CONSULTER LE RAPPORT

```bash
# Afficher le rapport
python main.py view --report-id 2c37d596-509f-4cf8-b74f-3248248e7b5d

# Ou consulter directement le fichier
type data\reports\2c37d596-509f-4cf8-b74f-3248248e7b5d.json
```

---

## 🏗️ Architecture technique

### Vue d'ensemble

```
                    ┌─────────────────────────┐
                    │   Fichier CSV/XLSX      │
                    │   (25K+ lignes)         │
                    └───────────┬─────────────┘
                                │
                    ┌───────────▼──────────────┐
                    │  1️⃣ IMPORTER (importer.py)│
                    │                          │
                    │ • Détecte format CSV/XLS │
                    │ • Teste UTF-8, Latin-1  │
                    │ • Essaie séparateur ; , │
                    │ • Normalise colonnes    │
                    └───────────┬──────────────┘
                                │
                    ┌───────────▼──────────────┐
                    │  2️⃣ ANALYSER (analyzer.py)│
                    │                          │
                    │ • Valide chaque ligne    │
                    │ • Normalise numéros      │
                    │ • Compte erreurs         │
                    │ • Génère statistiques    │
                    └───────────┬──────────────┘
                                │
                    ┌───────────▼──────────────┐
                    │ 3️⃣ REPORTER (reporter.py)│
                    │                          │
                    │ • Génère UUID            │
                    │ • Crée QR code (optionnel)│
                    │ • Sauvegarde JSON        │
                    │ • Retourne rapport_id    │
                    └───────────┬──────────────┘
                                │
                    ┌───────────▼──────────────┐
                    │   Rapports JSON + PNG    │
                    │   data/reports/{id}.json │
                    │   data/reports_qr/{id}.png
                    └──────────────────────────┘
```

### Modules core

#### **config.py** - Configuration
- Configuration centralisée
- Chemins répertoires
- Paramètres application
- Logging

#### **importer.py** - Importation
- Lecture CSV/XLSX
- Validation structure
- Normalisation données
- Gestion erreurs

#### **analyzer.py** - Analyse
- Normalisation numéros
- Validation numéros
- Analyse complète
- Statistiques détaillées

#### **reporter.py** - Rapports
- Génération UUID
- Création QR codes
- Formatage JSON
- Listings rapports

#### **db.py** - Base de données
- Initialisation SQLite
- Insertion rapports
- Consultation base
- Gestion statistiques

#### **main.py** - Orchestration
- Point d'entrée CLI
- Workflow complet
- Gestion d'erreurs

---

## 📊 Format des données

### Colonnes CSV/XLSX attendues

| Index | Colonne | Contenu | Exemple |
|-------|---------|---------|---------|
| A | Fax ID | Identifiant unique | FAX12345 |
| B | Utilisateur | Nom personne | Jean Dupont |
| D | Mode | SF (envoyé) ou RF (reçu) | SF |
| F | Date/Heure | Timestamp | 2024-12-10 14:30:00 |
| G | Numéro d'envoi | Numéro source | 0133445566 |
| H | Numéro appelé | **Critique** | 0622334455 |
| K | Pages réelles | Nombre pages | 5 |

### Format JSON de sortie

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
      "ne_commence_pas_33": 1
    }
  },
  
  "entries": [
    {
      "id": "UUID",
      "fax_id": "FAX001",
      "utilisateur": "Jean Dupont",
      "type": "send",
      "numero_original": "0622334455",
      "numero_normalise": "33622334455",
      "valide": true,
      "pages": 5,
      "datetime": "ISO8601",
      "erreurs": []
    }
  ]
}
```

---

## ✅ Règles de validation

### Normalisation des numéros

**Étape 1: Retirer caractères non-numériques**

| Format original | Résultat | Raison |
|---|---|---|
| `03.27.93.69.43` | `0327936943` | Points retirés |
| `+33 1 45 22 11 34` | `33145221134` | Espaces et + retirés |
| `+33-1-45-22-11-34` | `33145221134` | Tirets retirés |
| `0033145221134` | `33145221134` | Format international |

**Étape 2: Conversion formats français**

```
0145221134 (10 chiffres) → 33145221134 (11 chiffres)
+33145221134 → 33145221134
0033145221134 → 33145221134
```

### Validation des numéros

Un numéro est **valide** si:

1. ✅ **Longueur exacte = 11 chiffres**
   - `33145221134` ✅ (11 chiffres)
   - `0145221134` ❌ (10 chiffres)
   - `0033145221134` ❌ (13 chiffres)

2. ✅ **Commence par 33**
   - `33145221134` ✅
   - `0145221134` ❌ (commence par 0)
   - `4412345678` ❌ (indicatif UK)

3. ✅ **Contient seulement des chiffres**
   - `33145221134` ✅
   - `33 145 221 134` ❌ (espaces)
   - `33145-221-134` ❌ (tirets)

### Types d'erreurs

| Erreur | Message | Exemple |
|--------|---------|---------|
| 1 | Numéro vide | Champ vide ou NULL |
| 2 | Longueur incorrecte | `0145221134` (10 au lieu de 11) |
| 3 | Indicatif invalide | Ne commence pas par 33 |
| 4 | Format invalide | Caractères illisibles |

### Pseudo-code validation

```python
def validate_number(numero_brut):
    # Normaliser
    numero = re.sub(r'\D', '', str(numero_brut))
    
    # Conversion 0X → 33X
    if numero.startswith("0"):
        numero = "33" + numero[1:]
    
    # Vérifications
    if not numero:
        return False, "Numéro vide"
    if len(numero) != 11:
        return False, "Longueur incorrecte"
    if not numero.startswith("33"):
        return False, "Indicatif invalide"
    
    return True, None
```

---

## 📈 Statistiques et rapports

### Statistiques globales

| Métrique | Calcul | Exemple |
|---|---|---|
| **Total FAX envoyés** | Compte tous les mode="SF" | 1,250 |
| **Total FAX reçus** | Compte tous les mode="RF" | 890 |
| **Total pages envoyées** | Sum(pages) où mode="SF" | 5,432 pages |
| **Total pages reçues** | Sum(pages) où mode="RF" | 3,210 pages |
| **Total pages** | pages_envoyees + pages_recues | 8,642 pages |
| **Taux de réussite** | (fax_valides / total) × 100 | 94.2% |

### Formule du taux de réussite

$$\text{Taux} = \frac{\text{Total FAX} - \text{Erreurs}}{\text{Total FAX}} \times 100$$

### Statistiques par utilisateur

| Utilisateur | Envois | Erreurs | Taux réussite | Pages |
|---|---|---|---|---|
| Alice Dupont | 145 | 8 | 94.5% | 820 |
| Bob Martin | 98 | 5 | 94.9% | 560 |
| Carol Leblanc | 112 | 14 | 87.5% | 640 |

---

## 🗄️ Structure de base de données

### Table `reports`
```sql
id (TEXT PRIMARY KEY)
date_rapport (TEXT)
contract_id (TEXT)
date_debut (TEXT)
date_fin (TEXT)
total_fax (INTEGER)
fax_envoyes (INTEGER)
fax_recus (INTEGER)
pages_totales (INTEGER)
erreurs_totales (INTEGER)
taux_reussite (REAL)
qr_path (TEXT)
url_rapport (TEXT)
created_at (TEXT)
```

### Table `fax_entries`
```sql
id (TEXT PRIMARY KEY)
report_id (TEXT FK)
fax_id (TEXT)
utilisateur (TEXT)
type (TEXT) -- "send" ou "receive"
numero_original (TEXT)
numero_normalise (TEXT)
valide (BOOLEAN)
pages (INTEGER)
datetime (TEXT)
erreurs (TEXT) -- JSON
```

---

## 🔄 Flux de données

```
Fichier CSV/XLSX
      │
      ▼
┌─────────────────────┐
│ importer.py         │
│ Lire & valider      │
└─────────────────────┘
      │
      ▼
   [Rows] (List[Dict])
      │
      ▼
┌─────────────────────┐
│ analyzer.py         │
│ Normaliser & compter│
└─────────────────────┘
      │
      ▼
[Analysis] (entries + stats)
      │
      ▼
┌─────────────────────┐
│ reporter.py         │
│ UUID + QR + JSON    │
└─────────────────────┘
      │
      ├─────────────────┬──────────┐
      │                 │          │
      ▼                 ▼          ▼
    [JSON]          [PNG QR]   [SQLite]
```

---

## 📁 Structure du projet

```
faxcloud-analyzer/
├── main.py                    # Point d'entrée
├── requirements.txt           # Dépendances
├── README.md                  # Cette documentation
│
├── src/core/                  # Code source
│   ├── __init__.py
│   ├── config.py
│   ├── db.py
│   ├── importer.py
│   ├── analyzer.py
│   └── reporter.py
│
├── web/                       # Interface web
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── data/                      # Données générées
│   ├── imports/               # Fichiers importés
│   ├── reports/               # Rapports JSON
│   └── reports_qr/            # QR codes PNG
│
├── database/                  # Base de données
│   └── faxcloud.db
│
├── exports/                   # Fichiers source
│   └── sample_*.csv
│
└── logs/                      # Fichiers journaux
    └── analyzer.log
```

---

## 🔧 Dépannage

### Erreur: "ExecutionPolicy"
```bash
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\venv\Scripts\Activate.ps1
```

### Erreur: "Module not found"
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Erreur: "File not found"
- Vérifiez que le fichier existe dans `exports/`
- Utilisez le chemin complet: `C:\Users\...\exports\file.csv`

### Erreur: "Permission denied"
- Fermez les autres programmes accédant au fichier
- Relancez PowerShell en administrateur

### Base de données corrompue
```bash
# Supprimer l'ancienne base
rm database\faxcloud.db

# Réinitialiser
python main.py init
```

---

## 📚 Modules détaillés

### importer.py
**Responsabilités:**
- Lire fichiers CSV et XLSX
- Valider structure (colonnes)
- Normaliser données (dates, séparateurs)
- Gérer erreurs import

**Fonction principale:**
```python
import_faxcloud_export(file_path) -> dict
```

### analyzer.py
**Responsabilités:**
- Normaliser numéros
- Valider numéros
- Calculer statistiques
- Détecter erreurs

**Fonctions principales:**
```python
normalize_number(numero) -> str
validate_number(numero) -> dict
analyze_data(rows, contract_id, date_debut, date_fin) -> dict
```

### reporter.py
**Responsabilités:**
- Générer UUID uniques
- Créer QR codes PNG
- Formater JSON structuré
- Lister rapports

**Fonctions principales:**
```python
generate_report(analysis) -> dict
generate_qr_code(report_id, base_url) -> str
list_reports() -> list
```

### db.py
**Responsabilités:**
- Initialiser SQLite
- Insérer rapports
- Insérer entrées FAX
- Consulter statistiques

**Fonctions principales:**
```python
init_database()
insert_report_to_db(report_id, report_json, qr_path)
get_all_reports() -> list
get_report_by_id(report_id) -> dict
```

---

## 🎯 Prochaines étapes

### Court terme (Phase 2)
- [ ] API REST Flask complète
- [ ] Intégration Asterisk (validation FAX/VOIX)
- [ ] Page détail rapport (report.html)
- [ ] Export PDF des rapports
- [ ] Graphiques statistiques (Chart.js)

### Moyen terme (Phase 3)
- [ ] Authentification utilisateurs
- [ ] Historique complet
- [ ] Email notifications
- [ ] Planification imports auto
- [ ] Multi-utilisateur

### Long terme (Phase 4)
- [ ] API publique
- [ ] Mobile app native
- [ ] Analytics avancée
- [ ] Machine Learning
- [ ] Intégrations tierces

---

## 📦 Dépendances Python

```
pandas==2.0.0           # Traitement CSV/XLSX
openpyxl==3.10.0        # Support Excel
qrcode==7.4.2           # Génération QR codes
pillow==10.0.0          # Traitement images
flask==3.0.0            # API REST (futur)
requests==2.31.0        # HTTP client
python-dateutil==2.8.2  # Manipulation dates
```

Installer avec:
```bash
pip install -r requirements.txt
```

---

## 💡 Exemple complet d'utilisation

### Input CSV
```
Fax ID;Utilisateur;Mode;Date/Heure;Numéro envoi;Numéro appelé;Pages
FAX001;Jean Dupont;SF;2024-12-10 14:30;0133445566;0622334455;5
FAX002;Marie Martin;RF;2024-12-10 15:45;0622334455;0133445566;3
FAX003;Pierre Leblanc;SF;2024-12-10 16:20;0188776655;INVALID;0
```

### Commande
```bash
python main.py import --file exports/data.csv --contract TEST_001
```

### Résultat

**Console:**
```
✓ 3 lignes importées
✓ Analyse complète
✓ Rapport généré: 2c37d596-509f-4cf8-b74f-3248248e7b5d
✓ QR Code créé
✓ Base SQLite mise à jour
```

**Fichiers créés:**
- `data/reports/2c37d596-509f-4cf8-b74f-3248248e7b5d.json`
- `data/reports_qr/2c37d596-509f-4cf8-b74f-3248248e7b5d.png`
- `database/faxcloud.db` (mise à jour)

**Rapport JSON:**
```json
{
  "report_id": "2c37d596-509f-4cf8-b74f-3248248e7b5d",
  "statistics": {
    "total_fax": 3,
    "fax_envoyes": 2,
    "fax_recus": 1,
    "pages_totales": 8,
    "erreurs_totales": 1,
    "taux_reussite": 66.67
  }
}
```

---

## 📞 Support

**Questions?** Consultez les sections de cette documentation:
- Installation: voir [Installation complète](#installation-complète)
- Utilisation: voir [Utilisation rapide](#utilisation-rapide)
- Technique: voir [Architecture technique](#architecture-technique)
- Validation: voir [Règles de validation](#règles-de-validation)

---

## ✨ Fonctionnalités

✅ Importation CSV/XLSX flexible  
✅ Normalisation numéros automatique  
✅ Validation stricte (5 règles)  
✅ Statistiques complètes  
✅ Rapports JSON structurés  
✅ QR codes PNG  
✅ Base SQLite locale  
✅ CLI complète  
✅ Logs détaillés  
✅ Interface web responsive  

---

**Version:** 1.0.0  
**Statut:** ✅ Production-ready  
**Dernière mise à jour:** 11 Décembre 2025  
**Maintenance:** Activement maintenu
