# 🍓 FaxCloud Analyzer - Guide Raspberry Pi

Guide complet pour installer et exécuter FaxCloud Analyzer sur Raspberry Pi.

## 📋 Prérequis

### Matériel recommandé
- **Raspberry Pi 4** ou **5** (2GB+ RAM recommandé)
- Carte microSD 16GB+ (classe 10 ou mieux)
- Alimentation officielle 5V/3A
- Connexion réseau (Ethernet recommandé)

### Système d'exploitation
- **Raspberry Pi OS 64-bit** (Bookworm) - **Recommandé**
- Ubuntu Server 22.04+ (ARM64)
- Debian 12+ (ARM64)

## 🚀 Installation rapide

### Option 1: Installation automatique (recommandée)

```bash
# Cloner ou copier le projet sur le Pi
git clone https://github.com/your-repo/faxcloud-analyzer.git
cd faxcloud-analyzer

# Exécuter le script d'installation
sudo chmod +x raspberry-pi/install.sh
sudo ./raspberry-pi/install.sh
```

### Option 2: Installation avec Docker

```bash
# Installer Docker (si pas déjà installé)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Démarrer l'application
cd faxcloud-analyzer
docker compose up -d

# Vérifier que ça fonctionne
docker compose logs -f
```

### Option 3: Installation manuelle

```bash
# 1. Mettre à jour le système
sudo apt update && sudo apt upgrade -y

# 2. Installer les dépendances
sudo apt install -y python3 python3-pip python3-venv git

# 3. Créer l'utilisateur
sudo useradd -r -s /bin/false -d /opt/faxcloud-analyzer faxcloud

# 4. Copier les fichiers
sudo mkdir -p /opt/faxcloud-analyzer
sudo cp -r . /opt/faxcloud-analyzer/
sudo chown -R faxcloud:faxcloud /opt/faxcloud-analyzer

# 5. Créer l'environnement Python
cd /opt/faxcloud-analyzer
sudo -u faxcloud python3 -m venv venv
sudo -u faxcloud ./venv/bin/pip install -r requirements.txt
sudo -u faxcloud ./venv/bin/pip install gunicorn

# 6. Installer le service systemd
sudo cp raspberry-pi/faxcloud-analyzer.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable faxcloud-analyzer
sudo systemctl start faxcloud-analyzer
```

## 🔧 Configuration

### Variables d'environnement

Créez un fichier `/opt/faxcloud-analyzer/.env`:

```bash
# Port du serveur web
PORT=8000

# Timezone
TZ=Europe/Paris

# Mode debug (désactiver en production)
DEBUG=false
```

### Configuration réseau

Par défaut, l'application écoute sur le port **8000**.

Pour accéder à l'interface web:
```
http://<IP_DU_PI>:8000
```

Pour trouver l'IP de votre Pi:
```bash
hostname -I
```

## 📊 Gestion du service

### Commandes systemd

```bash
# Démarrer
sudo systemctl start faxcloud-analyzer

# Arrêter
sudo systemctl stop faxcloud-analyzer

# Redémarrer
sudo systemctl restart faxcloud-analyzer

# Voir le statut
sudo systemctl status faxcloud-analyzer

# Voir les logs en temps réel
sudo journalctl -u faxcloud-analyzer -f

# Activer au démarrage
sudo systemctl enable faxcloud-analyzer
```

### Commandes Docker

```bash
# Démarrer
cd /opt/faxcloud-analyzer
docker compose up -d

# Arrêter
docker compose down

# Voir les logs
docker compose logs -f

# Reconstruire après mise à jour
docker compose up -d --build

# Voir l'utilisation des ressources
docker stats faxcloud-analyzer
```

## 🔐 Sécurité

### Pare-feu (UFW)

```bash
# Installer UFW
sudo apt install ufw

# Autoriser SSH et l'application
sudo ufw allow ssh
sudo ufw allow 8000/tcp

# Activer le pare-feu
sudo ufw enable
```

### Accès HTTPS (optionnel)

Pour HTTPS, utilisez un reverse proxy comme Nginx:

```bash
sudo apt install nginx

# Configuration Nginx
sudo nano /etc/nginx/sites-available/faxcloud
```

```nginx
server {
    listen 80;
    server_name votre-domaine.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/faxcloud /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

Pour HTTPS avec Let's Encrypt:
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d votre-domaine.com
```

## 📈 Optimisation Raspberry Pi

### Limiter l'utilisation mémoire

Le service est configuré pour utiliser max 512MB de RAM. Vous pouvez ajuster dans le fichier service:

```ini
MemoryMax=512M
MemoryHigh=384M
```

### Utiliser un SSD externe

Pour de meilleures performances, utilisez un SSD USB au lieu de la carte SD:

```bash
# Monter un SSD sur /opt/faxcloud-analyzer/data
sudo mount /dev/sda1 /opt/faxcloud-analyzer/data
```

### Swap (si mémoire insuffisante)

```bash
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# Changer CONF_SWAPSIZE=1024
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

## 🔄 Mise à jour

### Via Git

```bash
cd /opt/faxcloud-analyzer
sudo systemctl stop faxcloud-analyzer
sudo -u faxcloud git pull
sudo -u faxcloud ./venv/bin/pip install -r requirements.txt
sudo systemctl start faxcloud-analyzer
```

### Via Docker

```bash
cd /opt/faxcloud-analyzer
docker compose pull
docker compose up -d --build
```

## 🐛 Dépannage

### L'application ne démarre pas

```bash
# Vérifier les logs
sudo journalctl -u faxcloud-analyzer -n 50

# Tester manuellement
cd /opt/faxcloud-analyzer
sudo -u faxcloud ./venv/bin/python main.py
```

### Port déjà utilisé

```bash
# Trouver le processus utilisant le port
sudo lsof -i :8000

# Tuer le processus si nécessaire
sudo kill -9 <PID>
```

### Problèmes de permissions

```bash
# Réinitialiser les permissions
sudo chown -R faxcloud:faxcloud /opt/faxcloud-analyzer
sudo chmod -R 755 /opt/faxcloud-analyzer
```

### Mémoire insuffisante

```bash
# Voir l'utilisation mémoire
free -h

# Augmenter le swap
sudo dphys-swapfile swapoff
sudo sed -i 's/CONF_SWAPSIZE=.*/CONF_SWAPSIZE=2048/' /etc/dphys-swapfile
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

## 📁 Structure des fichiers sur le Pi

```
/opt/faxcloud-analyzer/
├── main.py              # Point d'entrée CLI
├── requirements.txt     # Dépendances Python
├── docker-compose.yml   # Configuration Docker
├── Dockerfile           # Image Docker
├── venv/                # Environnement Python
├── src/                 # Code source
├── web/                 # Interface web
├── data/                # Données (persistantes)
│   ├── imports/         # Fichiers CSV/XLSX importés
│   ├── reports/         # Rapports JSON générés
│   └── reports_qr/      # QR codes
├── database/            # Base SQLite
└── logs/                # Logs applicatifs
```

## 📞 Support

En cas de problème, vérifiez:
1. Les logs: `sudo journalctl -u faxcloud-analyzer -f`
2. L'état du service: `sudo systemctl status faxcloud-analyzer`
3. L'espace disque: `df -h`
4. La mémoire: `free -h`
