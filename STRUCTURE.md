# Structure Propre - Index des Ressources

## 📂 Répertoires Principaux

### `/app` - Application principale
- **__init__.py** - Factory Flask, création de l'app
- **routes.py** - Toutes les routes Web et API
- **api/** - Endpoints API (v2, v3) - À développer
- **models/** - Modèles SQLAlchemy - À développer
- **utils/** - Fonctions utilitaires - À développer
- **templates/** - Fichiers HTML
  - dashboard-v2.html ✅ Moderne
  - reports-v2.html ✅ Moderne
  - report-v2.html ✅ Moderne
  - admin.html ✅ Moderne
  - 404.html / 500.html ✅
- **static/** - CSS et JavaScript
  - css/style.css
  - js/app.js

### `/config` - Configuration
- **settings.py** - Variables centralisées
  - DB config
  - Flask config
  - Logging config
  - Upload config

### `/scripts` - Scripts utilitaires
- **init_db.py** - Initialisation BD
- **cli.py** - Commandes CLI

### `/tests` - Tests unitaires
- À développer

### `/docs` - Documentation
- **ARCHITECTURE.md** ✅ Vue d'ensemble
- **INSTALLATION.md** - À créer
- **API.md** - À créer

### `/data` - Données
- **uploads/** - Fichiers uploadés
- **database/** - DB locale (optional)

### `/logs` - Fichiers logs
- **app.log** - Logs application

---

## 📝 Fichiers Racine

### À Garder
- **run.py** ✅ Point d'entrée principal
- **start.bat** ✅ Script démarrage Windows
- **requirements.txt** ✅ Dépendances
- **.env.example** ✅ Configuration exemple
- **.env** - Configuration locale (gitignored)
- **README_CLEAN.md** ✅ Documentation propre
- **.gitignore** ✅
- **.git/** ✅

### À Nettoyer / À Archiver
- benchmark.py → archives/
- check_db.py → archives/
- cli.py → scripts/
- test_upload.py → tests/
- test_v2_architecture.py → tests/
- test_v3_features.py → tests/
- verify_api.py → tests/
- main.py → archives/
- init_mysql.py → scripts/
- install.bat → archives/
- ARCHITECTURE_V2.md → archives/
- BACKEND_TECHNICAL_GUIDE.md → archives/
- DEPLOYMENT_SUMMARY.md → archives/
- FEATURES_V3.md → archives/
- PATCH_V3_SUMMARY.md → archives/
- SPEED_OPTIMIZATIONS.md → archives/
- optimize_mysql.sql → scripts/
- server.log → logs/
- test_v2_architecture.py → tests/

---

## 🎯 État Actuel

### ✅ Complété
- Structure dossiers propre
- Config centralisée
- Routes organisées
- Templates modernes
- Documentation

### ⏳ À Faire
- [ ] Développer /app/api/ (API v3 complète)
- [ ] Développer /app/models/ (ORM SQLAlchemy)
- [ ] Développer /app/utils/ (Helpers)
- [ ] Ajouter tests unitaires
- [ ] Intégrer BD MySQL
- [ ] Implémenter upload/import
- [ ] Ajouter authentification
- [ ] Déployer en production

---

## 🚀 Commandes Clés

```bash
# Démarrage
start.bat              # Windows
python run.py          # Cross-platform

# Configuration
copy .env.example .env  # Créer .env

# Dépendances
pip install -r requirements.txt

# Tests
pytest tests/

# Logs
tail -f logs/app.log   # Linux/Mac
```

---

## 📊 Hiérarchie Imports

```python
# Pour développer une nouvelle feature:

# 1. Importer depuis config
from config.settings import DB_HOST, UPLOAD_FOLDER

# 2. Importer depuis app
from app import create_app
from app.routes import bp_api

# 3. Point d'entrée
python run.py
```

---

## 🔄 Workflow Développement

### Ajouter une route
1. Éditer `app/routes.py`
2. Ajouter fonction décorée
3. Tester sur http://127.0.0.1:5000

### Ajouter une page
1. Créer `app/templates/ma-page.html`
2. Ajouter route `@bp_web.route()`
3. Tester

### Ajouter une API
1. Ajouter route `@bp_api.route()`
2. Retourner `jsonify({})`
3. Tester avec curl/Postman

---

**Créé:** Décembre 2025  
**Version:** 3.0 Clean  
**Status:** ✅ Prêt au développement
