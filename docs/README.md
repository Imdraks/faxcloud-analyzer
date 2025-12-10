# 📊 FaxCloud Analyzer

**Analyseur professionnel de fichiers FAX avec validation, normalisation et statistiques en temps réel**

> Version: **1.0** | Python 3.8+ | MySQL (WampServer) | Interface Web Drag & Drop

---

## 🎯 Fonctionnalités

- 📤 **Drag & Drop** - Déposez vos fichiers CSV/XLSX facilement
- 🔍 **Analyse en temps réel** - Normalisation et validation instantanées
- 📊 **Statistiques complètes** - Globales, par erreur, par utilisateur
- 🗄️ **MySQL intégré** - Sauvegarde en base de données WampServer
- 🔗 **QR Code** - Génération et téléchargement PNG
- 📱 **Interface mobile** - Design responsive (mobile-first)
- 🚀 **Moteur Python** - CLI complet pour automatisation

---

## 📋 Spécifications

### Conditions d'analyse officielles
Consultez `CONDITIONS_ANALYSE.md` pour les règles complètes :

- **Normalisation** : +33XX → 33XX, 0XX → 33XX, 0033XX → 33XX
- **Longueur** : Exactement 11 chiffres
- **Indicatif** : Doit commencer par 33 (France)
- **Détection d'erreurs** : 4 types détaillés
- **Statistiques** : 15+ métriques

### Formats supportés

| Format | Support | Statut |
|--------|---------|--------|
| CSV | ✅ Oui | Production |
| XLSX | ⏳ Partiel | Requiert openpyxl |
| XLS | ⏳ Partiel | Requiert openpyxl |

---

## 🚀 Installation rapide

### 1. Préalables

