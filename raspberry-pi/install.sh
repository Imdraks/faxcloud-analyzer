#!/bin/bash
#########################################################
# FaxCloud Analyzer - Script d'installation Raspberry Pi
# Compatible: Raspberry Pi 3/4/5 (ARM64)
# OS: Raspberry Pi OS (64-bit) / Debian / Ubuntu
#########################################################

set -e

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="faxcloud-analyzer"
APP_DIR="/opt/$APP_NAME"
APP_USER="faxcloud"
APP_PORT=8000

echo -e "${BLUE}"
echo "=========================================="
echo "  FaxCloud Analyzer - Installation Pi    "
echo "=========================================="
echo -e "${NC}"

# Vérification root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}❌ Ce script doit être exécuté en root (sudo)${NC}"
    exit 1
fi

# Vérification architecture
ARCH=$(uname -m)
echo -e "${YELLOW}📋 Architecture détectée: $ARCH${NC}"

if [[ "$ARCH" != "aarch64" && "$ARCH" != "arm64" && "$ARCH" != "armv7l" ]]; then
    echo -e "${YELLOW}⚠️  Architecture non-ARM détectée. Ce script est optimisé pour Raspberry Pi.${NC}"
    read -p "Continuer quand même? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo -e "${GREEN}✓ Vérifications préliminaires OK${NC}"

# Mise à jour système
echo -e "\n${BLUE}📦 Mise à jour du système...${NC}"
apt-get update -qq
apt-get upgrade -y -qq

# Installation des dépendances système
echo -e "\n${BLUE}📦 Installation des dépendances système...${NC}"
apt-get install -y -qq \
    python3 \
    python3-pip \
    python3-venv \
    git \
    curl \
    wget \
    libffi-dev \
    libssl-dev \
    build-essential

# Option: Installation Docker (recommandé)
echo -e "\n${YELLOW}❓ Voulez-vous installer Docker (recommandé)? (y/n)${NC}"
read -p "" -n 1 -r INSTALL_DOCKER
echo

