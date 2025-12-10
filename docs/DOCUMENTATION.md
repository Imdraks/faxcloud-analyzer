# 📋 DOCUMENTATION COMPLÈTE - FaxCloud Analyzer

## 1️⃣ PLAN D'ENSEMBLE DU PROJET

### 1.1 Vue d'ensemble
L'**FaxCloud Analyzer** est un système interne permettant d'analyser automatiquement les exports FaxCloud, de générer des rapports statistiques, et de fournir une interface web mobile pour la consultation des données.

### 1.2 Architecture générale

```
┌─────────────────────────────────────────────────────────┐
│                    UTILISATEUR                          │
└──────────────────────┬──────────────────────────────────┘
                       │
         ┌─────────────┴─────────────┐
         │                           │
    ┌────▼──────┐           ┌───────▼──────┐
    │ Interface │           │  Import CSV  │
    │   Web     │           │    /XLSX     │
    └────┬──────┘           └───────┬──────┘
         │                          │
         └──────────────┬───────────┘
                        │
            ┌───────────▼────────────┐
            │   MOTEUR D'ANALYSE     │
            │  (analyzer.py)         │
            │  - Normalisation       │
            │  - Validation          │
            │  - Statistiques        │
            └───────────┬────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
   ┌────▼───┐  ┌───────▼──────┐  ┌─────▼──┐
   │ Base    │  │ Rapports     │  │ QR     │
   │ SQLite  │  │ JSON         │  │ Codes  │
   │         │  │              │  │ PNG    │
   └─────────┘  └──────────────┘  └────────┘
```

---

## 2️⃣ MODULES ET RESPONSABILITÉS

### 2.1 `main.py` - Point d'entrée
**Rôle**: Orchestrateur du système

**Responsabilités**:
- Initialiser l'application
- Gérer le workflow complet
- Coordonner importer → analyser → rapporter
- Exposer l'API locale

**Pseudo-code**:
```python
def main():
    1. Initialiser logging et configuration
    2. Vérifier/créer la structure des dossiers
    3. Attendre une action utilisateur (API/CLI)
    4. Si import: appeler importer.py
    5. Si analyse: appeler analyzer.py
    6. Si rapport: appeler reporter.py
    7. Retourner JSON et fichiers générés
```

---

### 2.2 `importer.py` - Importation des données
**Rôle**: Lecture et validation des fichiers FaxCloud

**Responsabilités**:
- Lire les fichiers CSV ou XLSX
- Valider la structure des données
- Normaliser les données
- Retourner un dictionnaire Python structuré

**Pseudo-code**:
```python
def import_faxcloud_export(file_path: str) -> dict:
    1. Ouvrir le fichier CSV/XLSX
    2. Vérifier les colonnes obligatoires:
       - A: Fax ID
       - D: Mode (SF/RF)
       - H: Numéro appelé
       - F: Date et heure
       - G: Numéro d'envoi
       - K: Nombre de pages réel
       - B: Nom utilisateur
    3. Créer une liste de dictionnaires avec les lignes
    4. Valider que chaque ligne a les champs requis
    5. Retourner {
         "success": bool,
         "rows": [],
         "total_rows": int,
         "errors": []
       }
    
def normalize_data(rows: list) -> list:
    Pour chaque ligne:
    1. Convertir les dates en format ISO
    2. Normaliser les numéros (colonnes G et H)
    3. Mapper les modes (SF -> "send", RF -> "receive")
    4. Valider les types (pages = int, etc)
    5. Retourner la ligne nettoyée
```

**Colonnes attendues**:
| Index | Nom | Exemple | Type |
|-------|-----|---------|------|
| A | Fax ID | FAX12345 | str |
| B | Utilisateur | Jean Dupont | str |
| D | Mode | SF/RF | str |
| F | Date et heure | 2024-12-10 14:30:00 | datetime |
| G | Numéro d'envoi | 0133445566 | str |
| H | Numéro appelé | 0622334455 | str |
| K | Pages réelles | 5 | int |

