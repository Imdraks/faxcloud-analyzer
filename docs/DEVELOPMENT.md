# 👨‍💻 Guide Développement - FaxCloud Analyzer v3.0

## Démarrage Rapide

### 1️⃣ Setup Environnement

```bash
# Clone
git clone https://github.com/your-repo/faxcloud-analyzer.git
cd faxcloud-analyzer

# Windows
setup.bat

# Linux/macOS
chmod +x setup.sh
./setup.sh
```

### 2️⃣ Structure du Projet

```
app/
├── __init__.py          # Flask factory
├── routes.py            # All routes
├── models/              # Data models
├── utils/               # Helper functions
├── templates/           # HTML templates
└── static/              # CSS/JS

config/
└── settings.py          # Configuration

docs/
├── API_GUIDE.md         # API documentation
├── DEPLOYMENT.md        # Deployment guide
└── ARCHITECTURE.md      # Architecture details
```

### 3️⃣ Lancer l'Application

```bash
# Développement
python run.py
# Accès: http://127.0.0.1:5000

# Production
gunicorn wsgi:app --workers 4
```

---

## 🔧 Développement Local

### Ajouter une Route Web

```python
# app/routes.py

@bp_web.route('/mon-page')
def ma_page():
    """Ma nouvelle page"""
    return render_template('ma_page.html')
```

### Ajouter une Route API

```python
# app/routes.py

@bp_api.route('/data', methods=['GET'])
def api_get_data():
    """Récupérer les données"""
    data = {'message': 'Hello'}
    return jsonify(data), 200

@bp_api.route('/data', methods=['POST'])
def api_create_data():
    """Créer les données"""
    data = request.get_json()
    # Process data...
    return jsonify({'id': 1}), 201
```

### Créer un Template

```html
<!-- app/templates/ma_page.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Ma Page</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <h1>Welcome</h1>
    <script src="{{ url_for('static', filename='js/app.js') }}"></script>
</body>
</html>
```

### Ajouter un Modèle

```python
# app/models/__init__.py

class MyModel(db.Model):
    __tablename__ = 'my_table'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at.isoformat()
        }
```

---

## 📊 Utiliser l'API

### GET Requests

```javascript
// Simple GET
fetch('/api/reports')
    .then(res => res.json())
    .then(data => console.log(data));

// GET avec paramètres
fetch('/api/reports?limit=10&offset=0')
    .then(res => res.json())
    .then(data => console.log(data));
```

### POST Requests

```javascript
// Simple POST
fetch('/api/reports', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        name: 'Mon Rapport'
    })
})
.then(res => res.json())
.then(data => console.log(data));
```

### Error Handling

```javascript
fetch('/api/reports')
    .then(async res => {
        if (!res.ok) {
            const error = await res.json();
            throw new Error(error.message);
        }
        return res.json();
    })
    .catch(err => {
        console.error('Error:', err.message);
    });
```

---

## 🎨 Frontend Development

### Structure CSS

```css
/* app/static/css/style.css */

:root {
    --primary: #667eea;
    --secondary: #764ba2;
    --success: #10b981;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto;
    color: var(--primary);
}
```

### Responsive Design

```css
/* Desktop */
@media (min-width: 1024px) {
    .container { max-width: 1200px; }
}

/* Tablet */
@media (min-width: 768px) and (max-width: 1023px) {
    .container { max-width: 768px; }
}

/* Mobile */
@media (max-width: 767px) {
    .container { max-width: 100%; }
}
```

### Charts avec Chart.js

```javascript
// Dashboard
const ctx = document.getElementById('myChart').getContext('2d');
const chart = new Chart(ctx, {
    type: 'bar',
    data: {
        labels: ['Jan', 'Feb', 'Mar'],
        datasets: [{
            label: 'Sales',
            data: [12, 19, 3],
            backgroundColor: '#667eea'
        }]
    }
});
```

---

## 🧪 Testing

### Tester l'API

