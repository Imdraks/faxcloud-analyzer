# 🚀 FaxCloud v3.0 - FEATURES AVANCÉES

## 📋 Table des matières

1. [API v3 Avancée](#api-v3-avancée)
2. [Export Avancé](#export-avancé)
3. [Recherche et Filtrage](#recherche-et-filtrage)
4. [Dashboard Admin](#dashboard-admin)
5. [Monitoring & Métriques](#monitoring--métriques)
6. [CLI Avancée](#cli-avancée)
7. [Logging Audit](#logging-audit)
8. [Webhooks](#webhooks)
9. [Rate Limiting](#rate-limiting)

---

## API v3 Avancée

### 📊 Statistiques Détaillées

```bash
GET /api/v3/analytics/report/<report_id>
```

**Retour:**
```json
{
  "report_id": "import_xyz",
  "timestamp": "2024-01-15T10:30:00",
  "summary": {
    "total_entries": 89929,
    "valid_entries": 85000,
    "error_entries": 4929,
    "success_rate": 94.52
  },
  "breakdown": {
    "by_mode": {
      "SF": 45000,
      "RF": 44929,
      "OTHER": 0
    }
  },
  "pages": {
    "total": 250000,
    "average": 2.78,
    "by_mode": {
      "SF": 125000,
      "RF": 125000
    }
  }
}
```

### ⚠️ Rapport d'Erreurs

```bash
GET /api/v3/errors/<report_id>
```

**Retour:**
```json
{
  "report_id": "import_xyz",
  "total_errors": 4929,
  "error_breakdown": {
    "Invalid FAX mode": 1000,
    "Number format invalid": 2000,
    "Pages must be > 0": 1929
  }
}
```

### 🏥 Health Check Détaillé

```bash
GET /api/v3/health
```

---

## Export Avancé

### 📥 Exporter en CSV

```bash
GET /api/v3/export/<report_id>/csv
```

Retourne un fichier CSV téléchargeable avec toutes les données.

**Colonnes:**
- fax_id
- mode
- numero_original
- numero_normalise
- pages
- valide (0/1)
- erreurs
- date_heure

---

## Recherche et Filtrage

### 🔍 Recherche Avancée

```bash
GET /api/v3/search/<report_id>?q=33123456789&mode=SF&status=invalid&page=1&per_page=50
```

**Paramètres:**
- `q`: Recherche par numéro ou FAX ID
- `mode`: Filtre par mode (SF, RF)
- `status`: valid ou invalid
- `page`: Numéro de page (défaut: 1)
- `per_page`: Résultats par page (défaut: 50)

**Retour:**
```json
{
  "total": 2000,
  "page": 1,
  "per_page": 50,
  "pages": 40,
  "results": [...]
}
```

---

## Dashboard Admin

### 🎯 Accès

URL: `http://localhost:5000/admin`

**Fonctionnalités:**
- 📊 Statistiques système en temps réel
- 💻 Utilisation CPU/Mémoire
- ⏱️ Uptime serveur
- 💾 Performance du cache
- 📈 Métriques API
- ⏳ Détails de santé du système

### Auto-Refresh

Le dashboard se rafraîchit automatiquement toutes les 30 secondes.

---

## Monitoring & Métriques

### 📊 API Métriques Système

```bash
GET /api/admin/metrics
```

**Retour:**
```json
{
  "system": {
    "cpu_percent": 15.2,
    "memory_mb": 256.5,
    "memory_percent": 12.3,
    "num_threads": 8,
    "uptime_seconds": 3600
  },
  "uptime": {
    "seconds": 3600,
    "formatted": "1.0h"
  },
  "metrics_summary": {...},
  "rate_limiter_stats": {...}
}
```

### 🏥 Health Check Détaillé

```bash
GET /api/admin/health/detailed
```

Inclut:
- État de la base de données
- Nombre de rapports
- Nombre d'entrées
- Métriques système
- Stats du cache
- Stats du rate limiter

---

## CLI Avancée

### 📋 Installation

```bash
pip install tabulate
```

### 🎯 Commandes Disponibles

#### **Status Système**
```bash
python cli.py status
```

Affiche:
- Total de rapports
- Total de FAX
- Statistiques de validation
- Utilisation CPU/Mémoire
- Uptime

#### **Lister les Rapports**
```bash
python cli.py reports list
```

#### **Statistiques d'un Rapport**
```bash
python cli.py entries stats REPORT_ID
```

Affiche:
- Statistiques par mode
- Statistiques de validation

#### **Stats du Cache**
```bash
python cli.py cache stats
```

Affiche:
- Cache hits/misses
- Hit rate
- Nombre d'évictions

#### **Logs d'Audit**
```bash
python cli.py audit log --limit 50
```

Affiche les 50 derniers événements d'audit.

#### **Sauvegarde Base de Données**
```bash
python cli.py database backup
```

Crée un backup SQL dans `backups/`

#### **Re-valider tous les FAX**
```bash
python cli.py validate all
```

Re-exécute la validation sur tous les FAX entré.

---

## Logging Audit

### 📋 Fichier d'Audit

Localisation: `logs/audit.log`

**Format JSON:**
```json
{
  "timestamp": "2024-01-15T10:30:00",
  "event_type": "upload",
  "user_id": "anonymous",
  "resource_id": "import_xyz",
  "action": "file_import",
  "status": "success",
  "details": {
    "file_size": 2500000,
    "total_entries": 89929,
    "valid_entries": 85000,
    "success_rate": "94.52%"
  }
}
```

### 📊 Types d'Événements

- `upload` - Import de fichier
- `export` - Export de données
- `api_call` - Appels API
- `delete` - Suppression
- `validation` - Validations

---

## Webhooks

### 📡 Enregistrer un Webhook

```bash
POST /api/v3/webhooks/register
```

**Payload:**
```json
{
  "url": "https://example.com/webhook",
  "event": "upload_complete"
}
```

**Retour:**
```json
{
  "webhook_id": "webhook_1"
}
```

### 📋 Lister les Webhooks

```bash
GET /api/v3/webhooks
```

### 🔔 Événements Disponibles

- `upload_complete` - Upload terminé
- `error` - Erreur détectée
- `validation_complete` - Validation terminée
- `export_complete` - Export terminé

---

## Rate Limiting

### ⚙️ Configuration

Par défaut: **60 requêtes/minute** par endpoint par IP

### 📊 Vérifier les Stats

```bash
GET /api/admin/metrics
```

Inclut les statistiques du rate limiter.

### 🚀 Contourner (Admin Only)

Ajouter le header (si implémenté):
```
X-Rate-Limit-Bypass: admin_token
```

---

## 🎯 Exemples d'Utilisation

### 1️⃣ Récupérer les stats d'un rapport

```bash
curl http://localhost:5000/api/v3/analytics/report/import_xyz
```

### 2️⃣ Exporter les données

```bash
curl http://localhost:5000/api/v3/export/import_xyz/csv > report.csv
```

### 3️⃣ Chercher les erreurs

```bash
curl http://localhost:5000/api/v3/search/import_xyz?status=invalid&page=1
```

### 4️⃣ Accéder au dashboard

```
http://localhost:5000/admin
```

### 5️⃣ Utiliser la CLI

```bash
python cli.py status
python cli.py reports list
python cli.py cache stats
```

---

## 🔒 Sécurité

### ✅ Implémenté

- Rate limiting par endpoint
- Audit logging complet
- Validation des inputs
- Error handling robuste

### 🔜 À Implémenter (Future)

- Authentification API (JWT/OAuth)
- Chiffrement des données sensibles
- CORS configuration
- API key management

---

## 📈 Performance

### 🚀 Optimisations

- **Caching intelligent** avec TTL et dépendances
- **GZIP compression** sur les réponses
- **Pagination** sur les grandes datasets
- **Indexes composites** en base de données
- **Lazy loading** des données

### 📊 Métriques Actuelles

- Temps d'import 89K FAX: ~4 secondes
- Mémoire utilisée: ~256 MB
- Cache hit rate: ~85% (avec warming)
- Requêtes/seconde: 100+ (non limité)

---

## 🐛 Troubleshooting

### Q: Pourquoi le dashboard ne charge pas?

**R:** Vérifier que le serveur tourne: `python web/app.py`

### Q: Comment activer la verbosité des logs?

**R:** Modifier `LOG_LEVEL` dans `src/core/config.py`

### Q: Problème de rate limit?

**R:** Vérifier `/api/admin/metrics` pour voir les limites actuelles

### Q: Export très lent?

**R:** Vérifier la charge CPU via `/api/admin/metrics`

---

## 📞 Support

Pour plus d'aide:
1. Consulter les logs: `tail -f logs/app.log`
2. Vérifier le dashboard: `http://localhost:5000/admin`
3. Tester l'API: `curl http://localhost:5000/api/v3/health`

**Enjoy the new FaxCloud v3.0 features!** 🎉