---

### 2.3 `analyzer.py` - Moteur d'analyse
**Rôle**: Analyse les données et génère les statistiques

**Responsabilités**:
- Normaliser les numéros de téléphone
- Valider les numéros selon les règles
- Détecter les erreurs
- Calculer les statistiques
- Retourner les résultats structurés

**Pseudo-code - Normalisation des numéros**:
```python
def normalize_number(raw_number: str) -> str:
    """
    Entrée: "0133445566", "+33133445566", "33 1 33 44 55 66"
    Sortie: "33133445566" (11 chiffres commençant par 33)
    """
    1. Si vide ou None: return ""
    2. Supprimer tous les caractères non-numériques: re.sub(r"\D", "", raw)
    3. Si commence par "+33": remplacer par "33"
    4. Si commence par "0" (format français): remplacer "0" par "33"
    5. Retourner le numéro normalisé
    
def validate_number(normalized: str) -> dict:
    """
    Retourne: {
        "is_valid": bool,
        "normalized": str,
        "errors": []
    }
    """
    errors = []
    
    1. Si vide:
       errors.append("Numéro vide")
       return {"is_valid": False, "normalized": "", "errors": errors}
    
    2. Si len != 11:
       errors.append(f"Longueur incorrecte: {len} au lieu de 11")
    
    3. Si ne commence pas par "33":
       errors.append("Ne commence pas par 33")
    
    4. Si contient des caractères non-numériques:
       errors.append("Caractères invalides détectés")
    
    return {
        "is_valid": len(errors) == 0,
        "normalized": normalized,
        "errors": errors
    }
```

**Pseudo-code - Analyse des données**:
```python
def analyze_data(rows: list, contract_id: str, date_debut: str, date_fin: str) -> dict:
    """
    Analyse l'intégralité des données importées
    """
    
    # Initialiser les compteurs et structures
    stats = {
        "total_fax": 0,
        "fax_envoyes": 0,
        "fax_recus": 0,
        "pages_totales": 0,
        "erreurs_totales": 0,
        "taux_reussite": 0.0,
        "erreurs_par_type": {
            "numero_vide": 0,
            "longueur_incorrecte": 0,
            "ne_commence_pas_33": 0,
            "caracteres_invalides": 0
        },
        "envois_par_utilisateur": {},
        "erreurs_par_utilisateur": {}
    }
    
    entries = []
    
    # Parcourir chaque ligne
    Pour chaque row dans rows:
        1. Extraire les données:
           - fax_id = row['A']
           - utilisateur = row['B']
           - mode = row['D']  # SF ou RF
           - datetime = row['F']
           - numero_envoi = row['G']
           - numero_appele = row['H']
           - pages = row['K']
        
        2. Normaliser le numéro appelé:
           normalized = normalize_number(numero_appele)
           validation = validate_number(normalized)
        
        3. Déterminer le type:
           type_fax = "send" si mode == "SF" else "receive"
        
        4. Créer l'entrée:
           entry = {
               "id": uuid.uuid4(),
               "fax_id": fax_id,
               "utilisateur": utilisateur,
               "type": type_fax,
               "numero_original": numero_appele,
               "numero_normalise": normalized,
               "valide": validation["is_valid"],
               "pages": pages,
               "datetime": datetime,
               "erreurs": validation["errors"]
           }
        
        5. Ajouter à entries
        
        6. Mettre à jour les statistiques:
           stats["total_fax"] += 1
           
           if type_fax == "send":
               stats["fax_envoyes"] += 1
           else:
               stats["fax_recus"] += 1
           
           stats["pages_totales"] += pages
           
           if not validation["is_valid"]:
               stats["erreurs_totales"] += 1
               # Incrémenter le compteur d'erreur spécifique
               for error_msg in validation["errors"]:
                   if "vide" in error_msg:
                       stats["erreurs_par_type"]["numero_vide"] += 1
                   elif "Longueur" in error_msg:
                       stats["erreurs_par_type"]["longueur_incorrecte"] += 1
                   # etc...
           
           # Compter par utilisateur
           if utilisateur not in stats["envois_par_utilisateur"]:
               stats["envois_par_utilisateur"][utilisateur] = 0
           stats["envois_par_utilisateur"][utilisateur] += 1
           
           if not validation["is_valid"]:
               if utilisateur not in stats["erreurs_par_utilisateur"]:
                   stats["erreurs_par_utilisateur"][utilisateur] = 0
               stats["erreurs_par_utilisateur"][utilisateur] += 1
    
    # Calculer le taux de réussite
    if stats["total_fax"] > 0:
        stats["taux_reussite"] = ((stats["total_fax"] - stats["erreurs_totales"]) 
                                   / stats["total_fax"] * 100)
    
    return {
        "entries": entries,
        "statistics": stats,
        "contract_id": contract_id,
        "date_debut": date_debut,
        "date_fin": date_fin
    }
```