- **Python 3.8+** ([Télécharger](https://www.python.org/downloads/))
- **WampServer** démarré ([Télécharger](https://www.wampserver.com/))
- **MySQL actif** sur WampServer

### 2. Installation des dépendances

**Option 1 - Script batch (Recommandé)**
```bash
install.bat
```

**Option 2 - Manuel**
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Initialiser MySQL

```bash
python init_mysql.py
```

Cela va:
- ✅ Créer la base `faxcloud_analyzer`
- ✅ Créer les tables `reports` et `fax_entries`
- ✅ Afficher les statistiques

---

## 💻 Utilisation

### Web Interface (Recommandé)

**Lancer l'application web:**
```bash
launch-web.bat
```

Puis:
1. Un navigateur s'ouvre sur `http://localhost:8000`
2. Déposez votre fichier CSV dans la zone de drag & drop
3. Les résultats s'affichent immédiatement
4. Téléchargez le QR code

### CLI (Command-Line)

**Analyser un fichier:**
```bash
python main.py import --file data/imports/export_2024_12.csv --contract "CLIENT_001" --start 2024-12-01 --end 2024-12-31
```

**Afficher les rapports:**
```bash
python main.py list
```

**Consulter un rapport:**
```bash
python main.py view --report-id "550e8400-e29b-41d4-a716-446655440000"
```

**Initialiser la base:**
```bash
python main.py init
```

---

## 📁 Structure du projet

```
faxcloud-analyzer/
├── src/
│   └── core/
│       ├── config.py                 # Configuration MySQL
│       ├── db.py                     # Gestion base de données
│       ├── validation_rules.py       # Règles de validation (17 tests ✅)
│       ├── analyzer.py               # Moteur d'analyse
│       ├── importer.py               # Lecteur CSV/XLSX
│       ├── reporter.py               # Génération rapports
│       └── __init__.py
├── web/
│   ├── app/
│   │   ├── app.html                  # Interface web
│   │   ├── app.css                   # Styles responsive
│   │   └── app.js                    # Moteur d'analyse JavaScript
│   ├── server.py                     # Serveur HTTP
│   ├── index.html                    # Ancien dashboard (optionnel)
│   └── style.css
├── data/
│   ├── imports/                      # Fichiers à analyser
│   ├── reports/                      # Rapports JSON
│   └── reports_qr/                   # Codes QR PNG
├── database/                         # Fichiers base données (unused - MySQL)
├── docs/
│   ├── CONDITIONS_ANALYSE.md         # Spécification officielle
│   ├── DOCUMENTATION.md              # Doc complète
│   ├── ARCHITECTURE.md               # Architecture technique
│   └── ...
├── main.py                           # Point d'entrée CLI
├── init_mysql.py                     # Script initialisation MySQL
├── install.bat                       # Installation dépendances
├── launch-web.bat                    # Lancement web
├── requirements.txt                  # Dépendances Python
├── README.md                         # Ce fichier
├── CONDITIONS_ANALYSE.md             # Conditions officielles
└── IMPLEMENTATION_STATUS.md          # Statut de conformité
```

---

## 🗄️ Configuration MySQL

### Paramètres par défaut

| Paramètre | Valeur |
|-----------|--------|
| Hôte | localhost |
| Port | 3306 |
| Utilisateur | root |
| Mot de passe | (vide) |
| Base | faxcloud_analyzer |

### Personnalisation

Éditez `src/core/config.py`:
```python
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'votreMotdePasse',  # Si défini
    'database': 'faxcloud_analyzer',
    'port': 3306
}
```

### Accès phpMyAdmin

- URL: `http://localhost/phpmyadmin`
- Base: `faxcloud_analyzer`

---

## 📊 Statistiques produites

### Globales
- Total FAX envoyés (SF)
- Total FAX reçus (RF)
- Total pages envoyées/reçues
- Taux de réussite (%)

### Par erreur
- Histogramme des 4 types d'erreurs
- Répartition en %

### Par utilisateur
- Nombre d'envois
- Nombre d'erreurs
- Taux de réussite
- Pages par utilisateur

---

## 🧪 Tests

### Valider les règles de normalisation

```bash
python src/core/validation_rules.py
```

Résultat attendu:
```
[RESULTATS] 17 OK | 0 ERREURS | Total: 17
```

### Test rapide

```python
from src.core.validation_rules import analyze_number

# Test
est_valide, numero_norm, erreur = analyze_number("+33 1 45 22 11 34")
print(est_valide)      # → True
print(numero_norm)     # → "33145221134"
print(erreur)          # → None
```

---

## 🔴 Types d'erreurs

| Erreur | Description | Exemple |
|--------|-------------|---------|
| **Numéro vide** | Champ vide ou caractères non-numériques | "" ou "---" |
| **Longueur incorrecte** | ≠ 11 chiffres | "0145221134" (10) |
| **Indicatif invalide** | Ne commence pas par 33 | "+1-212-555-1234" |
| **Format invalide** | Caractères illisibles/corrompus | "\x00\x01\x02" |

---

## 🐛 Dépannage

### Erreur: "Access denied for user 'root'@'localhost'"

1. Vérifiez que WampServer MySQL est **vert** (démarré)
2. Vérifiez le mot de passe dans `src/core/config.py`
3. Testez: `mysql -h localhost -u root`

### Erreur: "Can't connect to MySQL server"

1. Lancez WampServer
2. Vérifiez que MySQL écoute sur 127.0.0.1:3306
3. Attendez 10 secondes après le démarrage

### Erreur: "Base faxcloud_analyzer n'existe pas"

```bash
python init_mysql.py
```

### Fichier CSV non reconnu

- Format: UTF-8 sans BOM
- Séparateur: Virgule (,)
- Colonnes: 14 exactement (A-N)

---

## 📚 Documentation complète

- **CONDITIONS_ANALYSE.md** - Spécification officielle des règles
- **IMPLEMENTATION_STATUS.md** - Statut de conformité (17/17 tests ✅)
- **ARCHITECTURE.md** - Architecture technique complète
- **DOCUMENTATION.md** - Documentation détaillée (CLI, API, BD)
- **MYSQL_SETUP.md** - Configuration MySQL avancée
- **QUICK_START.md** - Guide de démarrage rapide

---

## 🤝 Contribution

Pour signaler un bug ou proposer une amélioration:

1. Consultez `CONDITIONS_ANALYSE.md`
2. Vérifiez les tests: `python src/core/validation_rules.py`
3. Créez un issue avec:
   - Description du problème
   - Fichier d'exemple
   - Comportement attendu vs obtenu

---

## 📝 Licence

Propriétaire - FaxCloud Analyzer v1.0 (Décembre 2025)

---

## 🎯 Roadmap

| Version | Statut | Fonctionnalités |
|---------|--------|---|
| **1.0** | ✅ Actuelle | Drag & Drop, Analyse locale, MySQL, QR Code |
| **1.1** | 🔜 Très proche | Export PDF, Notifications email |
| **2.0** | 📅 Planifiée | Intégration Asterisk, API REST complète |
| **3.0** | 📅 Futur | Dashboard temps réel, Webhooks |

---

## ❓ FAQ

**Q: Puis-je utiliser sans MySQL?**
A: Actuellement non, MySQL est requis pour la sauvegarde des résultats.

**Q: Les données sont-elles sécurisées?**
A: Oui, l'analyse se fait localement. Seuls les résultats sont sauvegardés en MySQL.

**Q: Combien de fichiers puis-je analyser?**
A: Limitation: taille fichier < 10MB, nombre d'entrées < 100 000 (pour performance).

**Q: Comment exporter les résultats?**
A: JSON via l'API ou téléchargement QR. Export PDF prévu en v1.1.

**Q: Asterisk est inclus?**
A: Non, c'est une fonctionnalité planifiée pour v2.0.

---

**Support:** Consultez les documents `docs/` ou les commentaires dans le code.

**Dernière mise à jour:** 10 décembre 2025 | **v1.0 - Production Ready**
