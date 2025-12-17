# Architecture FaxCloud Analyzer v3.0

## Vue d'ensemble

```
┌─────────────┐
│   Frontend  │  Dashboard moderne + Admin
│  (HTML/CSS) │  Glassmorphism design
└──────┬──────┘
       │ HTTP/JSON
       ▼
┌─────────────────────────────────────┐
│      Flask Application (run.py)     │
├─────────────────────────────────────┤
│  Routes Web          │  Routes API   │
│  ├─ /               │  ├─ /api/health
│  ├─ /reports        │  ├─ /api/stats
│  ├─ /report/{id}    │  ├─ /api/upload
│  └─ /admin          │  ├─ /api/latest-reports
│                     │  └─ /api/report/{id}/*
└──────────┬──────────────┬───────────┘
           │              │
           ▼              ▼
    ┌─────────────────────────────┐
    │  App Package (app/)         │
    ├────────────────────────────┤
    │  - routes.py (Web + API)   │
    │  - api/ (v2, v3)           │
    │  - models/ (BD Models)     │
    │  - utils/ (Helper)         │
    │  - templates/ (HTML)       │
    │  - static/ (CSS, JS)       │
    └──────────┬──────────────────┘
               │
               ▼
    ┌──────────────────────┐
    │  Configuration       │
    ├──────────────────────┤
    │ config/settings.py   │
    │ .env                 │
    └──────────┬───────────┘
               │
               ▼
    ┌──────────────────────┐
    │   MySQL Database     │
    ├──────────────────────┤
    │ - reports table      │
    │ - fax_entries table  │
    │ - users table        │
    │ - audit logs         │
    └──────────────────────┘
```

---

## Modules Clés

### 1. **app/__init__.py** - Factory Flask
Crée l'instance Flask avec:
- Configuration chargée depuis `config/settings.py`
- Extensions (Compress)
- Routes enregistrées
- Error handlers

### 2. **app/routes.py** - Routes Centralisées
Gère toutes les routes:
- **bp_web**: Routes HTML (Dashboard, Reports, Admin)
- **bp_api**: Routes API v3 (health, upload, stats)

Structure:
```
GET  /                    → Dashboard principal
GET  /reports            → Liste des rapports
GET  /report/{id}        → Détail rapport
GET  /admin              → Admin dashboard

GET  /api/health         → Health check
GET  /api/stats          → Statistiques globales
POST /api/upload         → Importer fichier
GET  /api/latest-reports → Rapports récents
GET  /api/report/{id}    → Détail rapport (JSON)
```

### 3. **config/settings.py** - Configuration
Centralise toutes les variables:
- DB (host, port, user, pass, name)
- Flask (debug, secret key, upload folder)
- Logging (level, file path)
- Ngrok (optionnel)

Charge depuis `.env` avec defaults sûrs.

### 4. **run.py** - Point d'entrée
Démarre l'application:
```bash
python run.py  # Démarrage simple
```

### 5. **start.bat** - Script Windows
Automatise:
1. Création virtualenv si absent
2. Activation virtualenv
3. Installation dépendances
4. Initialisation BD
5. Démarrage Flask

---

## Flux de Requête

### Requête Web (Dashboard)
```
1. GET / 
   ↓ (app/routes.py @bp_web.route('/'))
2. return render_template('dashboard-v2.html')
   ↓ (Charge depuis app/templates/)
3. HTML chargé dans le navigateur
   ↓ (JavaScript)
4. Appel AJAX vers /api/stats
   ↓ (app/routes.py @bp_api.route('/stats'))
5. JSON retourné
   ↓ (JavaScript met à jour DOM)
6. Dashboard mis à jour
```

### Requête Upload
```
1. POST /api/upload (multipart/form-data)
   ↓ (app/routes.py @bp_api.route('/upload', methods=['POST']))
2. Lecture du fichier
3. Validation du format
4. Importation en BD
5. Création rapport
6. JSON retourné: {success, report_id}
   ↓ (JavaScript redirige vers /report/{id})
7. Rapport affiché
```

---

## Structure des Données

### Table: reports
```
id (PRIMARY KEY)
name (VARCHAR)
file_size (INT)
entries (INT)
valid (INT)
errors (INT)
created_at (DATETIME)
updated_at (DATETIME)
```

### Table: fax_entries
```
id (PRIMARY KEY)
report_id (FOREIGN KEY)
fax_number (VARCHAR)
caller_id (VARCHAR)
recipient (VARCHAR)
duration (INT)
status (ENUM: valid, error)
error_message (TEXT)
created_at (DATETIME)
```

---

## Cycle de Vie de l'Application

### Démarrage
```
start.bat
  ├─ Créer virtualenv si absent
  ├─ Activer virtualenv
  ├─ pip install -r requirements.txt
  ├─ python scripts/init_db.py
  └─ python run.py
       └─ app/__init__.py:create_app()
            ├─ Charger config
            ├─ Initialiser extensions
            ├─ Enregistrer blueprints
            └─ Prêt pour requêtes
```

### Arrêt
```
Ctrl+C
  ├─ Flask arrêt gracieux
  ├─ Fermeture connexions BD
  └─ Sauvegarde logs
```

---

## Dépendances Inter-modules

```
run.py
  └── app/__init__.py (create_app)
       ├── config/settings.py (import config)
       └── app/routes.py (register blueprints)
            ├── templates/*.html (render_template)
            └── static/* (CSS, JS)
```

---

## Points d'Extension

### Ajouter une nouvelle route
**Fichier:** `app/routes.py`
```python
@bp_api.route('/nouveau', methods=['GET'])
def nouveau():
    return jsonify({...}), 200
```

### Ajouter une nouvelle page
**Fichier:** `app/routes.py`
```python
@bp_web.route('/nouvelle-page')
def nouvelle_page():
    return render_template('nouvelle-page.html')
```

**Fichier:** `app/templates/nouvelle-page.html`
```html
<!-- HTML de la page -->
```

### Ajouter un modèle BD
**Fichier:** `app/models/__init__.py`
```python
class MonModele:
    # Définir le modèle
```

---

## Performance

### Optimisations Actives
- ✅ GZIP compression (Flask-Compress)
- ✅ Static file caching
- ✅ JSON response optimization
- ✅ Database indexes

### Monitoring
- Logs centralisés: `logs/app.log`
- Endpoints stats: `/api/stats`
- Health check: `/api/health`

---

## Sécurité

### Configurable
- SECRET_KEY pour sessions
- CORS headers (à ajouter)
- Rate limiting (à implémenter)
- Input validation (à étendre)

### En Production
- Utiliser HTTPS
- SECRET_KEY complexe
- DB credentials en `.env` sécurisé
- Activer rate limiting
- Valider tous les uploads

---

## Maintenance

### Logs
```
logs/app.log  ← Tous les logs
```

### Déboggage
```bash
set FLASK_DEBUG=1
python run.py  # Mode debug avec reloader
```

### Mise à jour
```bash
pip install --upgrade -r requirements.txt
```

---

**Dernière mise à jour:** Décembre 2025  
**Version:** 3.0  
**Status:** ✅ Production Ready