---

### 2.4 `reporter.py` - Génération de rapports
**Rôle**: Crée les rapports finaux, QR codes et sauvegarde en base

**Responsabilités**:
- Générer un UUID unique pour le rapport
- Créer le QR code
- Formater le rapport JSON
- Sauvegarder en base de données
- Retourner le chemin et l'ID du rapport

**Pseudo-code**:
```python
def generate_report(analysis_result: dict) -> dict:
    """
    Crée un rapport complet avec tous les fichiers associés
    """
    
    1. Générer l'UUID du rapport:
       report_id = str(uuid.uuid4())
    
    2. Générer le QR code:
       qr_path = generate_qr_code(report_id, base_url="http://localhost/reports")
       # Retourne: "reports_qr/[report_id].png"
    
    3. Formater le rapport JSON:
       report_json = {
           "report_id": report_id,
           "timestamp": datetime.now().isoformat(),
           "contract_id": analysis_result["contract_id"],
           "date_debut": analysis_result["date_debut"],
           "date_fin": analysis_result["date_fin"],
           "statistics": analysis_result["statistics"],
           "entries": analysis_result["entries"],
           "qr_code_url": f"/reports_qr/{report_id}.png",
           "report_url": f"/reports/{report_id}"
       }
    
    4. Sauvegarder le rapport JSON:
       with open(f"reports/{report_id}.json", "w") as f:
           json.dump(report_json, f, indent=2)
    
    5. Insérer en base de données:
       insert_report_to_db(report_id, report_json, qr_path)
    
    6. Retourner:
       {
           "success": True,
           "report_id": report_id,
           "report_url": f"/reports/{report_id}",
           "qr_path": f"/reports_qr/{report_id}.png"
       }

def generate_qr_code(report_id: str, base_url: str = "http://localhost/reports") -> str:
    """
    Génère un QR code unique pour le rapport
    Entrée: report_id = "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6"
    Sortie: chemin du fichier PNG généré
    """
    
    1. Créer l'URL cible:
       url = f"{base_url}/{report_id}"
       # Exemple: http://localhost/reports/a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6
    
    2. Utiliser qrcode library:
       qr = qrcode.QRCode(
           version=1,
           error_correction=qrcode.constants.ERROR_CORRECT_H,
           box_size=10,
           border=4
       )
       qr.add_data(url)
       qr.make(fit=True)
    
    3. Créer l'image:
       img = qr.make_image(fill_color="black", back_color="white")
    
    4. Créer le dossier s'il n'existe pas:
       os.makedirs("reports_qr", exist_ok=True)
    
    5. Sauvegarder:
       file_path = f"reports_qr/{report_id}.png"
       img.save(file_path)
    
    6. Retourner le chemin:
       return file_path
```

---

### 2.5 `db.py` - Gestion de la base de données
**Rôle**: Persistance des données dans SQLite

