# 🗄️ Configuration MySQL - FaxCloud Analyzer

## ✅ Prérequis

- **WampServer** démarré (Apache + MySQL + PHP)
- **Python 3.8+** installé
- Package Python **mysql-connector-python** (dans requirements.txt)

---

## 📋 Étapes de Configuration

### 1️⃣ Vérifier que WampServer est actif

1. Démarrez **WampServer**
2. Vérifiez que MySQL est **vert** (système de notification)
3. Accédez à **http://localhost/phpmyadmin** pour confirmer

### 2️⃣ Installer les dépendances Python

```bash
pip install -r requirements.txt
```

Cela installera `mysql-connector-python>=8.0.0`

### 3️⃣ Initialiser la base de données

Exécutez le script d'initialisation:

```bash
python init_mysql.py
```

Ce script va:
- ✅ Tester la connexion MySQL
- ✅ Créer la base de données `faxcloud_analyzer`
- ✅ Créer les tables `reports` et `fax_entries`
- ✅ Afficher les statistiques

### 4️⃣ Accéder à la base de données

**Via phpMyAdmin (interface web):**
- URL: http://localhost/phpmyadmin
- Base: `faxcloud_analyzer`
- Utilisateur: `root`
- Mot de passe: (vide par défaut)

**Via ligne de commande (MySQL CLI):**
```bash
mysql -h localhost -u root faxcloud_analyzer
```

---

## 🔧 Configuration Personnalisée

Si vous avez changé les paramètres MySQL (mot de passe, port, etc.):

1. Éditez `src/core/config.py`
2. Modifiez le dictionnaire `MYSQL_CONFIG`:

```python
MYSQL_CONFIG = {
    'host': 'localhost',              # Adresse MySQL
    'user': 'root',                   # Utilisateur
    'password': 'votreMotdePasse',    # Mot de passe (si défini)
    'database': 'faxcloud_analyzer',  # Nom base
    'port': 3306                      # Port MySQL
}
```

---

## 🗂️ Structure des Tables

### Table `reports`
```sql
id (VARCHAR 36) - Identifiant unique du rapport
date_rapport (DATETIME) - Date du rapport
contract_id (VARCHAR 100) - ID du contrat
date_debut (DATE) - Date de début d'analyse
date_fin (DATE) - Date de fin d'analyse
total_fax (INT) - Nombre total de FAX
fax_envoyes (INT) - FAX envoyés (mode SF)
fax_recus (INT) - FAX reçus (mode RF)
pages_totales (INT) - Nombre total de pages
erreurs_totales (INT) - Nombre total d'erreurs
taux_reussite (FLOAT) - Taux de réussite (%)
qr_path (VARCHAR 255) - Chemin du code QR
url_rapport (VARCHAR 255) - URL du rapport
created_at (DATETIME) - Timestamp création
```

### Table `fax_entries`
```sql
id (VARCHAR 36) - Identifiant unique de l'entrée
report_id (VARCHAR 36) - Référence au rapport (FK)
fax_id (VARCHAR 100) - ID du FAX source
utilisateur (VARCHAR 100) - Utilisateur
type (VARCHAR 10) - Type (SF/RF)
numero_original (VARCHAR 20) - Numéro d'origine
numero_normalise (VARCHAR 20) - Numéro normalisé
valide (BOOLEAN) - Validité du numéro
pages (INT) - Nombre de pages
datetime (DATETIME) - Date/heure du FAX
erreurs (JSON) - Erreurs détaillées
created_at (DATETIME) - Timestamp création
```

---

## 🧪 Test de Connexion

Pour tester directement en Python:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src' / 'core'))

import db
import config

# Test connexion
try:
    conn = db.get_db_connection()
    print("✅ Connexion réussie!")
    
    # Récupérer les statistiques
    stats = db.get_statistics()
    print(f"Rapports: {stats['total_reports']}")
    
    conn.close()
except Exception as e:
    print(f"❌ Erreur: {e}")
```

---

## ⚠️ Dépannage

### Erreur: "Access denied for user 'root'@'localhost'"
- Vérifiez que WampServer MySQL est démarré (notification rouge = arrêté)
- Vérifiez le mot de passe MySQL dans `config.py`

### Erreur: "Can't connect to MySQL server"
- Démarrez WampServer
- Vérifiez que MySQL est accessible sur 127.0.0.1:3306
- Essayez: `mysql -h 127.0.0.1 -u root` en terminal

### Erreur: "Base de données faxcloud_analyzer n'existe pas"
- Exécutez `python init_mysql.py` pour créer la base
- Ou lancez l'app (elle crée la base automatiquement)

### Comment voir les données en temps réel?
- Utilisez **phpMyAdmin**: http://localhost/phpmyadmin
- Ou **MySQL Workbench** (gratuit, complet)
- Ou la ligne de commande: `mysql -u root faxcloud_analyzer`

---

## 🎯 Prochaines Étapes

1. ✅ Base de données configurée
2. 📊 Lancez l'application: `python main.py import --file data.csv`
3. 🔍 Vérifiez les données en phpMyAdmin
4. 🌐 Accédez à l'interface web: `launch-web.bat`

---

**Questions?** Consultez les documents:
- `DOCUMENTATION.md` - Spécifications complètes
- `README.md` - Guide utilisateur
- `ARCHITECTURE.md` - Architecture technique
