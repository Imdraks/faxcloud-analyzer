#!/bin/bash
#########################################################
# FaxCloud Analyzer - Script de sauvegarde
# Sauvegarde les données et la base de données
#########################################################

set -e

APP_DIR="/opt/faxcloud-analyzer"
BACKUP_DIR="${1:-$HOME/faxcloud-backups}"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="faxcloud-backup-$DATE"

echo "💾 Sauvegarde FaxCloud Analyzer"
echo "================================"

# Créer le répertoire de backup
mkdir -p "$BACKUP_DIR"

# Créer l'archive
echo "📦 Création de l'archive..."
tar -czf "$BACKUP_DIR/$BACKUP_NAME.tar.gz" \
    -C "$APP_DIR" \
    data \
    database \
    --exclude='*.pyc' \
    --exclude='__pycache__'

# Vérifier la taille
SIZE=$(du -h "$BACKUP_DIR/$BACKUP_NAME.tar.gz" | cut -f1)
echo "✅ Sauvegarde créée: $BACKUP_DIR/$BACKUP_NAME.tar.gz ($SIZE)"

# Nettoyer les anciennes sauvegardes (garder les 7 dernières)
echo "🧹 Nettoyage des anciennes sauvegardes..."
ls -t "$BACKUP_DIR"/faxcloud-backup-*.tar.gz 2>/dev/null | tail -n +8 | xargs -r rm

echo ""
echo "📋 Sauvegardes disponibles:"
ls -lh "$BACKUP_DIR"/faxcloud-backup-*.tar.gz 2>/dev/null || echo "Aucune"

echo ""
echo "💡 Pour restaurer: tar -xzf $BACKUP_DIR/$BACKUP_NAME.tar.gz -C $APP_DIR"