**Responsabilités**:
- Créer et initialiser la base de données
- Insérer les rapports
- Insérer les entrées FAX
- Consulter les données
- Exporter les rapports

**Pseudo-code**:
```python
def init_database(db_path: str = "database/faxcloud.db"):
    """
    Crée les tables si elles n'existent pas
    """
    
    1. Se connecter à SQLite:
       conn = sqlite3.connect(db_path)
       cursor = conn.cursor()
    
    2. Créer la table 'reports':
       CREATE TABLE IF NOT EXISTS reports (
           id TEXT PRIMARY KEY,
           date_rapport TEXT,
           contract_id TEXT,
           date_debut TEXT,
           date_fin TEXT,
           fichier_source TEXT,
           total_fax INTEGER,
           fax_envoyes INTEGER,
           fax_recus INTEGER,
           pages_totales INTEGER,
           erreurs_totales INTEGER,
           taux_reussite REAL,
           qr_path TEXT,
           url_rapport TEXT,
           created_at TEXT
       )
    
    3. Créer la table 'fax_entries':
       CREATE TABLE IF NOT EXISTS fax_entries (
           id TEXT PRIMARY KEY,
           report_id TEXT,
           fax_id TEXT,
           utilisateur TEXT,
           type TEXT,  -- "send" ou "receive"
           numero_original TEXT,
           numero_normalise TEXT,
           valide BOOLEAN,
           pages INTEGER,
           datetime TEXT,
           erreurs TEXT,  -- JSON string
           FOREIGN KEY (report_id) REFERENCES reports(id)
       )
    
    4. Créer les indexes:
       CREATE INDEX IF NOT EXISTS idx_reports_contract 
           ON reports(contract_id)
       CREATE INDEX IF NOT EXISTS idx_fax_entries_report 
           ON fax_entries(report_id)
    
    5. Valider et fermer:
       conn.commit()
       conn.close()

def insert_report_to_db(report_id: str, report_json: dict, qr_path: str):
    """
    Insère un rapport et ses entrées en base
    """
    
    1. Ouvrir la connexion
    2. Insérer le rapport:
       INSERT INTO reports (
           id, date_rapport, contract_id, date_debut, date_fin,
           total_fax, fax_envoyes, fax_recus, pages_totales,
           erreurs_totales, taux_reussite, qr_path, url_rapport,
           created_at
       ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    
    3. Pour chaque entrée dans report_json["entries"]:
       INSERT INTO fax_entries (
           id, report_id, fax_id, utilisateur, type,
           numero_original, numero_normalise, valide, pages,
           datetime, erreurs
       ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    
    4. Valider:
       conn.commit()
       conn.close()

def get_all_reports() -> list:
    """
    Récupère tous les rapports
    """
    1. Ouvrir la connexion
    2. SELECT * FROM reports ORDER BY created_at DESC
    3. Convertir en liste de dictionnaires
    4. Retourner

def get_report_by_id(report_id: str) -> dict:
    """
    Récupère un rapport complet avec ses entrées
    """
    1. Récupérer le rapport: SELECT * FROM reports WHERE id = ?
    2. Récupérer les entrées: SELECT * FROM fax_entries WHERE report_id = ?
    3. Retourner dict avec report + entries
```

---

## 3️⃣ STRUCTURE DES DONNÉES

### 3.1 Format d'import (CSV/XLSX)

**Exemple de données brutes**:
```
Fax ID;Nom et prénom utilisateur;Revendeur;Mode;Adresse de messagerie;Date et heure du fax;Numéro d'envoi;Numéro appelé;Appel international;Appel interne;Nombre de pages réel;Durée;Pages facturées;Type facturation
FAX001;Jean Dupont;TAKELEAD;SF;jean.dupont@takelead.fr;2024-12-10 14:30:00;0133445566;0622334455;Non;Oui;5;120;5;Standard
FAX002;Marie Martin;TAKELEAD;RF;marie.martin@takelead.fr;2024-12-10 15:45:00;0622334455;0133445566;Non;Oui;3;90;3;Standard
FAX003;Pierre Leblanc;TAKELEAD;SF;pierre.leblanc@takelead.fr;2024-12-10 16:20:00;0188776655;INVALIDE;Non;Non;0;0;0;Erreur
```

