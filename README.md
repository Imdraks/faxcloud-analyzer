# 📊 FaxCloud Analyzer

**Analyseur intelligent pour fichiers d'export FAX FaxCloud**

> Version 3.0 | Python 3.8+ | Flask | MySQL

---

## 🚀 Démarrage Rapide

### Windows
```bash
start.bat
```

### Linux/Mac
```bash
./setup.sh
```

### Manuel
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
python run.py
```

**Accès :** http://127.0.0.1:5000

---

## 📌 Fonctionnalités

- ✅ Import CSV/XLSX automatique
- ✅ Normalisation des numéros de téléphone (tous formats → 33XXXXXXXXX)
- ✅ Validation avec règles strictes
- ✅ Statistiques détaillées (envois, réceptions, erreurs)
- ✅ Génération de rapports JSON avec QR codes
- ✅ API REST complète
- ✅ Interface web moderne
- ✅ Dashboard administrateur

---

## 🌐 URLs

| Page | URL |
|------|-----|
| Dashboard | http://127.0.0.1:5000 |
| Rapports | http://127.0.0.1:5000/reports |
| Admin | http://127.0.0.1:5000/admin |
| API Health | http://127.0.0.1:5000/api/health |

---

## 📁 Structure du Projet

```
faxcloud-analyzer/
├── run.py                 # Point d'entrée
├── start.bat              # Script Windows
├── setup.sh               # Script Linux/Mac
├── requirements.txt       # Dépendances
│
├── app/                   # Application Flask
│   ├── __init__.py        # Factory Flask
│   ├── routes.py          # Routes web + API
│   ├── templates/         # Pages HTML
│   ├── static/            # CSS, JS
│   └── utils/             # Services
│
├── config/                # Configuration
│   └── settings.py        # Variables centralisées
│
├── src/core/              # Logique métier
│   ├── analyzer.py        # Analyse des données
│   ├── importer.py        # Import CSV/XLSX
│   ├── reporter.py        # Génération rapports
│   ├── db_mysql.py        # Connexion MySQL
│   └── pdf_generator.py   # Export PDF
│
├── data/                  # Données
│   ├── imports/           # Fichiers importés
│   ├── reports/           # Rapports JSON
│   └── reports_qr/        # QR codes
│
├── docs/                  # Documentation
└── logs/                  # Fichiers logs
```

---

## 🔧 Configuration

Copier `.env.example` vers `.env` et configurer :

```env
# Base de données MySQL
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=faxcloud_analyzer

# Flask
FLASK_DEBUG=true
SECRET_KEY=your-secret-key
```

---

## 📊 API Endpoints

### Rapports
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/reports` | Liste des rapports |
| GET | `/api/reports/{id}` | Détail d'un rapport |
| POST | `/api/reports` | Créer un rapport |
| GET | `/api/reports/{id}/entries` | Entrées FAX d'un rapport |
| GET | `/api/reports/{id}/export` | Exporter un rapport |

### Statistiques
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/stats` | Statistiques globales |
| GET | `/api/trends` | Tendances sur N jours |
| GET | `/api/health` | État du serveur |

### Admin
| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/admin/metrics` | Métriques système |
| GET | `/api/admin/health/detailed` | Santé détaillée |

---

## 📥 Format des Fichiers CSV

Le fichier CSV doit contenir les colonnes suivantes :

| Colonne | Contenu | Exemple |
|---------|---------|---------|
| Fax ID | Identifiant unique | FAX12345 |
| Utilisateur | Nom | Jean Dupont |
| Mode | SF (envoyé) ou RF (reçu) | SF |
| Date/Heure | Timestamp | 2024-12-10 14:30 |
| Numéro appelé | Numéro destination | 0622334455 |
| Pages | Nombre de pages | 5 |

---

## ✅ Règles de Validation

### Normalisation des numéros
```
0145221134     → 33145221134
+33145221134   → 33145221134
0033145221134  → 33145221134
03.27.93.69.43 → 33327936943
```

### Critères de validité
- Longueur exacte : 11 chiffres
- Commence par : 33
- Caractères : chiffres uniquement

---

## 📈 Statistiques Générées

- **Total FAX** : envoyés + reçus
- **Pages** : par type (envoi/réception)
- **Taux de réussite** : (FAX valides / total) × 100
- **Erreurs par type** : numéro vide, longueur incorrecte, indicatif invalide

---

## 🛠️ Dépendances

```
flask>=3.0.0
pandas>=2.2.0
mysql-connector-python>=8.0.0
openpyxl>=3.1.0
qrcode>=7.4.0
pillow>=10.0.0
reportlab>=4.0.0
python-dotenv>=1.0.0
```

---

## 📝 Changelog

Voir [CHANGELOG.md](CHANGELOG.md) pour l'historique des versions.

---

## 📄 License

MIT License - Voir le fichier LICENSE pour plus de détails.
