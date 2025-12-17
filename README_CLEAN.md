# 📊 FaxCloud Analyzer v3.0

Plateforme d'analyse FAX avancée avec interface moderne et API REST complète.

---

## 🚀 Démarrage Rapide

### Windows (Recommandé)
```bash
start.bat
```

### Linux/Mac
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

**Accès:**
- 🌐 Dashboard: http://127.0.0.1:5000
- 📊 Admin: http://127.0.0.1:5000/admin
- 🔌 API Health: http://127.0.0.1:5000/api/health

---

## 📁 Structure du Projet

```
faxcloud-analyzer/
├── app/                          # Application principale
│   ├── __init__.py              # Factory Flask
│   ├── routes.py                # Toutes les routes (web + api)
│   ├── api/                     # Endpoints API (v2, v3)
│   ├── models/                  # Modèles BD
│   ├── utils/                   # Utilitaires partagés
│   ├── templates/               # Pages HTML
│   └── static/                  # CSS, JS
│
├── config/                       # Configuration
│   └── settings.py              # Variables centralisées
│
├── scripts/                      # Scripts utilitaires
│   ├── init_db.py              # Initialisation BD
│   └── cli.py                  # Commandes CLI
│
├── tests/                        # Tests unitaires
│
├── docs/                         # Documentation
│   ├── INSTALLATION.md
│   ├── API.md
│   └── ARCHITECTURE.md
│
├── data/                         # Données (uploads, db)
│   └── uploads/
│
├── logs/                         # Fichiers logs
│
├── run.py                        # Point d'entrée principal
├── start.bat                     # Script de démarrage Windows
├── requirements.txt              # Dépendances Python
└── .env.example                  # Configuration exemple

```

---

## ⚙️ Configuration

Copier `.env.example` en `.env` et adapter:

```env
# Environnement
FLASK_ENV=development
FLASK_DEBUG=true

# Base de données MySQL
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=faxcloud_db

# Sécurité
SECRET_KEY=your-secret-key-here

# Ngrok (optionnel)
NGROK_ENABLED=false
NGROK_AUTHTOKEN=
```

---

## 📚 API v3

### Routes Principales

**Health Check**
```
GET /api/health
```

**Statistiques**
```
GET /api/stats
```

**Upload de fichier**
```
POST /api/upload
Content-Type: multipart/form-data
- file: [CSV ou XLSX]
```

**Rapports**
```
GET /api/latest-reports?limit=10
GET /api/report/{id}
GET /api/report/{id}/entries
GET /api/report/{id}/export
```

---

## 🎨 Frontend

### Pages Disponibles

| Page | URL | Description |
|------|-----|-------------|
| Dashboard | `/` | Accueil principal |
| Rapports | `/reports` | Liste des rapports |
| Rapport | `/report/{id}` | Détail d'un rapport |
| Admin | `/admin` | Dashboard administrateur |

### Design
- 🎨 Design moderne avec glassmorphism
- 📱 Responsive sur mobile
- ⚡ Animations fluides
- 🌙 Support dark mode

---

## 🔧 Développement

### Ajouter une nouvelle route

**1. Dans `app/routes.py`:**
```python
@bp_api.route('/ma-route', methods=['GET'])
def ma_route():
    return jsonify({'data': 'exemple'}), 200
```

### Ajouter une nouvelle page

**1. Créer `app/templates/ma-page.html`**

**2. Ajouter route dans `app/routes.py`:**
```python
@bp_web.route('/ma-page')
def ma_page():
    return render_template('ma-page.html')
```

### Ajouter CSS/JS

Placer dans `app/static/`:
- CSS: `app/static/css/mon-style.css`
- JS: `app/static/js/mon-script.js`

---

## 📊 Commandes Utiles

```bash
# Démarrage normal
python run.py

# Avec debug activé
set FLASK_DEBUG=1
python run.py

# Initialiser BD
python scripts/init_db.py

# Tests
pytest tests/
```

---

## 🐛 Troubleshooting

### Le serveur ne démarre pas
```
1. Vérifier virtualenv: .venv existe
2. Vérifier requirements: pip install -r requirements.txt
3. Vérifier logs: logs/app.log
```

### Erreur MySQL
```
1. Vérifier configuration .env
2. S'assurer MySQL est en cours d'exécution
3. Vérifier credentials DB
```

### Port 5000 déjà utilisé
```
set FLASK_PORT=5001
python run.py
```

---

## 📝 Documentation

Voir le dossier `docs/` pour:
- [Installation complète](docs/INSTALLATION.md)
- [Documentation API](docs/API.md)
- [Architecture système](docs/ARCHITECTURE.md)

---

## 📦 Dépendances Principales

- **Flask 3.1.2** - Framework web
- **MySQL** - Base de données
- **Chart.js** - Visualisations
- **PyMySQL** - Driver MySQL
- **python-dotenv** - Configuration

---

## 🔒 Sécurité

- ✅ HTTPS recommandé en production
- ✅ Variables sensibles dans `.env` (pas en repo)
- ✅ Validation des uploads
- ✅ Protection CORS configurée
- ✅ Rate limiting (à configurer)

---

## 📊 Performance

- ⚡ GZIP compression active
- 🚀 Optimisations BD (indexes)
- 🔄 Cache optimisé
- 📈 Monitoring intégré

---

## 👤 Support

Pour les problèmes:
1. Vérifier les logs: `logs/app.log`
2. Consulter la documentation: `docs/`
3. Vérifier les issues GitHub

---

## 📄 Licence

Copyright © 2025 FaxCloud Analyzer

---

**Status:** ✅ Opérationnel  
**Version:** 3.0  
**Dernière mise à jour:** Décembre 2025