### 3.2 Structure des données analysées

**Après import et analyse**:
```json
{
  "entries": [
    {
      "id": "entry-uuid-1",
      "fax_id": "FAX001",
      "utilisateur": "Jean Dupont",
      "type": "send",
      "numero_original": "0622334455",
      "numero_normalise": "33622334455",
      "valide": true,
      "pages": 5,
      "datetime": "2024-12-10T14:30:00",
      "erreurs": []
    },
    {
      "id": "entry-uuid-2",
      "fax_id": "FAX002",
      "utilisateur": "Marie Martin",
      "type": "receive",
      "numero_original": "0133445566",
      "numero_normalise": "33133445566",
      "valide": true,
      "pages": 3,
      "datetime": "2024-12-10T15:45:00",
      "erreurs": []
    },
    {
      "id": "entry-uuid-3",
      "fax_id": "FAX003",
      "utilisateur": "Pierre Leblanc",
      "type": "send",
      "numero_original": "INVALIDE",
      "numero_normalise": "",
      "valide": false,
      "pages": 0,
      "datetime": "2024-12-10T16:20:00",
      "erreurs": ["Numéro vide", "Caractères invalides détectés"]
    }
  ],
  "statistics": {
    "total_fax": 3,
    "fax_envoyes": 2,
    "fax_recus": 1,
    "pages_totales": 8,
    "erreurs_totales": 1,
    "taux_reussite": 66.67,
    "erreurs_par_type": {
      "numero_vide": 0,
      "longueur_incorrecte": 0,
      "ne_commence_pas_33": 0,
      "caracteres_invalides": 1
    },
    "envois_par_utilisateur": {
      "Jean Dupont": 1,
      "Marie Martin": 1,
      "Pierre Leblanc": 1
    },
    "erreurs_par_utilisateur": {
      "Pierre Leblanc": 1
    }
  }
}
```

### 3.3 Structure du rapport final (JSON)

**Fichier `reports/{report_id}.json`**:
```json
{
  "report_id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
  "timestamp": "2024-12-10T17:00:00.123456",
  "contract_id": "CONTRACT_001",
  "date_debut": "2024-12-01",
  "date_fin": "2024-12-10",
  "statistics": {
    "total_fax": 150,
    "fax_envoyes": 95,
    "fax_recus": 55,
    "pages_totales": 412,
    "erreurs_totales": 12,
    "taux_reussite": 92.0,
    "erreurs_par_type": {
      "numero_vide": 2,
      "longueur_incorrecte": 5,
      "ne_commence_pas_33": 3,
      "caracteres_invalides": 2
    },
    "envois_par_utilisateur": {
      "Jean Dupont": 45,
      "Marie Martin": 38,
      "Pierre Leblanc": 67
    },
    "erreurs_par_utilisateur": {
      "Jean Dupont": 2,
      "Marie Martin": 4,
      "Pierre Leblanc": 6
    }
  },
  "entries": [
    {
      "id": "entry-uuid-1",
      "fax_id": "FAX001",
      "utilisateur": "Jean Dupont",
      "type": "send",
      "numero_original": "0622334455",
      "numero_normalise": "33622334455",
      "valide": true,
      "pages": 5,
      "datetime": "2024-12-10T14:30:00",
      "erreurs": []
    }
  ],
  "qr_code_url": "/reports_qr/a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6.png",
  "report_url": "/reports/a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6"
}
```

---

## 4️⃣ STRUCTURE DE LA BASE DE DONNÉES