if [[ $INSTALL_DOCKER =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}🐳 Installation de Docker...${NC}"
    
    if ! command -v docker &> /dev/null; then
        curl -fsSL https://get.docker.com -o get-docker.sh
        sh get-docker.sh
        rm get-docker.sh
        
        # Ajouter l'utilisateur pi au groupe docker
        usermod -aG docker pi 2>/dev/null || true
        
        # Installer docker-compose
        apt-get install -y -qq docker-compose-plugin || pip3 install docker-compose
        
        echo -e "${GREEN}✓ Docker installé avec succès${NC}"
    else
        echo -e "${GREEN}✓ Docker est déjà installé${NC}"
    fi
fi

# Création de l'utilisateur application
echo -e "\n${BLUE}👤 Configuration de l'utilisateur...${NC}"
if ! id "$APP_USER" &>/dev/null; then
    useradd -r -s /bin/false -d "$APP_DIR" "$APP_USER"
    echo -e "${GREEN}✓ Utilisateur $APP_USER créé${NC}"
else
    echo -e "${GREEN}✓ Utilisateur $APP_USER existe déjà${NC}"
fi

# Création du répertoire d'installation
echo -e "\n${BLUE}📁 Création des répertoires...${NC}"
mkdir -p "$APP_DIR"
mkdir -p "$APP_DIR/data/imports"
mkdir -p "$APP_DIR/data/reports"
mkdir -p "$APP_DIR/data/reports_qr"
mkdir -p "$APP_DIR/database"
mkdir -p "$APP_DIR/logs"

# Copie des fichiers (si exécuté depuis le répertoire du projet)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

if [ -f "$PROJECT_DIR/main.py" ]; then
    echo -e "${BLUE}📄 Copie des fichiers du projet...${NC}"
    cp -r "$PROJECT_DIR"/* "$APP_DIR/"
    echo -e "${GREEN}✓ Fichiers copiés${NC}"
fi

# Configuration des permissions
chown -R "$APP_USER:$APP_USER" "$APP_DIR"
chmod -R 755 "$APP_DIR"

# Installation des dépendances Python (si pas Docker)
if [[ ! $INSTALL_DOCKER =~ ^[Yy]$ ]]; then
    echo -e "\n${BLUE}🐍 Installation de l'environnement Python...${NC}"
    cd "$APP_DIR"
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    pip install gunicorn
    deactivate
    echo -e "${GREEN}✓ Environnement Python configuré${NC}"
fi

# Installation du service systemd
echo -e "\n${BLUE}⚙️  Installation du service systemd...${NC}"
cat > /etc/systemd/system/faxcloud-analyzer.service << EOF
[Unit]
Description=FaxCloud Analyzer Web Service
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=$APP_USER
Group=$APP_USER
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin:/usr/local/bin:/usr/bin:/bin"
Environment="PYTHONUNBUFFERED=1"
ExecStart=$APP_DIR/venv/bin/gunicorn --bind 0.0.0.0:$APP_PORT --workers 2 --threads 2 --timeout 120 src.wsgi:app
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=10

# Sécurité
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$APP_DIR/data $APP_DIR/database $APP_DIR/logs

[Install]
WantedBy=multi-user.target
EOF

# Service Docker (alternative)
cat > /etc/systemd/system/faxcloud-analyzer-docker.service << EOF
[Unit]
Description=FaxCloud Analyzer (Docker)
After=docker.service
Requires=docker.service

[Service]
Type=simple
WorkingDirectory=$APP_DIR
ExecStartPre=-/usr/bin/docker compose down
ExecStart=/usr/bin/docker compose up
ExecStop=/usr/bin/docker compose down
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Rechargement systemd
systemctl daemon-reload

echo -e "${GREEN}✓ Services systemd installés${NC}"

# Configuration du pare-feu (optionnel)
echo -e "\n${YELLOW}❓ Voulez-vous ouvrir le port $APP_PORT dans le pare-feu? (y/n)${NC}"
read -p "" -n 1 -r OPEN_FIREWALL
echo

if [[ $OPEN_FIREWALL =~ ^[Yy]$ ]]; then
    if command -v ufw &> /dev/null; then
        ufw allow $APP_PORT/tcp
        echo -e "${GREEN}✓ Port $APP_PORT ouvert (UFW)${NC}"
    elif command -v firewall-cmd &> /dev/null; then
        firewall-cmd --permanent --add-port=$APP_PORT/tcp
        firewall-cmd --reload
        echo -e "${GREEN}✓ Port $APP_PORT ouvert (firewalld)${NC}"
    else
        echo -e "${YELLOW}⚠️  Aucun pare-feu détecté${NC}"
    fi
fi

# Résumé final
echo -e "\n${GREEN}"
echo "=========================================="
echo "  ✅ Installation terminée avec succès!  "
echo "=========================================="
echo -e "${NC}"

IP_ADDR=$(hostname -I | awk '{print $1}')

echo -e "${BLUE}📋 Résumé:${NC}"
echo "   • Répertoire: $APP_DIR"
echo "   • Port: $APP_PORT"
echo "   • URL: http://$IP_ADDR:$APP_PORT"
echo ""

if [[ $INSTALL_DOCKER =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}🐳 Pour démarrer avec Docker:${NC}"
    echo "   cd $APP_DIR"
    echo "   docker compose up -d"
    echo ""
    echo "   Ou avec systemd:"
    echo "   sudo systemctl enable faxcloud-analyzer-docker"
    echo "   sudo systemctl start faxcloud-analyzer-docker"
else
    echo -e "${YELLOW}🚀 Pour démarrer le service:${NC}"
    echo "   sudo systemctl enable faxcloud-analyzer"
    echo "   sudo systemctl start faxcloud-analyzer"
    echo ""
    echo "   Vérifier le statut:"
    echo "   sudo systemctl status faxcloud-analyzer"
fi

echo ""
echo -e "${BLUE}📊 Commandes utiles:${NC}"
echo "   • Voir les logs: sudo journalctl -u faxcloud-analyzer -f"
echo "   • Redémarrer: sudo systemctl restart faxcloud-analyzer"
echo "   • Arrêter: sudo systemctl stop faxcloud-analyzer"
echo ""
