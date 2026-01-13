#!/bin/bash
#########################################################
# FaxCloud Analyzer - Script d'installation AUTOMATIQUE
# Compatible: Raspberry Pi 3/4/5 (ARM64) / Debian / Ubuntu
# 
# Ce script installe TOUT automatiquement:
# - Docker & Docker Compose
# - L'application FaxCloud Analyzer
# - Le service systemd pour démarrage auto
#
# Usage: sudo ./install.sh [--no-start]
#########################################################

set -e

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# Configuration
APP_NAME="faxcloud-analyzer"
APP_DIR="/opt/$APP_NAME"
APP_USER="faxcloud"
APP_PORT=8000
AUTO_START=true

# Parse arguments
for arg in "$@"; do
    case $arg in
        --no-start)
            AUTO_START=false
            shift
            ;;
    esac
done

# Fonctions d'affichage
step() {
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}${BOLD}▶ $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

success() {
    echo -e "   ${GREEN}✓ $1${NC}"
}

warn() {
    echo -e "   ${YELLOW}⚠ $1${NC}"
}

error_exit() {
    echo -e "\n${RED}❌ ERREUR: $1${NC}"
    exit 1
}

#########################################################
# VÉRIFICATIONS PRÉLIMINAIRES
#########################################################
clear

# Banner ASCII
echo -e "${CYAN}"
cat << 'EOF'
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║   ███████╗ █████╗ ██╗  ██╗ ██████╗██╗      ██████╗ ██╗   ██╗██████╗       ║
║   ██╔════╝██╔══██╗╚██╗██╔╝██╔════╝██║     ██╔═══██╗██║   ██║██╔══██╗      ║
║   █████╗  ███████║ ╚███╔╝ ██║     ██║     ██║   ██║██║   ██║██║  ██║      ║
║   ██╔══╝  ██╔══██║ ██╔██╗ ██║     ██║     ██║   ██║██║   ██║██║  ██║      ║
║   ██║     ██║  ██║██╔╝ ██╗╚██████╗███████╗╚██████╔╝╚██████╔╝██████╔╝      ║
║   ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚══════╝ ╚═════╝  ╚═════╝ ╚═════╝       ║
║                                                                           ║
║                    🏥 ANALYZER - Installation v1.2.0                      ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo -e "${BOLD}Installation automatique de FaxCloud Analyzer${NC}"
echo -e "Cette opération va installer Docker et l'application.\n"

# Vérifier root
if [ "$EUID" -ne 0 ]; then
    error_exit "Ce script doit être exécuté en tant que root (sudo)"
fi

# Détecter l'OS et l'architecture
OS=$(cat /etc/os-release 2>/dev/null | grep "^ID=" | cut -d= -f2 | tr -d '"')
ARCH=$(uname -m)

echo -e "${BOLD}📋 Système détecté:${NC}"
echo "   OS: $OS"
echo "   Architecture: $ARCH"
echo ""

# Obtenir le répertoire du script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

#########################################################
# ÉTAPE 1: Mise à jour du système
#########################################################
step "1/11 - Mise à jour du système"

export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get upgrade -y -qq
success "Système mis à jour"

#########################################################
# ÉTAPE 2: Installation des dépendances
#########################################################
step "2/11 - Installation des dépendances"

apt-get install -y -qq \
    curl \
    wget \
    git \
    ca-certificates \
    gnupg \
    lsb-release \
    jq \
    htop \
    > /dev/null 2>&1

success "Dépendances installées"

#########################################################
# ÉTAPE 3: Installation de Docker
#########################################################
step "3/11 - Installation de Docker"

if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version | grep -oP '\d+\.\d+\.\d+')
    success "Docker déjà installé (v$DOCKER_VERSION)"
else
    echo "   Installation de Docker..."
    
    # Supprimer anciennes versions
    apt-get remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true
    
    # Ajouter le repo Docker
    install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/$OS/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg 2>/dev/null
    chmod a+r /etc/apt/keyrings/docker.gpg
    
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/$OS $(lsb_release -cs) stable" | \
        tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Installer Docker
    apt-get update -qq
    apt-get install -y -qq docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin > /dev/null 2>&1
    
    # Démarrer Docker
    systemctl enable docker
    systemctl start docker
    
    success "Docker installé avec succès"
