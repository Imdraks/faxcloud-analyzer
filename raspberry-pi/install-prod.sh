#!/bin/bash
#########################################################
# FaxCloud Analyzer - Installation Production avec Traefik
# Accès via nom de domaine + HTTPS automatique
#########################################################

set -e

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║   FaxCloud Analyzer - Configuration Production            ║"
echo "║   Avec Traefik + Let's Encrypt (HTTPS)                    ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Vérifier root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Ce script doit être exécuté en tant que root (sudo)"
    exit 1
fi

# Demander le domaine
read -p "Votre nom de domaine (ex: faxanalyser.fr): " DOMAIN
read -p "Votre email (pour Let's Encrypt): " EMAIL

# Créer le fichier .env
cat > .env << EOF
DOMAIN=$DOMAIN
ACME_EMAIL=$EMAIL
TZ=Europe/Paris
EOF

echo -e "\n${BLUE}▶ Création des répertoires...${NC}"
mkdir -p traefik/config
mkdir -p data/imports data/reports data/reports_qr
mkdir -p database logs

# Créer le fichier acme.json pour les certificats
touch traefik/acme.json
chmod 600 traefik/acme.json

echo -e "${GREEN}✓ Répertoires créés${NC}"

echo -e "\n${BLUE}▶ Création de la configuration Traefik...${NC}"

# Configuration Traefik
cat > traefik/traefik.yml << 'EOF'
api:
  dashboard: true
  insecure: false

entryPoints:
  web:
    address: ":80"
  websecure:
    address: ":443"

certificatesResolvers:
  letsencrypt:
    acme:
      email: "${ACME_EMAIL}"
      storage: /acme.json
      httpChallenge:
        entryPoint: web

providers:
  docker:
    endpoint: "unix:///var/run/docker.sock"
    exposedByDefault: false
    network: web

log:
  level: INFO
EOF

# Remplacer l'email
sed -i "s/\${ACME_EMAIL}/$EMAIL/" traefik/traefik.yml

echo -e "${GREEN}✓ Configuration Traefik créée${NC}"

echo -e "\n${BLUE}▶ Démarrage des conteneurs...${NC}"

# Arrêter les anciens conteneurs
docker compose -f docker-compose.prod.yml down 2>/dev/null || true

# Démarrer avec la config production
docker compose -f docker-compose.prod.yml --env-file .env up -d --build

echo -e "${GREEN}✓ Conteneurs démarrés${NC}"

# Attendre le démarrage
echo -e "\n${BLUE}▶ Attente du démarrage...${NC}"
sleep 10

# Vérification
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗"
echo -e "║   ✅  INSTALLATION TERMINÉE !                                ║"
echo -e "╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}Votre application est accessible à :${NC}"
echo -e "   ${YELLOW}https://$DOMAIN${NC}"
echo ""
echo -e "${BLUE}📋 Prochaines étapes :${NC}"
echo "   1. Configurez votre DNS pour pointer vers ce serveur"
echo "   2. Attendez quelques minutes pour le certificat SSL"
echo ""
echo -e "${BLUE}🔧 Commandes utiles :${NC}"
echo "   Logs:      docker compose -f docker-compose.prod.yml logs -f"
echo "   Statut:    docker compose -f docker-compose.prod.yml ps"
echo "   Arrêter:   docker compose -f docker-compose.prod.yml down"
echo ""
