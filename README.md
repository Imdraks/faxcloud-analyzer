# FaxCloud Analyzer (FastAPI + SQLite/PostgreSQL)

Plateforme interne et open-source pour importer et analyser les exports FaxCloud (CSV/XLSX), générer des rapports versionnés, produire des QR codes et servir des vues desktop/mobile sans aucune dépendance cloud.

## Sommaire
- [Fonctionnalités](#fonctionnalités)
- [Architecture](#architecture)
- [Installation rapide (Debian / RPi5)](#installation-rapide-debian--rpi5)
- [Lancer en dev](#lancer-en-dev)
- [Migrations Alembic](#migrations-alembic)
- [Déploiement systemd + nginx](#déploiement-systemd--nginx)
- [API (exemples curl)](#api-exemples-curl)
- [Tests](#tests)
- [Structure du dépôt](#structure-du-dépôt)

## Fonctionnalités
- Upload CSV/XLSX (`/api/reports/upload`) avec checksum SHA256 et blocage de doublons (configurable).
- Mapping flexible des colonnes via `config/columns.yaml` + auto-détection de synonymes.
- Analyse statistique : succès/échecs, taux de réussite, top codes d’erreur, série temporelle, détection simple d’anomalies.
- Stockage des fichiers originaux, QR code PNG par rapport, page mobile `/r/<token>` et image `/q/<token>.png`.
- Dashboard protégé par Basic Auth (ADMIN_USER/ADMIN_PASS), vues desktop `/dashboard` et détail `/dashboard/reports/{id}`.
- Base SQLite par défaut, bascule PostgreSQL via env, migrations Alembic.
- Journalisation structurée dans `./data/logs/app.log`.
- Option watchdog pour surveiller `./data/inbox` et auto-importer (WATCH_INBOX=true).

## Architecture
- **Backend** : FastAPI + SQLModel/SQLAlchemy, Alembic.
- **Parsing** : pandas/openpyxl/csv.
- **Frontend** : Jinja2 + HTML/CSS/JS vanilla (responsive).
- **DB** : SQLite (par défaut) ou PostgreSQL (env `USE_POSTGRES=true`).
- **Sécurité** : Basic Auth sur dashboard/API, QR public configurable (`PUBLIC_QR_ALLOWED`). CORS off par défaut.

## Installation rapide (Debian / RPi5)
```bash
sudo apt update && sudo apt install -y python3.11 python3.11-venv python3-pip
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install poetry
poetry install --no-root
cp .env.example .env  # puis ajuster ADMIN_USER/ADMIN_PASS
```

## Lancer en dev
```bash
source .venv/bin/activate
poetry run alembic upgrade head
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Accès : `http://localhost:8000/dashboard` (Basic Auth requis).

## Migrations Alembic
```bash
poetry run alembic upgrade head      # appliquer
poetry run alembic revision --autogenerate -m "message"  # nouvelle révision
poetry run alembic downgrade -1      # revenir en arrière
```
La config Alembic pointe sur `app.db.session:get_engine_url`.

## Déploiement systemd + nginx
1. **systemd** : copier `deploy/faxcloud-analyzer.service` dans `/etc/systemd/system/` puis :
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable --now faxcloud-analyzer
   ```
2. **nginx (optionnel)** : exemple dans `deploy/nginx.conf`, placer sous `/etc/nginx/sites-available/` et lier vers `sites-enabled`, puis `sudo nginx -t && sudo systemctl reload nginx`.
3. **Firewall** : restreindre au LAN (ex: `ufw allow from 192.168.0.0/16 to any port 8000` ou binder sur `127.0.0.1` et exposer via nginx).

## API (exemples curl)
```bash
# Upload (Basic Auth)
curl -u admin:change-me -F "file=@tests/fixtures/sample.csv" \
  http://localhost:8000/api/reports/upload

# Liste paginée
curl -u admin:change-me "http://localhost:8000/api/reports?limit=10&status=failed"

# Détail + stats
curl -u admin:change-me http://localhost:8000/api/reports/<report_id>

# Télécharger l’original
curl -u admin:change-me -OJ http://localhost:8000/api/reports/<report_id>/download

# Export JSON (public_token dans la réponse du détail)
curl http://localhost:8000/r/<public_token>
```

## Tests
```bash
poetry run pytest
```

## Structure du dépôt
```
app/
  main.py
  core/
  db/
  services/
  api/
  templates/
  static/
config/columns.yaml
data/ (créé au runtime)
deploy/ (systemd + nginx)
tests/ (unit + API + fixtures)
```

## Notes sécurité
- Par défaut l’app écoute sur 0.0.0.0 : ajuster `API_HOST` si nécessaire.
- QR public accessible si `PUBLIC_QR_ALLOWED=true`; sinon, exiger auth sur les routes QR.
- Aucune intégration cloud, toutes les dépendances sont locales.
