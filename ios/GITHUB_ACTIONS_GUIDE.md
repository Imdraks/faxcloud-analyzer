# GitHub Actions iOS Build Guide

## 📱 Builder iOS sur le Cloud (Sans Mac Local!)

Ce guide vous montre comment utiliser **GitHub Actions** pour builder votre app iOS automatiquement.

---

## 🚀 Configuration Rapide (5 minutes)

### Étape 1: Préparer votre dépôt GitHub

```powershell
# Assurez-vous que le code est sur GitHub
cd c:\Users\VOXCL\Documents\GitHub\faxcloud-analyzer

# Vérifiez le remote
git remote -v

# Si pas de remote, ajoutez:
git remote add origin https://github.com/VOTRE_USERNAME/faxcloud-analyzer.git
git branch -M main
git push -u origin main
```

### Étape 2: Le workflow est déjà créé!

Le fichier `.github/workflows/build-ios.yml` est prêt. Il va:
- ✅ Trigger automatiquement à chaque `push` sur `main` ou `develop`
- ✅ Builder sur un serveur macOS d'Apple
- ✅ Créer un fichier `.ipa` (l'app iOS)
- ✅ Sauvegarder en tant qu'artefact

### Étape 3: Déclencher le Build

**Option A - Automatique (Recommandé):**
```powershell
# Commitez et pushez votre code
git add .
git commit -m "feat: Initial iOS app"
git push origin main

# Le build démarre automatiquement!
# Allez voir: GitHub > Actions > Workflows
```

**Option B - Manuel:**
- Allez sur GitHub.com
- Cliquez "Actions"
- Cliquez "Build iOS App"
- Cliquez "Run workflow"

---

## 📊 Voir le Résultat du Build

### Sur GitHub:

1. **Allez sur votre repo**: https://github.com/VOTRE_USERNAME/faxcloud-analyzer
2. **Cliquez sur "Actions"** (onglet du haut)
3. **Voyez le build en cours:**
   - 🟡 Yellow = En cours
   - 🟢 Green = Succès
   - 🔴 Red = Erreur

### Récupérer l'app compilée:

```
1. Allez dans Actions > Build iOS App > [votre build]
2. Scroll down pour "Artifacts"
3. Téléchargez "FaxCloudAnalyzer.ipa"
4. C'est votre app iOS prête à tester!
```

---

## 📥 Installer l'app sur iPhone

### Via l'IPA téléchargée:

**Option 1: Avec Finder (Mac)**
```powershell
# L'app .ipa peut être glissée dans Finder sur Mac
# Puis synchronisée vers iPhone
```

**Option 2: Avec Apple Configurator (Windows/Mac)**
- Téléchargez Apple Configurator 2
- Connectez iPhone
- Glissez-déposez l'IPA
- L'app s'installe automatiquement

**Option 3: Via TestFlight (Recommandé)**
- Inscrivez-vous à Apple Developer ($99/an)
- Uploadez l'IPA sur App Store Connect
- Partagez le lien TestFlight avec testeurs
- Ils installent via l'app TestFlight

---

## 🔧 Configuration Avancée

### Authentification avec Apple

Pour la signature automatique (optionnel):

1. **Créez un App Store Connect API Key:**
   - https://appstoreconnect.apple.com/access/api

2. **Ajoutez les secrets GitHub:**
   - Settings > Secrets and variables > Actions
   - Ajoutez `APPLE_API_KEY_ID`, `APPLE_API_KEY_ISSUER_ID`, `APPLE_API_KEY_CONTENT`

3. **Mettez à jour le workflow** pour utiliser ces secrets

### Build sur demande

Le workflow actuellement déclenche sur chaque `push`. Pour changer:

```yaml
on:
  workflow_dispatch:  # Seulement manuel
  push:
    branches:
      - main
      - develop
  schedule:
    - cron: '0 2 * * 0'  # Chaque dimanche à 2h
```

---

## 📋 Commandes Locales (Optionnel)

Si vous avez un Mac ou une VM:

```powershell
# Lister les schemes disponibles
xcodebuild -list -project ios/FaxCloudAnalyzer.xcodeproj

# Builder localement
xcodebuild -workspace ios/FaxCloudAnalyzer.xcworkspace \
  -scheme FaxCloudAnalyzer \
  -configuration Release \
  -derivedDataPath build

# Créer l'archive
xcodebuild -workspace ios/FaxCloudAnalyzer.xcworkspace \
  -scheme FaxCloudAnalyzer \
  -archivePath build/FaxCloudAnalyzer.xcarchive \
  archive

# Exporter l'IPA
xcodebuild -exportArchive \
  -archivePath build/FaxCloudAnalyzer.xcarchive \
  -exportOptionsPlist ios/ExportOptions.plist \
  -exportPath ios/output
```

---

## 🐛 Troubleshooting

### ❌ Build échoue: "Pod install failed"

**Solution:**
```powershell
# Mettre à jour le workflow pour CocoaPods
cd ios
pod repo update
pod install
```

### ❌ Build échoue: "No provisioning profile"

**Solution:**
- Pour le CI/CD gratuit sans signing, utilisez `CODE_SIGN_IDENTITY=""` (déjà configuré)
- Ou inscrivez-vous à Apple Developer pour la signature automatique

### ❌ L'IPA ne s'installe pas

**Solutions:**
1. Vérifiez que le Bundle ID est correct
2. Vérifiez que iOS 16+ est installé
3. Utilisez Apple Configurator ou TestFlight

---

## ✅ Checklist

- [x] Fichier workflow `.github/workflows/build-ios.yml` créé
- [x] Fichier config `ios/ExportOptions.plist` créé
- [ ] Pushé le code vers GitHub
- [ ] Allez voir le build dans Actions
- [ ] Téléchargez l'IPA
- [ ] Testez l'installation sur iPhone

---

## 📊 Qu'est-ce qui se passe?

```
1. Vous pushez du code vers GitHub
   ↓
2. GitHub Actions détecte le push
   ↓
3. Loue une VM macOS chez Apple
   ↓
4. Installe Xcode et dépendances
   ↓
5. Compile votre code Swift
   ↓
6. Crée un fichier .ipa (l'app)
   ↓
7. Sauvegarde en tant qu'artefact
   ↓
8. Vous téléchargez et installez sur iPhone!
```

**Tout ça sans Mac local!** ✨

---

## 🔗 Ressources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [iOS App Building Guide](https://developer.apple.com/documentation/xcode/building-an-app-for-distribution)
- [TestFlight Documentation](https://developer.apple.com/testflight/)

---

## 💡 Astuces Pro

### Notification du build
Ajoutez dans votre `.github/workflows/build-ios.yml`:

```yaml
- name: Slack Notification
  if: always()
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    text: 'iOS Build ${{ job.status }}'
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### Test sur plusieurs iOS versions
```yaml
- name: Build for iOS 16
- name: Build for iOS 17
- name: Build for iOS 18
```

---

**Vous êtes prêt!** 🚀

Poussez votre code et regardez le magic se produire! ✨
