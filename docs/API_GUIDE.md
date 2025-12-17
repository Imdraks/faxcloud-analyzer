# 📡 Guide Complet API FaxCloud Analyzer v3.0

## Table des Matières
1. [Vue d'ensemble](#vue-densemble)
2. [Authentification](#authentification)
3. [Endpoints Reports](#endpoints-reports)
4. [Endpoints Stats](#endpoints-stats)
5. [Endpoints Admin](#endpoints-admin)
6. [Format des Réponses](#format-des-réponses)
7. [Codes d'Erreur](#codes-derreur)
8. [Exemples complets](#exemples-complets)

---

## Vue d'ensemble

**Base URL**: `http://127.0.0.1:5000/api`

**Format**: JSON  
**Version**: 3.0  
**Status**: ✅ Production  

### Headers Recommandés
```json
{
    "Content-Type": "application/json",
    "Accept": "application/json"
}
```

---

## Authentification

> Actuellement pas requise pour le développement. À implémenter avec JWT.

---

## Endpoints Reports

### 1. Récupérer tous les rapports

**Request**
```http
GET /reports?limit=20&offset=0
```

**Paramètres**
| Param | Type | Défaut | Description |
|-------|------|--------|-------------|
| limit | int | 20 | Nombre de rapports à retourner |
| offset | int | 0 | Décalage pour pagination |

**Response** (200 OK)
```json
[
    {
        "id": 1,
        "name": "Rapport_20251217_001",
        "file_size": 125000,
        "entries": 500,
        "valid": 495,
        "errors": 5,
        "status": "completed",
        "created_at": "2025-12-17T16:00:00"
    }
]
```

**Exemple cURL**
```bash
curl -X GET "http://127.0.0.1:5000/api/reports?limit=10" \
  -H "Accept: application/json"
```

**Exemple JavaScript**
```javascript
fetch('/api/reports?limit=10')
    .then(res => res.json())
    .then(data => console.log(data));
```

---

### 2. Récupérer un rapport spécifique

**Request**
```http
GET /reports/<report_id>
```

**Paramètres**
| Param | Type | Description |
|-------|------|-------------|
| report_id | int | ID du rapport |

**Response** (200 OK)
```json
{
    "id": 1,
    "name": "Rapport_20251217_001",
    "file_size": 125000,
    "entries": 500,
    "valid": 495,
    "errors": 5,
    "status": "completed",
    "created_at": "2025-12-17T16:00:00"
}
```

**Erreurs possibles**
- 404 Not Found: Rapport inexistant

---

### 3. Créer un nouveau rapport

**Request**
```http
POST /reports
Content-Type: application/json

{
    "name": "Nouveau Rapport",
    "file_size": 50000
}
```

**Corps**
| Clé | Type | Requis | Description |
|-----|------|--------|-------------|
| name | string | ✅ | Nom du rapport |
| file_size | int | ❌ | Taille du fichier en bytes |

**Response** (201 Created)
```json
{
    "id": 6,
    "name": "Nouveau Rapport",
    "file_size": 50000,
    "entries": 0,
    "valid": 0,
    "errors": 0,
    "status": "processing",
    "created_at": "2025-12-17T16:30:00"
}
```

**Exemple cURL**
```bash
curl -X POST "http://127.0.0.1:5000/api/reports" \
  -H "Content-Type: application/json" \
  -d '{"name":"Mon Rapport","file_size":75000}'
```

---

### 4. Récupérer les entrées d'un rapport

**Request**
```http
GET /reports/<report_id>/entries?limit=50&offset=0
```

**Paramètres**
| Param | Type | Défaut | Description |
|-------|------|--------|-------------|
| report_id | int | - | ID du rapport |
| limit | int | 50 | Nombre d'entrées |
| offset | int | 0 | Décalage |

**Response** (200 OK)
```json
[
    {
        "id": 1,
        "report_id": 1,
        "fax_number": "+33123456789",
        "caller_id": "Caller_1",
        "recipient": "Recipient_1",
        "duration": 120,
        "page_count": 5,
        "status": "valid",
        "error_message": null,
        "created_at": "2025-12-17T16:00:00"
    }
]
```

---

### 5. Ajouter une entrée FAX

**Request**
```http
POST /reports/<report_id>/entries
Content-Type: application/json

{
    "fax_number": "+33123456789",
    "caller_id": "Caller_1",
    "recipient": "Recipient_1",
    "duration": 120,
    "page_count": 5,
    "status": "valid"
}
```

**Corps**
| Clé | Type | Requis | Description |
|-----|------|--------|-------------|
| fax_number | string | ✅ | Numéro FAX |
| caller_id | string | ✅ | Identifiant de l'appelant |
| recipient | string | ✅ | Destinataire |
| duration | int | ❌ | Durée en secondes |
| page_count | int | ❌ | Nombre de pages |
| status | string | ✅ | "valid" ou "error" |
| error_message | string | ❌ | Message d'erreur si applicable |

**Response** (201 Created)
```json
{
    "id": 100,
    "report_id": 1,
    "fax_number": "+33123456789",
    "caller_id": "Caller_1",
    "recipient": "Recipient_1",
    "duration": 120,
    "page_count": 5,
    "status": "valid",
    "error_message": null,
    "created_at": "2025-12-17T16:30:00"
}
```

---

### 6. Exporter un rapport

**Request**
```http
GET /reports/<report_id>/export
```

**Response** (200 OK)
```json
{
    "report": {
        "id": 1,
        "name": "Rapport_20251217_001",
        ...
    },
    "entries": [
        { "id": 1, ... },
        { "id": 2, ... }
    ]
}
```

---

## Endpoints Stats

### 1. Statistiques globales

**Request**
```http
GET /stats
```

**Response** (200 OK)
```json
{
    "total_reports": 5,
    "total_entries": 2500,
    "valid_entries": 2450,
    "error_entries": 50,
    "success_rate": 98.0
}
```

---

### 2. Tendances

**Request**
```http
GET /trends?days=7
```

**Paramètres**
| Param | Type | Défaut | Description |
|-------|------|--------|-------------|
| days | int | 7 | Nombre de jours |

**Response** (200 OK)
```json
[
    {
        "date": "2025-12-11",
        "total": 1250,
        "valid": 1240
    },
    {
        "date": "2025-12-12",
        "total": 1500,
        "valid": 1485
    }
]
```

---

### 3. Health Check

**Request**
```http
GET /health
```

**Response** (200 OK)
```json
{
    "status": "online",
    "version": "3.0",
    "service": "FaxCloud Analyzer"
}
```

---

## Endpoints Admin

### 1. Santé détaillée du système

**Request**
```http
GET /admin/health/detailed
```

**Response** (200 OK)
```json
{
    "status": "healthy",
    "database": {
        "reports": 5,
        "entries": 2500
    },
    "uptime": 3600
}
```

---

### 2. Métriques système

**Request**
```http
GET /admin/metrics
```

**Response** (200 OK)
```json
{
    "cpu_usage": 35,
    "memory_usage": 42,
    "disk_usage": 28,
    "database_size": 2048,
    "reports_today": 5,
    "entries_today": 1250,
    "avg_processing_time": 12.5,
    "error_rate": 2.0,
    "success_rate": 98.0
}
```

---

## Format des Réponses

### Succès (2xx)
```json
{
    "data": {...}
}
```

### Erreur (4xx, 5xx)
```json
{
    "error": "Description de l'erreur",
    "code": "ERROR_CODE"
}
```

---

## Codes d'Erreur

| Code | Status | Description |
|------|--------|-------------|
| 200 | OK | Requête réussie |
| 201 | Created | Ressource créée |
| 400 | Bad Request | Données invalides |
| 404 | Not Found | Ressource inexistante |
| 500 | Server Error | Erreur serveur |
| 503 | Service Unavailable | Service indisponible |

---

## Exemples Complets

### Exemple 1: Obtenir les stats et afficher

```javascript
async function getStats() {
    try {
        const response = await fetch('/api/stats');
        if (!response.ok) throw new Error('Network response was not ok');
        const stats = await response.json();
        
        console.log(`Total Reports: ${stats.total_reports}`);
        console.log(`Success Rate: ${stats.success_rate}%`);
    } catch (error) {
        console.error('Error:', error);
    }
}

getStats();
```

---

### Exemple 2: Créer un rapport et ajouter des entrées

```javascript
async function createReportWithEntries() {
    // Créer le rapport
    const reportRes = await fetch('/api/reports', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            name: 'Mon Rapport',
            file_size: 100000 
        })
    });
    const report = await reportRes.json();
    const reportId = report.id;

    // Ajouter une entrée
    const entryRes = await fetch(`/api/reports/${reportId}/entries`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            fax_number: '+33123456789',
            caller_id: 'Caller_1',
            recipient: 'Recipient_1',
            duration: 120,
            page_count: 5,
            status: 'valid'
        })
    });
    const entry = await entryRes.json();
    
    console.log('Report created:', reportId);
    console.log('Entry added:', entry.id);
}

createReportWithEntries();
```

---

### Exemple 3: Obtenir les tendances et les afficher

```javascript
async function displayTrends() {
    const response = await fetch('/api/trends?days=7');
    const trends = await response.json();
    
    trends.forEach(trend => {
        console.log(`${trend.date}: ${trend.total} entrées (${trend.valid} valides)`);
    });
}

displayTrends();
```

---

## 🎯 Bonnes Pratiques

1. **Toujours valider les réponses**
   ```javascript
   if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
   ```

2. **Gérer les timeouts**
   ```javascript
   const controller = new AbortController();
   const timeoutId = setTimeout(() => controller.abort(), 5000);
   ```

3. **Implémenter la pagination**
   ```javascript
   // Page 1
   fetch('/api/reports?limit=20&offset=0')
   // Page 2
   fetch('/api/reports?limit=20&offset=20')
   ```

4. **Utiliser le caching**
   ```javascript
   const cache = new Map();
   ```

---

## 📚 Ressources

- [Documentation Flask](https://flask.palletsprojects.com/)
- [JSON API Standard](https://jsonapi.org/)
- [HTTP Status Codes](https://httpwg.org/specs/rfc9110.html)

---

**Document créé**: 2025-12-17  
**Version API**: 3.0  
**Auteur**: FaxCloud Team
