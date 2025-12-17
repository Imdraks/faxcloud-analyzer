# 🚀 Guide de Déploiement Production - FaxCloud Analyzer

## Prérequis

- Ubuntu 20.04+ ou Debian 10+
- Python 3.8+
- Nginx
- MySQL 8.0+
- Supervisor (pour process management)
- Certbot (pour SSL/TLS)

## 1️⃣ Installation des Dépendances Système

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv git curl wget
sudo apt install -y nginx mysql-server supervisor certbot python3-certbot-nginx
```

## 2️⃣ Cloner l'Application

```bash
cd /var/www
sudo git clone https://github.com/ton-repo/faxcloud-analyzer.git
cd faxcloud-analyzer
sudo chown -R www-data:www-data .
```

## 3️⃣ Configuration Python

```bash
# Créer environnement virtuel
python3 -m venv .venv
source .venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
pip install gunicorn

# Créer le fichier .env
sudo nano .env
```

### Contenu du fichier `.env`
```ini
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your-super-secret-key-here
DATABASE_URL=mysql://faxcloud:password@localhost/faxcloud
LOG_LEVEL=INFO
WORKERS=4
```

## 4️⃣ Configuration de la Base de Données

```bash
mysql -u root -p << EOF
CREATE DATABASE faxcloud CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'faxcloud'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON faxcloud.* TO 'faxcloud'@'localhost';
FLUSH PRIVILEGES;
EOF

# Initialiser la base de données
source .venv/bin/activate
python scripts/init_db.py
```

## 5️⃣ Configuration Gunicorn

Créer `/var/www/faxcloud-analyzer/wsgi.py`:
```python
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
```

## 6️⃣ Configuration Supervisor

Créer `/etc/supervisor/conf.d/faxcloud.conf`:
```ini
[program:faxcloud]
directory=/var/www/faxcloud-analyzer
command=/var/www/faxcloud-analyzer/.venv/bin/gunicorn \
    --workers 4 \
    --worker-class sync \
    --bind unix:/tmp/faxcloud.sock \
    --timeout 30 \
    --access-logfile - \
    --error-logfile - \
    wsgi:app
user=www-data
autostart=true
autorestart=true
stopwaitsecs=10
stdout_logfile=/var/log/faxcloud/access.log
stderr_logfile=/var/log/faxcloud/error.log

[group:faxcloud]
programs=faxcloud
priority=999
```

Démarrer Supervisor:
```bash
sudo mkdir -p /var/log/faxcloud
sudo chown www-data:www-data /var/log/faxcloud
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start faxcloud
```

## 7️⃣ Configuration Nginx

Créer `/etc/nginx/sites-available/faxcloud`:
```nginx
upstream faxcloud {
    server unix:/tmp/faxcloud.sock fail_timeout=0;
}

server {
    listen 80;
    server_name faxcloud.example.com;

    client_max_body_size 100M;
    
    location / {
        proxy_pass http://faxcloud;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }

    location /static/ {
        alias /var/www/faxcloud-analyzer/app/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Logs
    access_log /var/log/nginx/faxcloud_access.log combined;
    error_log /var/log/nginx/faxcloud_error.log;
}
```

Activer le site:
```bash
sudo ln -s /etc/nginx/sites-available/faxcloud /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 8️⃣ SSL/TLS avec Certbot

```bash
sudo certbot --nginx -d faxcloud.example.com -d www.faxcloud.example.com
```

## 9️⃣ Logging & Monitoring

### Logs
```bash
# Logs applicatifs
tail -f /var/log/faxcloud/error.log
tail -f /var/log/faxcloud/access.log

# Logs Nginx
tail -f /var/log/nginx/faxcloud_access.log
tail -f /var/log/nginx/faxcloud_error.log
```

### Monitoring
```bash
# Vérifier le statut du service
sudo supervisorctl status faxcloud

# Vérifier les processus
ps aux | grep gunicorn
```

## 🔟 Backup & Restore

### Backup
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/faxcloud"

mkdir -p $BACKUP_DIR

# Database backup
mysqldump -u faxcloud -p faxcloud > $BACKUP_DIR/db_${DATE}.sql

# Files backup
tar -czf $BACKUP_DIR/app_${DATE}.tar.gz /var/www/faxcloud-analyzer

echo "Backup completed: $DATE"
```

### Restore
```bash
# Restore database
mysql -u faxcloud -p faxcloud < /backups/faxcloud/db_20251217.sql

# Restore files
tar -xzf /backups/faxcloud/app_20251217.tar.gz
```

## 1️⃣1️⃣ Health Check

```bash
# API Health
curl https://faxcloud.example.com/api/health

# Response
# {
#   "status": "online",
#   "version": "3.0",
#   "service": "FaxCloud Analyzer"
# }
```

## 1️⃣2️⃣ Scaling

### Augmenter les Workers
```ini
# /etc/supervisor/conf.d/faxcloud.conf
command=/var/www/faxcloud-analyzer/.venv/bin/gunicorn \
    --workers 8 \  # Augmenter ce nombre
    --worker-class sync \
    ...
```

### Ajouter du Cache Redis
```python
# Dans config/settings.py
CACHE_TYPE = 'redis'
CACHE_REDIS_URL = 'redis://localhost:6379/0'
```

### Load Balancing
```nginx
upstream faxcloud {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}
```

## 📊 Performance

### Optimisations
- ✅ Gzip compression activé
- ✅ Cache statiques 30j
- ✅ Connection pooling
- ✅ Database indexing
- ✅ CDN pour assets

### Benchmarking
```bash
# Apache Bench
ab -n 1000 -c 100 https://faxcloud.example.com/

# Wrk
wrk -t12 -c400 -d30s https://faxcloud.example.com/
```

## 🔐 Sécurité

### Checklist
- ✅ SSH keys au lieu de passwords
- ✅ Firewall UFW configuré
- ✅ SSL/TLS forcé
- ✅ Headers de sécurité
- ✅ Rate limiting
- ✅ CSRF protection

```bash
# Configurer UFW
sudo ufw enable
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

## 📋 Checklist Déploiement

- [ ] Cloner le repository
- [ ] Configurer `.env`
- [ ] Initialiser la base de données
- [ ] Installer les dépendances
- [ ] Configurer Supervisor
- [ ] Configurer Nginx
- [ ] Configurer SSL/TLS
- [ ] Tester les endpoints
- [ ] Configurer les logs
- [ ] Setup le monitoring
- [ ] Configurer les backups
- [ ] Documenter les accès

## 🚨 Troubleshooting

### Application ne démarre pas
```bash
sudo supervisorctl tail -f faxcloud
```

### Erreur de permissions
```bash
sudo chown -R www-data:www-data /var/www/faxcloud-analyzer
sudo chmod -R 755 /var/www/faxcloud-analyzer
```

### Erreur de base de données
```bash
# Vérifier la connexion MySQL
mysql -u faxcloud -p -h localhost -D faxcloud -e "SELECT 1"

# Vérifier les variables d'environnement
cat /var/www/faxcloud-analyzer/.env
```

### Erreur 502 Bad Gateway
```bash
# Vérifier le socket
ls -la /tmp/faxcloud.sock

# Vérifier Gunicorn
ps aux | grep gunicorn
```

---

**Document créé**: 2025-12-17  
**Version**: 3.0.0  
**Status**: Production Ready ✅