### 4.1 Table `reports`

| Colonne | Type | Description |
|---------|------|-------------|
| id | TEXT (PRIMARY KEY) | UUID du rapport |
| date_rapport | TEXT | Date de création du rapport (ISO) |
| contract_id | TEXT | Identifiant du contrat |
| date_debut | TEXT | Début de la période analysée |
| date_fin | TEXT | Fin de la période analysée |
| fichier_source | TEXT | Chemin du fichier importé |
| total_fax | INTEGER | Nombre total de FAX |
| fax_envoyes | INTEGER | Nombre de FAX envoyés |
| fax_recus | INTEGER | Nombre de FAX reçus |
| pages_totales | INTEGER | Total de pages |
| erreurs_totales | INTEGER | Nombre d'erreurs |
| taux_reussite | REAL | Pourcentage de succès (0-100) |
| qr_path | TEXT | Chemin vers le QR code PNG |
| url_rapport | TEXT | URL du rapport sur l'interface web |
| created_at | TEXT | Timestamp de création |

### 4.2 Table `fax_entries`

| Colonne | Type | Description |
|---------|------|-------------|
| id | TEXT (PRIMARY KEY) | UUID de l'entrée |
| report_id | TEXT (FK) | Référence au rapport |
| fax_id | TEXT | ID du FAX dans l'export |
| utilisateur | TEXT | Nom de l'utilisateur |
| type | TEXT | "send" ou "receive" |
| numero_original | TEXT | Numéro brut du fichier |
| numero_normalise | TEXT | Numéro normalisé (33xxxxxxxxxx) |
| valide | BOOLEAN | Numéro valide ou non |
| pages | INTEGER | Nombre de pages |
| datetime | TEXT | Date/heure du FAX (ISO) |
| erreurs | TEXT | JSON array des erreurs |

### 4.3 Indexes

```sql
CREATE INDEX idx_reports_contract ON reports(contract_id);
CREATE INDEX idx_reports_created ON reports(created_at);
CREATE INDEX idx_fax_entries_report ON fax_entries(report_id);
CREATE INDEX idx_fax_entries_utilisateur ON fax_entries(utilisateur);
```

---

## 5️⃣ FLUX COMPLET D'EXÉCUTION

### Étape 1: Importation
```
Utilisateur choisit:
├─ Contrat: "CONTRACT_001"
├─ Date début: "2024-12-01"
├─ Date fin: "2024-12-10"
└─ Fichier: "export_faxcloud.csv"
    ↓
importer.py
├─ Vérifier le fichier
├─ Lire les colonnes
├─ Normaliser les données
└─ Retourner les lignes
```

### Étape 2: Analyse
```
analyzer.py
├─ Pour chaque ligne:
│  ├─ Normaliser le numéro
│  ├─ Valider le numéro
│  ├─ Détecter le type (send/receive)
│  └─ Ajouter aux statistiques
├─ Calculer les statistiques globales
└─ Retourner les résultats
```

### Étape 3: Rapport
```
reporter.py
├─ Générer l'UUID
├─ Créer le QR code (PNG)
├─ Formater le JSON
├─ Sauvegarder les fichiers
├─ Insérer en base de données
└─ Retourner les URLs
```

### Étape 4: Présentation
```
Interface Web
├─ Afficher la liste des rapports
├─ Permettre la consultation détaillée
├─ Afficher les QR codes
└─ Lecteur QR intégré
```

---

## 6️⃣ RÈGLES DE VALIDATION DES NUMÉROS

### Normalisation

**Entrée possible**:
- `0622334455` (format France)
- `+33622334455` (format international)
- `33 6 22 33 44 55` (espaces)
- `invalid` (invalide)

**Processus**:
```python
raw = "0622334455"
normalized = re.sub(r"\D", "", raw)      # "622334455" (supprime non-chiffres)
if normalized.startswith("0"):
    normalized = "33" + normalized[1:]   # "33622334455"
elif normalized.startswith("+33"):
    normalized = "33" + normalized[3:]   # "33622334455"
# Résultat: "33622334455"
```

