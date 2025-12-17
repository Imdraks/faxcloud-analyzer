# 🚀 Démarrage Rapide

## Pour Windows

### Option 1 : Script automatique (Recommandé)
```bash
start.bat
```

### Option 2 : Manuel
```bash
# Activer virtualenv
.venv\Scripts\activate.bat

# Installer dépendances
pip install -r requirements.txt

# Démarrer l'app
python run.py
```

## Pour Linux/Mac

```bash
# Créer et activer virtualenv
python3 -m venv .venv
source .venv/bin/activate

# Installer dépendances
pip install -r requirements.txt

# Démarrer l'app
python run.py
```

---

## 🌐 URLs d'Accès

| Service | URL |
|---------|-----|
| Dashboard | http://127.0.0.1:5000 |
| Admin | http://127.0.0.1:5000/admin |
| Rapports | http://127.0.0.1:5000/reports |
| API Health | http://127.0.0.1:5000/api/health |
| Stats | http://127.0.0.1:5000/api/stats |

---

## 📁 Structure à Comprendre

```
faxcloud-analyzer/
├── app/              ← Application principale
│   ├── __init__.py    (création Flask)
│   ├── routes.py      (toutes les routes)
│   └── templates/     (pages HTML)
│
├── config/           ← Configuration
│   └── settings.py    (variables centralisées)
│
├── run.py            ← Point d'entrée
├── start.bat         ← Script démarrage Windows
└── requirements.txt  ← Dépendances
```

---

## ⚙️ Configuration

1. Copier `.env.example` en `.env`
2. Adapter les valeurs (DB, etc.)
3. Redémarrer le serveur

---

## 🔧 Développement

### Ajouter une route

**Fichier:** `app/routes.py`

```python
@bp_api.route('/ma-route', methods=['GET'])
def ma_route():
    return jsonify({'message': 'Hello'}), 200
```

### Ajouter une page

**Fichier:** `app/templates/ma-page.html`

```html
<!DOCTYPE html>
<html>
<head><title>Ma Page</title></head>
<body>Contenu</body>
</html>
```

**Fichier:** `app/routes.py`

```python
@bp_web.route('/ma-page')
def ma_page():
    return render_template('ma-page.html')
```

---

## 📚 Documentation Complète

- **Architecture:** [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- **README:** [README_CLEAN.md](README_CLEAN.md)
- **Structure:** [STRUCTURE.md](STRUCTURE.md)

---

## ❌ Problèmes Courants

### Le serveur ne démarre pas
```
→ Vérifier: pip install -r requirements.txt
→ Vérifier: .venv existe
```

### Port 5000 déjà utilisé
```
FLASK_PORT=5001 python run.py
```

### Erreur de logging
```
→ Vérifier: dossier logs/ existe
→ Vérifier: permissions d'écriture
```

---

**Status:** ✅ Prêt à l'emploi  
**Version:** 3.0 Clean  
**Dernière MAJ:** Décembre 2025
