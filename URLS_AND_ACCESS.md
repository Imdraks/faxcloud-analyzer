# 🔗 URLs & Accès - FaxCloud Analyzer v3.0

## 🌐 Accès Local (Développement)

### Pages Web
| Page | URL | Description |
|------|-----|-------------|
| 🏠 Dashboard | http://127.0.0.1:5000 | Accueil avec statistiques |
| 📋 Rapports | http://127.0.0.1:5000/reports | Liste de tous les rapports |
| 📊 Rapport #1 | http://127.0.0.1:5000/report/1 | Détail du rapport 1 |
| ⚙️ Admin | http://127.0.0.1:5000/admin | Dashboard administrateur |

### API Health
| Endpoint | URL | Méthode |
|----------|-----|---------|
| Health Check | http://127.0.0.1:5000/api/health | GET |
| Stats | http://127.0.0.1:5000/api/stats | GET |
| Trends | http://127.0.0.1:5000/api/trends | GET |

### API Reports
| Endpoint | URL | Méthode |
|----------|-----|---------|
| List Reports | http://127.0.0.1:5000/api/reports | GET |
| Get Report #1 | http://127.0.0.1:5000/api/reports/1 | GET |
| Create Report | http://127.0.0.1:5000/api/reports | POST |
| Get Entries #1 | http://127.0.0.1:5000/api/reports/1/entries | GET |
| Export Report #1 | http://127.0.0.1:5000/api/reports/1/export | GET |

### API Admin
| Endpoint | URL | Méthode |
|----------|-----|---------|
| Health Detailed | http://127.0.0.1:5000/api/admin/health/detailed | GET |
| Metrics | http://127.0.0.1:5000/api/admin/metrics | GET |

---

## 📚 Documentation Locale

### Files Documentation
| Document | Chemin | Contenu |
|----------|--------|---------|
| README | `/README_PRO.md` | Vue d'ensemble projet |
| Summary | `/PROJECT_SUMMARY.md` | Résumé des réalisations |
| Checklist | `/CHECKLIST.md` | Checklist complète |
| Changelog | `/CHANGELOG.md` | Historique des versions |

### Developer Docs
| Document | Chemin | Contenu |
|----------|--------|---------|
| API Guide | `/docs/API_GUIDE.md` | Documentation API complète |
| Development | `/docs/DEVELOPMENT.md` | Guide développement |
| Architecture | `/docs/ARCHITECTURE.md` | Architecture technique |
| Deployment | `/docs/DEPLOYMENT.md` | Guide déploiement production |

---

## 🚀 Démarrage Rapide

### Windows
```bash
cd c:\Users\VOXCL\Documents\GitHub\faxcloud-analyzer
setup.bat
```

### Linux/macOS
```bash
cd ~/faxcloud-analyzer
chmod +x setup.sh
./setup.sh
```

### Manuel
```bash
python -m venv .venv
source .venv/bin/activate  # .venv\Scripts\activate on Windows
pip install -r requirements.txt
python run.py
```

**Puis accéder à**: http://127.0.0.1:5000

---

## 🔨 Commandes Utiles

### Gestion du Serveur
```bash
# Démarrer
python run.py

# Arrêter
Ctrl+C

# Mode production
gunicorn wsgi:app --workers 4
```

### Gestion de l'Environnement
```bash
# Créer virtual env
python -m venv .venv

# Activer (Windows)
.venv\Scripts\activate

# Activer (Linux/macOS)
source .venv/bin/activate

# Installer dépendances
pip install -r requirements.txt

# Ajouter une dépendance
pip install package-name
pip freeze > requirements.txt
```

### Testing API
```bash
# Test Health
curl http://127.0.0.1:5000/api/health

# Get Stats
curl http://127.0.0.1:5000/api/stats

# Get Reports
curl http://127.0.0.1:5000/api/reports

# Create Report
curl -X POST http://127.0.0.1:5000/api/reports \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Report"}'
```

---

## 📊 Structure des URLs

### Web Routes
```
/                    → dashboard.html (Dashboard principal)
/reports             → reports.html (Liste des rapports)
/report/<id>         → report.html (Détail d'un rapport)
/admin               → admin.html (Admin dashboard)
```

### API Routes
```
/api/
  ├── health                          (GET)
  ├── stats                           (GET)
  ├── trends                          (GET)
  ├── reports                         (GET, POST)
  ├── reports/<id>                    (GET)
  ├── reports/<id>/entries            (GET, POST)
  ├── reports/<id>/export             (GET)
  └── admin/
      ├── health/detailed             (GET)
      └── metrics                     (GET)
```

---

## 🧪 Test Endpoints avec cURL