### Validation

**Règles**:
1. **Longueur exacte**: 11 chiffres ✓
2. **Commence par 33**: ✓
3. **Aucun caractère invalide**: ✓

**Erreurs détectées**:
- Numéro vide
- Longueur incorrecte (< 11 ou > 11)
- Ne commence pas par 33
- Caractères non-numériques

---

## 7️⃣ ARCHITECTURE DES FICHIERS

```
/faxcloud-analyzer
│
├── main.py                           # Orchestrateur principal
├── importer.py                       # Lecture CSV/XLSX
├── analyzer.py                       # Moteur d'analyse
├── reporter.py                       # Génération rapports + QR
├── db.py                             # Gestion SQLite
├── config.py                         # Configuration globale
├── requirements.txt                  # Dépendances Python
│
├── /config
│   ├── __init__.py
│   └── settings.py                   # Paramètres de configuration
│
├── /src
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── contract_manager.py       # Gestion des contrats
│   │   ├── data_analyzer.py          # Analyse avancée
│   │   └── file_importer.py          # Import fichiers
│   │
│   ├── detectors/
│   │   ├── __init__.py
│   │   └── asterisk_detector.py      # (Futur) Détection Asterisk
│   │
│   └── reports/
│       ├── __init__.py
│       ├── report_generator.py       # Générateur rapports
│       └── qr_generator.py           # Générateur QR
│
├── /web
│   ├── index.html                    # Dashboard
│   ├── report.html                   # Détail d'un rapport
│   ├── style.css                     # Styles
│   └── script.js                     # Scripts JS
│
├── /data
│   ├── /imports                      # Fichiers importés
│   ├── /reports                      # Rapports JSON générés
│   └── /reports_qr                   # QR codes PNG
│
├── /database
│   └── faxcloud.db                   # Base SQLite
│
├── /exports                          # Dossier pour exports FaxCloud
│
└── DOCUMENTATION.md                  # Cette documentation
```

---

## 8️⃣ DÉPENDANCES PYTHON

```txt
python>=3.8
pandas==2.0.0              # Lecture CSV/XLSX
openpyxl==3.10.0           # Support XLSX
qrcode==7.4.2              # Génération QR codes
pillow==10.0.0             # Traitement images
requests==2.31.0           # Requêtes HTTP (futur Asterisk)
sqlite3                    # Intégré dans Python
```

---

## 9️⃣ PROCHAINES ÉTAPES

### Phase 2 (Futur)
- Intégration Asterisk pour validation FAX/VOIX
- API REST complète
- Authentification utilisateurs
- Historique et audit
- Notifications email

### Améliorations
- Support des bases multi-utilisateurs
- Export PDF des rapports
- Graphiques statistiques avancés
- Archivage des rapports

---

## 🔟 EXEMPLES D'UTILISATION

### Cas 1: Import et Analyse
```python
# main.py
from importer import import_faxcloud_export
from analyzer import analyze_data
from reporter import generate_report

# Importer
data = import_faxcloud_export("exports/faxcloud_2024_12.csv")

# Analyser
analysis = analyze_data(
    data["rows"],
    contract_id="CONTRACT_001",
    date_debut="2024-12-01",
    date_fin="2024-12-31"
)

# Rapporter
report = generate_report(analysis)
print(f"Rapport généré: {report['report_id']}")
print(f"QR Code: {report['qr_path']}")
```

### Cas 2: Consultation via Web
1. Utilisateur ouvre `http://localhost:8000`
2. Dashboard affiche la liste des rapports
3. Utilisateur clique sur un rapport
4. Affichage détaillé avec statistiques et QR code
5. Optionnel: Scanner le QR pour ouvrir via téléphone

---

**Document généré**: 2024-12-10
**Version**: 1.0