fi

#########################################################
# ÉTAPE 4: Installation de Docker Compose
#########################################################
step "4/11 - Vérification de Docker Compose"

if docker compose version &> /dev/null; then
    COMPOSE_VERSION=$(docker compose version --short 2>/dev/null)
    success "Docker Compose disponible (v$COMPOSE_VERSION)"
elif command -v docker-compose &> /dev/null; then
    COMPOSE_VERSION=$(docker-compose --version | grep -oP '\d+\.\d+\.\d+')
    success "Docker Compose (legacy) disponible (v$COMPOSE_VERSION)"
else
    echo "   Installation de Docker Compose standalone..."
    COMPOSE_URL="https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)"
    curl -SL "$COMPOSE_URL" -o /usr/local/bin/docker-compose 2>/dev/null
    chmod +x /usr/local/bin/docker-compose
    success "Docker Compose installé"
fi

#########################################################
# ÉTAPE 5: Création de l'utilisateur
#########################################################
step "5/11 - Configuration utilisateur"

if id "$APP_USER" &>/dev/null; then
    success "Utilisateur $APP_USER existe déjà"
else
    useradd -r -s /bin/false -d "$APP_DIR" "$APP_USER"
    success "Utilisateur $APP_USER créé"
fi

# Ajouter au groupe docker
usermod -aG docker "$APP_USER" 2>/dev/null || true
success "Permissions Docker configurées"

#########################################################
# ÉTAPE 6: Création des répertoires
#########################################################
step "6/11 - Création des répertoires"

mkdir -p "$APP_DIR"
mkdir -p "$APP_DIR/data/imports"
mkdir -p "$APP_DIR/data/reports"
mkdir -p "$APP_DIR/data/reports_qr"
mkdir -p "$APP_DIR/database"
mkdir -p "$APP_DIR/logs"

success "Structure des répertoires créée"

#########################################################
# ÉTAPE 7: Copie des fichiers
#########################################################
step "7/11 - Installation de l'application"

