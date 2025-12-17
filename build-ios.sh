#!/bin/bash
# Script pour automatiser le build iOS avec GitHub Actions
# Usage: ./build-ios.sh "Votre message de commit"

set -e

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Navigation
cd "$(dirname "$0")"

echo -e "${BLUE}🚀 FaxCloud iOS Build Script${NC}"
echo -e "${BLUE}================================${NC}\n"

# Vérifier Git
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git n'est pas installé${NC}"
    exit 1
fi

# Message de commit
COMMIT_MESSAGE="${1:-'chore: Build iOS app'}"

echo -e "${YELLOW}📝 Préparation du build...${NC}\n"

# Vérifier le status
echo "📊 Status Git:"
git status --short

# Ajouter les changements
echo -e "\n${YELLOW}📦 Ajout des changements...${NC}"
git add .

# Commit
echo -e "\n${YELLOW}💾 Commit: $COMMIT_MESSAGE${NC}"
git commit -m "$COMMIT_MESSAGE" || echo "Aucun changement à committer"

# Push
echo -e "\n${YELLOW}⬆️  Push vers GitHub...${NC}"
git push origin main || git push -u origin main

# Afficher le lien
REPO_URL=$(git config --get remote.origin.url)
REPO_NAME=$(basename "$REPO_URL" .git)
REPO_OWNER=$(git config --get remote.origin.url | grep -oP 'github.com/\K[^/]*')

echo -e "\n${GREEN}✅ Code poussé avec succès!${NC}\n"
echo -e "${BLUE}🔍 Voir le build:${NC}"
echo "   https://github.com/$REPO_OWNER/$REPO_NAME/actions"

echo -e "\n${GREEN}⏱️  Le build démarre automatiquement...${NC}"
echo -e "${YELLOW}⏳ Attendez 5-10 minutes pour la compilation${NC}\n"

echo -e "${BLUE}📥 Pour télécharger l'app:${NC}"
echo "   1. Allez sur le lien ci-dessus"
echo "   2. Cliquez sur 'Build iOS App'"
echo "   3. Cliquez sur votre build (en vert si succès)"
echo "   4. Scroll down pour 'Artifacts'"
echo "   5. Téléchargez 'FaxCloudAnalyzer.ipa'\n"

echo -e "${GREEN}🎉 C'est tout! Votre app iOS est en cours de build!${NC}"
