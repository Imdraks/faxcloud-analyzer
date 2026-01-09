#!/bin/bash
#########################################################
# FaxCloud Analyzer - Script de déploiement rapide
# Usage: ./deploy.sh [docker|native]
#########################################################

set -e

MODE="${1:-docker}"
APP_DIR="/opt/faxcloud-analyzer"

echo "🚀 Déploiement FaxCloud Analyzer (mode: $MODE)"

# Arrêter le service actuel
if systemctl is-active --quiet faxcloud-analyzer; then
    echo "⏹️  Arrêt du service..."
    sudo systemctl stop faxcloud-analyzer
fi

if systemctl is-active --quiet faxcloud-analyzer-docker; then
    echo "⏹️  Arrêt du service Docker..."
    sudo systemctl stop faxcloud-analyzer-docker
fi

# Mise à jour des fichiers
if [ -d ".git" ]; then
    echo "📥 Mise à jour depuis Git..."
    git pull
fi

# Copier vers le répertoire d'installation
echo "📁 Mise à jour des fichiers..."
sudo cp -r src web main.py requirements.txt Dockerfile docker-compose.yml "$APP_DIR/"

if [ "$MODE" = "docker" ]; then
    echo "🐳 Construction de l'image Docker..."
    cd "$APP_DIR"
    sudo docker compose build
    
    echo "▶️  Démarrage du conteneur..."
    sudo docker compose up -d
    
    echo "✅ Déploiement Docker terminé!"
    sudo docker compose ps
else
    echo "🐍 Mise à jour des dépendances Python..."
    cd "$APP_DIR"
    sudo -u faxcloud ./venv/bin/pip install -r requirements.txt
    
    echo "▶️  Démarrage du service..."
    sudo systemctl start faxcloud-analyzer
    
    echo "✅ Déploiement natif terminé!"
    sudo systemctl status faxcloud-analyzer --no-pager
fi

IP=$(hostname -I | awk '{print $1}')
echo ""
echo "🌐 Application disponible sur: http://$IP:8000"