if [ -f "$PROJECT_DIR/main.py" ]; then
    # Copier tous les fichiers du projet
    cp -r "$PROJECT_DIR"/* "$APP_DIR/" 2>/dev/null || true
    
    # Ne pas écraser les données existantes
    rm -rf "$APP_DIR/raspberry-pi"
    
    success "Fichiers de l'application copiés"
else
    error_exit "Fichier main.py non trouvé. Exécutez ce script depuis le dossier du projet."
fi

# Configurer les permissions
chown -R "$APP_USER:$APP_USER" "$APP_DIR"
chmod -R 755 "$APP_DIR"
chmod 777 "$APP_DIR/data" "$APP_DIR/database" "$APP_DIR/logs"

success "Permissions configurées"

#########################################################
# ÉTAPE 8: Construction de l'image Docker
#########################################################
step "8/11 - Construction de l'image Docker"

cd "$APP_DIR"

# Construire l'image
echo "   Construction en cours... (cela peut prendre quelques minutes)"
docker build -t faxcloud-analyzer:latest . > /dev/null 2>&1

success "Image Docker construite"

#########################################################
# ÉTAPE 9: Installation du service systemd
#########################################################
step "9/11 - Configuration du service systemd"

cat > /etc/systemd/system/faxcloud-analyzer.service << EOF
[Unit]
Description=FaxCloud Analyzer - Analyseur de consommation
Documentation=https://github.com/faxcloud/analyzer
After=docker.service network-online.target
Requires=docker.service
Wants=network-online.target

[Service]
Type=simple
User=root
WorkingDirectory=$APP_DIR
Environment="COMPOSE_PROJECT_NAME=faxcloud"

# Arrêter proprement avant de démarrer
ExecStartPre=-/usr/bin/docker compose down --remove-orphans

# Démarrer l'application
ExecStart=/usr/bin/docker compose up

# Arrêt propre
ExecStop=/usr/bin/docker compose down

# Redémarrage automatique
Restart=always
RestartSec=10
TimeoutStartSec=300
TimeoutStopSec=30

# Logs
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable faxcloud-analyzer

success "Service systemd installé et activé"

#########################################################
# ÉTAPE 10: Configuration du pare-feu
#########################################################
step "10/11 - Configuration du pare-feu"

if command -v ufw &> /dev/null; then
    ufw allow $APP_PORT/tcp > /dev/null 2>&1 || true
    success "Port $APP_PORT ouvert (UFW)"
elif command -v firewall-cmd &> /dev/null; then
    firewall-cmd --permanent --add-port=$APP_PORT/tcp > /dev/null 2>&1 || true
    firewall-cmd --reload > /dev/null 2>&1 || true
    success "Port $APP_PORT ouvert (firewalld)"
else
    warn "Aucun pare-feu détecté - assurez-vous que le port $APP_PORT est accessible"
fi

#########################################################
# ÉTAPE 11: Démarrage de l'application
#########################################################
if [ "$AUTO_START" = true ]; then
    step "11/11 - Démarrage de l'application"
    
    systemctl start faxcloud-analyzer
    
    echo "   Attente du démarrage de l'application..."
    sleep 5
    
    # Vérifier que l'application répond
    HEALTH_OK=false
    for i in {1..30}; do
        if curl -s http://localhost:$APP_PORT/api/health > /dev/null 2>&1; then
            HEALTH_OK=true
            break
        fi
        sleep 2
    done
    
    if [ "$HEALTH_OK" = true ]; then
        success "Application démarrée et accessible"
    else
        warn "L'application démarre encore... Vérifiez dans quelques secondes"
    fi
else
    step "11/11 - Application prête (non démarrée)"
    warn "Démarrez manuellement avec: sudo systemctl start faxcloud-analyzer"
fi

#########################################################
# RÉSUMÉ FINAL
#########################################################
IP_ADDR=$(hostname -I | awk '{print $1}')

echo ""
echo -e "${GREEN}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║   ✅  INSTALLATION TERMINÉE AVEC SUCCÈS !                   ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${BOLD}📋 Informations:${NC}"
echo "   ┌─────────────────────────────────────────────────────────┐"
echo "   │  Application:  FaxCloud Analyzer v1.2.0                 │"
echo "   │  Répertoire:   $APP_DIR"
echo "   │  Port:         $APP_PORT                                     │"
echo "   │  URL locale:   http://localhost:$APP_PORT                   │"
echo "   │  URL réseau:   http://$IP_ADDR:$APP_PORT"
echo "   └─────────────────────────────────────────────────────────┘"
echo ""

echo -e "${BOLD}🔧 Commandes utiles:${NC}"
echo "   ┌─────────────────────────────────────────────────────────┐"
echo "   │  Statut:       sudo systemctl status faxcloud-analyzer  │"
echo "   │  Logs:         sudo journalctl -u faxcloud-analyzer -f  │"
echo "   │  Redémarrer:   sudo systemctl restart faxcloud-analyzer │"
echo "   │  Arrêter:      sudo systemctl stop faxcloud-analyzer    │"
echo "   │  Docker logs:  cd $APP_DIR && docker compose logs -f    │"
echo "   └─────────────────────────────────────────────────────────┘"
echo ""

echo -e "${CYAN}🌐 Ouvrez votre navigateur:${NC}"
echo -e "   ${BOLD}http://$IP_ADDR:$APP_PORT${NC}"
echo ""

# Test final
if curl -s http://localhost:$APP_PORT/api/health 2>/dev/null | jq -e '.status == "healthy"' > /dev/null 2>&1; then
    echo -e "${GREEN}✓ L'application fonctionne correctement!${NC}"
else
    if [ "$AUTO_START" = true ]; then
        warn "L'application est en cours de démarrage..."
        echo "   Vérifiez avec: curl http://localhost:$APP_PORT/api/health"
    fi
fi

echo ""
echo -e "${CYAN}Merci d'utiliser FaxCloud Analyzer! 🎉${NC}"
echo ""