```bash
# Health check
curl http://127.0.0.1:5000/api/health

# Get stats
curl http://127.0.0.1:5000/api/stats

# Get reports
curl http://127.0.0.1:5000/api/reports

# Create report
curl -X POST http://127.0.0.1:5000/api/reports \
  -H "Content-Type: application/json" \
  -d '{"name":"Test"}'
```

### Unit Tests

```python
# tests/test_api.py
import unittest
from app import create_app

class TestAPI(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
    
    def test_health(self):
        resp = self.client.get('/api/health')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('status', resp.json)

if __name__ == '__main__':
    unittest.main()
```

---

## 🔍 Debugging

### Console Logs

```javascript
console.log('Info:', data);
console.error('Error:', error);
console.warn('Warning:', warning);
console.table(data);  // Afficher un tableau
```

### Flask Debugging

```python
from flask import current_app

# Log
current_app.logger.info("Message")
current_app.logger.error("Error")

# Debugger
import pdb; pdb.set_trace()
```

### Browser DevTools

- **F12** ou **Right-click → Inspect**
- **Network tab** pour voir les requêtes
- **Console tab** pour les erreurs JavaScript
- **Application tab** pour les cookies/storage

---

## 📦 Dépendances

### Ajouter une Nouvelle Dépendance

```bash
# Installer
pip install new-package

# Ajouter à requirements.txt
pip freeze > requirements.txt

# Ou manuellement
echo "new-package==1.0.0" >> requirements.txt
```

### Versions Actuelles

```
Flask==3.1.2
SQLAlchemy==2.0.x
Flask-Compress==1.x.x
PyMySQL==1.1.x
python-dotenv==1.0.x
```

---

## 🚀 Deployer une Fonction

### Ajout d'une Nouvelle Feature

1. **Créer une branche**
   ```bash
   git checkout -b feature/ma-feature
   ```

2. **Développer localement**
   ```bash
   # Faire les changements
   git add .
   git commit -m "Ajouter ma feature"
   ```

3. **Tester**
   ```bash
   python run.py
   # Vérifier que tout fonctionne
   ```

4. **Push & Pull Request**
   ```bash
   git push origin feature/ma-feature
   # Créer une PR sur GitHub
   ```

---

## 📝 Conventions de Code

### Nommage

```python
# Variables
report_name = "Mon Rapport"
get_all_reports()

# Classes
class ReportService:
    pass

# Constants
MAX_FILE_SIZE = 100 * 1024 * 1024
```

### Docstrings

```python
def get_report(report_id):
    """
    Récupérer un rapport spécifique.
    
    Args:
        report_id (int): L'ID du rapport
    
    Returns:
        dict: Les données du rapport
    
    Raises:
        ValueError: Si report_id est invalide
    """
    pass
```

### Commentaires

```python
# ✅ Bon
# Calculer le taux de succès
success_rate = (valid_entries / total_entries) * 100

# ❌ Mauvais
# Diviser et multiplier
success_rate = (valid_entries / total_entries) * 100
```

---

## 🐛 Résoudre les Bugs

### 1. Reproduire le bug
```bash
python run.py
# Reproduire les étapes
```

### 2. Localiser le bug
```python
# Ajouter des logs
current_app.logger.debug(f"Variable: {variable}")
```

### 3. Fixer le bug
```python
# Faire les corrections
```

### 4. Tester
```bash
# Vérifier que le fix fonctionne
```

### 5. Commit
```bash
git add .
git commit -m "Fix: description du bug"
```

---

## 📚 Ressources

- **Flask Docs**: https://flask.palletsprojects.com/
- **SQLAlchemy**: https://www.sqlalchemy.org/
- **Chart.js**: https://www.chartjs.org/
- **MDN Web Docs**: https://developer.mozilla.org/

---

## ❓ Questions Fréquentes

### Q: Où ajouter les constantes?
A: Dans `config/settings.py`

### Q: Comment accéder à l'app context?
A: Utiliser `current_app`

### Q: Comment gérer les erreurs?
A: Utiliser try/except et les status codes HTTP

### Q: Comment déboguer JavaScript?
A: Utiliser la console du navigateur (F12)

---

**Guide Développement** | Version 3.0 | 2025-12-17
