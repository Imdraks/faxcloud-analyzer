#!/bin/bash
#########################################################
# FaxCloud Analyzer - Script de MISE À JOUR
# Met à jour l'application sans perdre les données
#
# Usage: sudo ./update.sh
#########################################################

set -e

# Couleurs
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
APP_PORT=8000

echo -e "${CYAN}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║       FaxCloud Analyzer - Mise à jour v1.2.0              ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Vérifier root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}❌ Ce script doit être exécuté en tant que root (sudo)${NC}"
    exit 1
fi

# Vérifier que l'application est installée
if [ ! -d "$APP_DIR" ]; then
    echo -e "${RED}❌ L'application n'est pas installée dans $APP_DIR${NC}"
    echo "   Utilisez install.sh pour une première installation."
    exit 1
fi

# Obtenir le répertoire du script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}▶ Arrêt de l'application...${NC}"
systemctl stop faxcloud-analyzer 2>/dev/null || true
sleep 2
echo -e "${GREEN}✓ Application arrêtée${NC}"

echo -e "\n${BLUE}▶ Sauvegarde des données...${NC}"
BACKUP_DIR="/tmp/faxcloud-backup-$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -r "$APP_DIR/data" "$BACKUP_DIR/" 2>/dev/null || true
cp -r "$APP_DIR/database" "$BACKUP_DIR/" 2>/dev/null || true
echo -e "${GREEN}✓ Données sauvegardées dans $BACKUP_DIR${NC}"

echo -e "\n${BLUE}▶ Mise à jour des fichiers...${NC}"
# Copier les nouveaux fichiers (sans écraser data et database)
rsync -av --exclude='data/' --exclude='database/' --exclude='logs/' --exclude='.git/' --exclude='__pycache__/' --exclude='.venv/' --exclude='raspberry-pi/' "$PROJECT_DIR/" "$APP_DIR/" > /dev/null 2>&1 || \
cp -r "$PROJECT_DIR"/{src,web,main.py,requirements.txt,Dockerfile,docker-compose.yml} "$APP_DIR/" 2>/dev/null
echo -e "${GREEN}✓ Fichiers mis à jour${NC}"

echo -e "\n${BLUE}▶ Reconstruction de l'image Docker...${NC}"
cd "$APP_DIR"
docker build -t faxcloud-analyzer:latest . > /dev/null 2>&1
echo -e "${GREEN}✓ Image Docker reconstruite${NC}"

echo -e "\n${BLUE}▶ Redémarrage de l'application...${NC}"
systemctl start faxcloud-analyzer
sleep 3

# Vérifier le health check
for i in {1..15}; do
    if curl -s http://localhost:$APP_PORT/api/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Application redémarrée${NC}"
        break
    fi
    sleep 2
done

# Résumé
IP_ADDR=$(hostname -I | awk '{print $1}')
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗"
echo -e "║   ✅  MISE À JOUR TERMINÉE !                                 ║"
echo -e "╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "   URL: ${BOLD}http://$IP_ADDR:$APP_PORT${NC}"
echo ""

# Test final
if curl -s http://localhost:$APP_PORT/api/health 2>/dev/null | grep -q "healthy"; then
    echo -e "${GREEN}✓ L'application fonctionne correctement!${NC}"
else
    echo -e "${YELLOW}⚠ Vérifiez le statut: sudo systemctl status faxcloud-analyzer${NC}"
fi
echo ""
