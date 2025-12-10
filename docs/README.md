# 📊 FaxCloud Analyzer - Guide d'utilisation

## 🚀 Démarrage rapide

### Installation

```bash
# 1. Créer un répertoire du projet
mkdir faxcloud-analyzer
cd faxcloud-analyzer

# 2. Cloner ou copier les fichiers

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Initialiser la base de données
python main.py init
```

### Première utilisation

```bash
# Analyser un fichier d'export FaxCloud
python main.py import \
    --file exports/sample_export_2024_12.csv \
    --contract CONTRACT_001 \
    --start 2024-12-01 \
    --end 2024-12-31
```

---

## 📁 Structure du projet

```
faxcloud-analyzer/
├── main.py                    # Point d'entrée
├── config.py                  # Configuration globale
├── db.py                      # Gestion base de données
├── importer.py                # Import CSV/XLSX
├── analyzer.py                # Analyse des données
├── reporter.py                # Génération rapports
├── requirements.txt           # Dépendances Python
│
├── data/
│   ├── imports/              # Fichiers importés
│   ├── reports/              # Rapports JSON
│   └── reports_qr/           # QR codes PNG
│
├── database/
│   └── faxcloud.db          # Base SQLite
│
├── exports/                  # Exports FaxCloud sources
│   └── sample_export_2024_12.csv
│
├── web/                      # Interface web (futur)
│   ├── index.html
│   ├── report.html
│   ├── style.css
│   └── script.js
│
└── logs/
    └── analyzer.log         # Fichier de logs
```

---

## 📖 Commandes disponibles

### 1. Initialiser le projet

Crée la base de données et tous les répertoires nécessaires.

```bash
python main.py init
```

**Output**:
```
🔧 Initialisation du projet...
✓ Répertoire imports: .../data/imports
✓ Répertoire reports_json: .../data/reports
✓ Répertoire reports_qr: .../data/reports_qr
✓ Répertoire exports: .../exports
✓ Répertoire database: .../database
✓ Répertoire logs: .../logs
✓ Base de données initialisée: .../database/faxcloud.db
✅ Projet initialisé avec succès
```

---

### 2. Importer et analyser un fichier

Traite un export FaxCloud complet (import → analyse → rapport).

```bash
python main.py import \
    --file path/to/export.csv \
    --contract CONTRACT_001 \
    --start 2024-12-01 \
    --end 2024-12-31
```

**Paramètres**:
- `--file`: Chemin du fichier CSV ou XLSX (**requis**)
- `--contract`: ID du contrat (défaut: CONTRACT_001)
- `--start`: Date de début (défaut: 2024-01-01)
- `--end`: Date de fin (défaut: 2024-12-31)

**Output complet**:
```
======================================================================
TRAITEMENT EXPORT: CONTRACT_001 (2024-12-01 à 2024-12-31)
======================================================================

📥 ÉTAPE 1: IMPORTATION
----------------------------------------------------------------------
✓ Importation réussie: 20 lignes

📊 ÉTAPE 2: ANALYSE
----------------------------------------------------------------------
✓ Analyse complète:
  • Total FAX: 20
  • Envoyés: 12, Reçus: 8
  • Pages: 97
  • Erreurs: 3 (15.00%)
  • Taux réussite: 85.00%

📝 ÉTAPE 3: RAPPORT ET QR CODE
----------------------------------------------------------------------
✓ Rapport généré avec succès: a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6
  • ID: a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6
  • URL: /reports/a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6
  • QR Code: reports_qr/a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6.png

📋 RÉSUMÉ
----------------------------------------------------------------------
╔════════════════════════════════════════════════════════════════╗
║                   RAPPORT FaxCloud                            ║
╚════════════════════════════════════════════════════════════════╝

ID Rapport:           a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6
Contrat:              CONTRACT_001
Période:              2024-12-01 à 2024-12-31
Généré:               2024-12-10T17:00:00

─────────────────────────────────────────────────────────────────

STATISTIQUES GLOBALES

Total FAX:            20
  ├─ Envoyés:        12
  └─ Reçus:          8

Pages totales:        97

Erreurs:              3
Taux de réussite:     85.00%

─────────────────────────────────────────────────────────────────

ERREURS PAR TYPE

Numéros vides:        1
Longueur incorrecte:  1
Ne commence pas 33:   0
Caractères invalides: 1

─────────────────────────────────────────────────────────────────

UTILISATEURS

Total utilisateurs:   4

Envois par utilisateur:
  • Jean Dupont: 5 FAX (100.0% réussite)
  • Marie Martin: 5 FAX (80.0% réussite)
  • Pierre Leblanc: 5 FAX (80.0% réussite)
  • Sophie Dupuis: 5 FAX (80.0% réussite)

═══════════════════════════════════════════════════════════════

======================================================================
✅ TRAITEMENT RÉUSSI
======================================================================

✅ Rapport généré: a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6
```

---

### 3. Lister tous les rapports

Affiche la liste de tous les rapports générés.

```bash
python main.py list
```

**Output**:
```
📋 Liste des rapports
----------------------------------------------------------------------
Total: 3 rapport(s)

1. a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6
   Contrat: CONTRACT_001
   Généré: 2024-12-10T17:00:00
   FAX: 20 (Erreurs: 3, Réussite: 85.0%)

2. b2c3d4e5-f6g7-h8i9-j0k1-l2m3n4o5p6a1
   Contrat: CONTRACT_002
   Généré: 2024-12-09T16:30:00
   FAX: 150 (Erreurs: 12, Réussite: 92.0%)

3. c3d4e5f6-g7h8-i9j0-k1l2-m3n4o5p6a1b2
   Contrat: CONTRACT_001
   Généré: 2024-12-08T15:00:00
   FAX: 85 (Erreurs: 5, Réussite: 94.1%)
```

