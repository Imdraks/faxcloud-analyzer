# FaxCloud Analyzer v3.0 🎉

Une application professionnelle de gestion et d'analyse de rapports FAX avec interface moderne et API complète.

## 🚀 Caractéristiques

### Dashboard
- 📊 Vue d'ensemble des statistiques en temps réel
- 📈 Graphiques interactifs avec Chart.js
- 📋 Rapports récents
- 🎯 Taux de succès et métriques clés

### Gestion des Rapports
- 📥 Import de fichiers FAX
- 📝 Liste complète des rapports avec filtrage
- 🔍 Recherche et tri avancés
- 📊 Détails détaillés par rapport
- 📥 Export de données

### Admin Dashboard
- ⚙️ Métriques système
- 💾 Santé de la base de données
- 📊 Tendances d'utilisation
- 🔔 Alertes en temps réel

### API RESTful
- ✅ Endpoints CRUD complets
- 📡 Gestion des rapports et entrées
- 📊 Statistiques et tendances
- 🏥 Monitoring et health checks

## 🏗️ Architecture

```
FaxCloud Analyzer/
├── app/
│   ├── __init__.py              # Flask factory
│   ├── routes.py                # Tous les endpoints
│   ├── models/                  # Modèles SQLAlchemy
│   ├── utils/
│   │   └── data_service.py      # Service de données
│   ├── templates/               # Fichiers HTML
│   │   ├── dashboard.html       # Dashboard principal
│   │   ├── reports.html         # Liste des rapports
│   │   ├── report.html          # Détail d'un rapport
│   │   └── admin.html           # Dashboard admin
│   └── static/                  # Fichiers statiques
│       ├── css/
│       └── js/
├── config/
│   ├── __init__.py
│   └── settings.py              # Configuration centralisée
├── scripts/                     # Scripts utilitaires
├── docs/                        # Documentation
├── run.py                       # Point d'entrée
└── requirements.txt             # Dépendances
```

## 🛠️ Installation

### Prérequis
- Python 3.8+
- Pip
- Virtualenv (recommandé)

### Étapes

1. **Cloner le repo**
```bash
git clone <repo-url>
cd faxcloud-analyzer
```

2. **Créer l'environnement virtuel**
```bash
python -m venv .venv
.venv\Scripts\activate
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Lancer l'application**
```bash
python run.py
```

5. **Accéder à l'application**
- URL: http://127.0.0.1:5000
- Admin: http://127.0.0.1:5000/admin

## 📡 API Documentation

### Health & Stats
```
GET /api/health                 # État du serveur
GET /api/stats                  # Statistiques globales
GET /api/trends?days=7          # Tendances (7 derniers jours)
```

### Reports
```
GET    /api/reports                        # Tous les rapports
GET    /api/reports/<id>                   # Détail d'un rapport
POST   /api/reports                        # Créer un rapport
GET    /api/reports/<id>/entries           # Entrées d'un rapport
POST   /api/reports/<id>/entries           # Ajouter une entrée
GET    /api/reports/<id>/export            # Exporter un rapport
```

### Admin
```
GET /api/admin/health/detailed              # Santé détaillée
GET /api/admin/metrics                      # Métriques système
```

## 🎨 Design

- **Thème moderne**: Dégradés professionnels (Violet → Rose)
- **Responsive**: Adapté aux mobiles et tablettes
- **Accessible**: WCAG compliant
- **Performance**: Optimisé avec compression GZIP

## 📊 Modèles de Données

### Report
```python
{
    "id": 1,
    "name": "Rapport_20251217",
    "file_size": 125000,
    "entries": 500,
    "valid": 495,
    "errors": 5,
    "status": "completed",
    "created_at": "2025-12-17T16:00:00"
}
```

### FaxEntry
```python
{
    "id": 1,
    "report_id": 1,
    "fax_number": "+33123456789",
    "caller_id": "Caller_1",
    "recipient": "Recipient_1",
    "duration": 120,
    "page_count": 5,
    "status": "valid",
    "created_at": "2025-12-17T16:00:00"
}
```

## ⚙️ Configuration

### Fichier `.env`
```
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=mysql://user:password@localhost/faxcloud
```

### `config/settings.py`
Configuration centralisée pour:
- Base de données
- Logging
- Chemin des uploads
- Limites d'import
- Paramètres Flash

## 📈 Statistiques

L'application génère automatiquement:
- ✅ Total des rapports
- ✅ Total des entrées FAX
- ✅ Entrées valides
- ✅ Entrées en erreur
- ✅ Taux de succès (%)
- ✅ Tendances par jour

## 🔐 Sécurité

- ✅ CSRF Protection
- ✅ SQL Injection Prevention (SQLAlchemy ORM)
- ✅ Input Validation
- ✅ Compression GZIP
- ✅ Headers de sécurité

## 📝 Features à Venir

- [ ] Authentification & Autorisation
- [ ] Upload de fichiers CSV/XLSX
- [ ] Export PDF des rapports
- [ ] Webhooks pour notifications
- [ ] Cache Redis
- [ ] Tests automatisés
- [ ] Documentation Swagger
- [ ] Multi-langue

## 🐛 Troubleshooting

### Erreur de port occupé
```bash
# Changer le port
python run.py --port 5001
```

### Erreur de base de données
```bash
# Vérifier la connexion
python scripts/init_db.py
```

### Erreur CORS
Les CORS sont configurés pour les environnements de développement.

## 📞 Support

Pour toute question ou bug report:
- 📧 Email: support@faxcloud.com
- 🐙 GitHub Issues: [Créer une issue](https://github.com/...)
- 💬 Discord: [Rejoindre le serveur](https://discord.gg/...)

## 📄 License

MIT License - Voir [LICENSE](LICENSE) pour détails

## 👥 Contributeurs

- **Développeur Principal**: FaxCloud Team
- **Design**: Aurora Theme v1.0
- **QA**: Team QA

---

**Version**: 3.0.0  
**Dernière mise à jour**: 2025-12-17  
**Status**: ✅ Production Ready