### 1. Health Check
```bash
curl -X GET "http://127.0.0.1:5000/api/health" \
  -H "Accept: application/json"

# Response:
# {
#   "status": "online",
#   "version": "3.0",
#   "service": "FaxCloud Analyzer"
# }
```

### 2. Get All Reports
```bash
curl -X GET "http://127.0.0.1:5000/api/reports?limit=10" \
  -H "Accept: application/json"
```

### 3. Get Report Details
```bash
curl -X GET "http://127.0.0.1:5000/api/reports/1" \
  -H "Accept: application/json"
```

### 4. Get Stats
```bash
curl -X GET "http://127.0.0.1:5000/api/stats" \
  -H "Accept: application/json"

# Response:
# {
#   "total_reports": 5,
#   "total_entries": 2500,
#   "valid_entries": 2450,
#   "error_entries": 50,
#   "success_rate": 98.0
# }
```

### 5. Get Trends
```bash
curl -X GET "http://127.0.0.1:5000/api/trends?days=7" \
  -H "Accept: application/json"
```

### 6. Create Report
```bash
curl -X POST "http://127.0.0.1:5000/api/reports" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Nouveau Rapport",
    "file_size": 100000
  }'
```

### 7. Add Entry to Report
```bash
curl -X POST "http://127.0.0.1:5000/api/reports/1/entries" \
  -H "Content-Type: application/json" \
  -d '{
    "fax_number": "+33123456789",
    "caller_id": "Caller_1",
    "recipient": "Recipient_1",
    "duration": 120,
    "page_count": 5,
    "status": "valid"
  }'
```

### 8. Export Report
```bash
curl -X GET "http://127.0.0.1:5000/api/reports/1/export" \
  -H "Accept: application/json" \
  > report_export.json
```

### 9. Admin Health
```bash
curl -X GET "http://127.0.0.1:5000/api/admin/health/detailed" \
  -H "Accept: application/json"

# Response:
# {
#   "status": "healthy",
#   "database": {
#     "reports": 5,
#     "entries": 2500
#   },
#   "uptime": 3600
# }
```

### 10. Admin Metrics
```bash
curl -X GET "http://127.0.0.1:5000/api/admin/metrics" \
  -H "Accept: application/json"

# Response:
# {
#   "cpu_usage": 35,
#   "memory_usage": 42,
#   "disk_usage": 28,
#   "database_size": 2048,
#   "reports_today": 5,
#   "entries_today": 1250,
#   "avg_processing_time": 12.5,
#   "error_rate": 2.0,
#   "success_rate": 98.0
# }
```

---

## 📱 Tester avec JavaScript

### Fetch Stats
```javascript
fetch('/api/stats')
    .then(res => res.json())
    .then(data => console.log(data));
```

### Create Report
```javascript
fetch('/api/reports', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name: 'Test' })
})
.then(res => res.json())
.then(data => console.log(data));
```

### Get Report Details
```javascript
fetch('/api/reports/1')
    .then(res => res.json())
    .then(data => console.log(data));
```

---

## 🔗 External Resources

### Documentation
- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Docs](https://www.sqlalchemy.org/)
- [Chart.js](https://www.chartjs.org/)
- [MDN Web Docs](https://developer.mozilla.org/)

### Tools
- [Postman](https://www.postman.com/) - API Testing
- [Thunder Client](https://www.thunderclient.com/) - VS Code Extension
- [Insomnia](https://insomnia.rest/) - API Client

---

## 🐛 Troubleshooting URLs

### Si la page ne charge pas
```
✓ Vérifier que le serveur tourne
✓ Vérifier l'URL exacte
✓ Vérifier la console browser (F12)
✓ Vérifier les logs serveur
```

### Si une API retourne 404
```
✓ Vérifier que l'endpoint existe
✓ Vérifier la méthode HTTP (GET, POST)
✓ Vérifier l'ID du paramètre
✓ Consulter docs/API_GUIDE.md
```

### Si CORS error
```
✓ Les CORS sont configurés pour dev
✓ Consulter app/__init__.py
✓ Ajouter CORS si nécessaire
```

---

## 📞 Support

### Documentation
- 📖 Lire `README_PRO.md`
- 📖 Consulter `docs/API_GUIDE.md`
- 📖 Vérifier `docs/DEVELOPMENT.md`

### Server Issues
1. Vérifier les logs serveur
2. Redémarrer le serveur
3. Vérifier la configuration
4. Consulter `TROUBLESHOOTING.md`

---

**Dernière mise à jour**: 17 Décembre 2025  
**Version**: 3.0.0  
**Status**: ✅ Production Ready