---

### 4. Consulter un rapport détaillé

Affiche les détails complets d'un rapport avec les erreurs.

```bash
python main.py view --report-id a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6
```

**Output**:
```
📖 Affichage rapport: a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6
----------------------------------------------------------------------

[Affiche le résumé complet + les erreurs détaillées]

⚠️  ENTRÉES AVEC ERREURS:

  • FAX003 (Pierre Leblanc)
    Numéro: INVALID
    Erreurs: Caractères invalides détectés

  • FAX012 (Jean Dupont)
    Numéro: SHORT
    Erreurs: Longueur incorrecte: 5 au lieu de 11

  • FAX017 (Marie Martin)
    Numéro: 
    Erreurs: Numéro vide
```

---

## 📊 Fichiers générés

### 1. Rapport JSON

**Localisation**: `data/reports/{report_id}.json`

**Exemple**:
```json
{
  "report_id": "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
  "timestamp": "2024-12-10T17:00:00.123456",
  "contract_id": "CONTRACT_001",
  "date_debut": "2024-12-01",
  "date_fin": "2024-12-31",
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
      "Marie Martin": 5,
      "Pierre Leblanc": 5,
      "Sophie Dupuis": 5
    },
    "erreurs_par_utilisateur": {
      "Jean Dupont": 0,
      "Marie Martin": 1,
      "Pierre Leblanc": 1,
      "Sophie Dupuis": 1
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

### 2. QR Code PNG

**Localisation**: `data/reports_qr/{report_id}.png`

**Contenu encodé**: URL du rapport
```
http://localhost:8000/reports/a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6
```

### 3. Base de données SQLite

**Localisation**: `database/faxcloud.db`

**Tables**:
- `reports`: Rapports principaux
- `fax_entries`: Entrées FAX détaillées

---

## 🔍 Règles de validation des numéros

### Normalisation

| Entrée | Résultat |
|--------|----------|
| `0622334455` | `33622334455` ✓ |
| `+33622334455` | `33622334455` ✓ |
| `33 6 22 33 44 55` | `33622334455` ✓ |
| `33622334455` | `33622334455` ✓ |
| `INVALID` | `` ✗ |
| `` | `` ✗ |

### Validation

**Règles**:
1. Doit contenir exactement 11 chiffres
2. Doit commencer par 33 (code France)
3. Doit contenir uniquement des chiffres

**Erreurs détectées**:
- ✗ Numéro vide
- ✗ Longueur incorrecte
- ✗ Ne commence pas par 33
- ✗ Caractères invalides

---

## 📊 Format CSV/XLSX attendu

### Colonnes requises

| Index | Nom | Exemple | Type |
|-------|-----|---------|------|
| A | Fax ID | FAX001 | str |
| B | Utilisateur | Jean Dupont | str |
| C | Revendeur | TAKELEAD | str |
| D | Mode | SF/RF | str |
| E | Email | jean@example.com | str |
| F | Date/Heure | 2024-12-10 14:30:00 | datetime |
| G | Numéro envoi | 0133445566 | str |
| H | Numéro appelé | 0622334455 | str |
| I | Appel intl | Non/Oui | str |
| J | Appel interne | Oui/Non | str |
| K | Pages | 5 | int |
| L | Durée (sec) | 120 | int |
| M | Pages facturées | 5 | int |
| N | Type facturation | Standard | str |

### Exemple de fichier

Voir `exports/sample_export_2024_12.csv`

---

## 🐛 Dépannage

### Problème: "qrcode not found"

**Solution**: Installer les dépendances
```bash
pip install -r requirements.txt
```

### Problème: "Fichier non trouvé"

**Solution**: Vérifier le chemin du fichier
```bash
# Afficher les fichiers disponibles
dir exports\
```

### Problème: Base de données verrouillée

**Solution**: Supprimer et réinitialiser
```bash
del database\faxcloud.db
python main.py init
```

---

## 🚀 Utilisation programmée

```python
from main import process_export

# Traiter un export
result = process_export(
    file_path="exports/sample.csv",
    contract_id="CONTRACT_001",
    date_debut="2024-12-01",
    date_fin="2024-12-31"
)

if result["success"]:
    print(f"Rapport: {result['report_id']}")
    print(f"QR Code: {result['qr_path']}")
else:
    print(f"Erreur: {result['message']}")
```

---

## 📝 Fichiers de logs

Tous les événements sont enregistrés dans `logs/analyzer.log`:

```
[2024-12-10 17:00:00] INFO - __main__ - TRAITEMENT EXPORT: CONTRACT_001
[2024-12-10 17:00:01] INFO - importer - Lecture du fichier: exports/sample.csv
[2024-12-10 17:00:02] INFO - analyzer - Début analyse: 20 lignes
[2024-12-10 17:00:02] INFO - analyzer - ✓ Analyse complète: 20 FAX, 3 erreurs, 85.00% réussite
[2024-12-10 17:00:03] INFO - reporter - Génération rapport: a1b2c3d4-e5f6-...
```

---

## 🔮 Prochaines étapes

- [ ] Interface web interactive (HTML/CSS/JS)
- [ ] API REST Flask/FastAPI
- [ ] Intégration Asterisk
- [ ] Export PDF des rapports
- [ ] Graphiques statistiques
- [ ] Authentification utilisateurs
- [ ] Notifications email

---

## 📞 Support

Pour toute question ou bug: contact@takelead.fr

**Version**: 1.0.0
**Dernière mise à jour**: 2024-12-10
