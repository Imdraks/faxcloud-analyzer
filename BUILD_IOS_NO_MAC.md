# 🚀 Builder iOS sans Mac avec GitHub Actions

## ⚡ Démarrage Rapide (2 minutes)

### Étape 1: Si votre code n'est pas sur GitHub

```powershell
cd c:\Users\VOXCL\Documents\GitHub\faxcloud-analyzer

# Créez un nouveau repo sur GitHub (https://github.com/new)
# Puis:

git remote add origin https://github.com/VOTRE_USERNAME/faxcloud-analyzer.git
git branch -M main
git push -u origin main
```

### Étape 2: Lancez le build!

**Sur Windows (PowerShell):**
```powershell
.\build-ios.ps1 -Message "feat: Initial iOS build"
```

**Sur Mac/Linux (Bash):**
```bash
./build-ios.sh "feat: Initial iOS build"
```

**Ou manuellement:**
```powershell
git add .
git commit -m "feat: Initial iOS build"
git push origin main
```

### Étape 3: Regardez le build!

1. Allez sur https://github.com/VOTRE_USERNAME/faxcloud-analyzer
2. Cliquez sur l'onglet **"Actions"**
3. Vous verrez **"Build iOS App"** en cours ⏳
4. Attendez 5-10 minutes...
5. Quand c'est vert ✅, votre app est prête!

---

## 📥 Récupérer l'app

### Via GitHub Artifacts (Gratuit!)

```
Actions > Build iOS App > [votre build]
                          ↓
                    Scroll down
                          ↓
                      Artifacts
                          ↓
        Cliquez "FaxCloudAnalyzer.ipa"
                          ↓
                    Téléchargé! ✅
```

### Installer sur iPhone

**Option 1: Avec Apple Configurator 2 (Recommandé)**
- Téléchargez: https://apps.apple.com/app/apple-configurator-2/id1037126344
- Connectez iPhone
- Glissez-déposez l'IPA
- Installez ✅

**Option 2: TestFlight (Pour partager)**
- Inscrivez-vous App Developer ($99/an)
- Uploadez sur App Store Connect
- Partagez le lien
- Testeurs installent via app TestFlight

---

## 📊 Workflow GitHub Actions Inclus

Le fichier `.github/workflows/build-ios.yml` fait:

✅ Builder automatiquement à chaque `git push`  
✅ Sur les serveurs macOS d'Apple (gratuit!)  
✅ Compile votre code Swift  
✅ Crée un fichier `.ipa` (app iOS)  
✅ Sauvegarde pour téléchargement  
✅ Fonctionne sans certificats (pour test)  

---

## 🎯 Cas d'Usage

### Vous êtes sur Windows
```powershell
# C'est votre solution! ✨
.\build-ios.ps1
```

### Vous êtes sur Mac (mais sans Xcode)
```bash
./build-ios.sh
```

### Vous avez Xcode
```bash
# Vous pouvez aussi builder localement:
xcodebuild -workspace ios/FaxCloudAnalyzer.xcworkspace \
  -scheme FaxCloudAnalyzer \
  -configuration Release
```

---

## 🔧 Fichiers Créés

```
.github/
└── workflows/
    └── build-ios.yml           ← Le workflow GitHub Actions

ios/
├── ExportOptions.plist         ← Config d'export iOS
└── GITHUB_ACTIONS_GUIDE.md     ← Documentation détaillée

build-ios.ps1                   ← Script PowerShell (Windows)
build-ios.sh                    ← Script Bash (Mac/Linux)
```

---

## 📋 Checklist

- [ ] Code pushé sur GitHub
- [ ] Allez voir Actions > Build iOS App
- [ ] Attendez le ✅ vert
- [ ] Téléchargez l'IPA
- [ ] Installez sur iPhone avec Apple Configurator
- [ ] Testez! 🎉

---

## ❓ FAQ

**Q: Pourquoi "unsigned"?**
A: Sans certificat Apple, l'app n'est pas signée. C'est normal pour le test. Pour App Store, il faut la signing certificate.

**Q: Combien ça coûte?**
A: GRATUIT! GitHub Actions offre 2000 min/mois gratuitement.

**Q: Ça fonctionne pour Android aussi?**
A: Oui! On peut ajouter un workflow pour Android. Demandez! 

**Q: Comment partager l'app avec d'autres?**
A: Via TestFlight (App Developer $99/an) ou App Store (après approbation).

**Q: Et les mises à jour?**
A: Chaque `git push` redéclenche un nouveau build automatiquement!

---

## 🚀 Commandes Utiles

```powershell
# Voir tout l'historique des builds
git log --oneline

# Voir le dernier build
git log -1

# Voir si le push est en place
git log --all --oneline

# Accéder au dossier du projet
cd c:\Users\VOXCL\Documents\GitHub\faxcloud-analyzer
```

---

## 💡 Pro Tips

### Build sur demande (sans push)

Sur GitHub:
1. Actions > Build iOS App
2. "Run workflow" > Run workflow

C'est plus rapide si vous testez juste!

### Notifications

Ajoutez un webhook Slack pour être notifié du succès/échec du build.

### Build programmé

Déclenchez un build tous les jours à 2h du matin:

```yaml
schedule:
  - cron: '0 2 * * *'
```

---

## 📞 Support

**Problème?** Allez voir:
- [GITHUB_ACTIONS_GUIDE.md](./GITHUB_ACTIONS_GUIDE.md) - Guide détaillé
- [GitHub Actions Docs](https://docs.github.com/en/actions)

---

## ✨ Résumé

Vous avez maintenant:

✅ **Build iOS automatique** en cloud  
✅ **Sans Mac local** requis  
✅ **Gratuit** (2000 min/mois)  
✅ **Une app iOS** testable  
✅ **Prêt pour App Store** (avec signing cert)  

**Allez-y! Pushez du code et regardez la magie! 🎉**

```powershell
# C'est tout ce que vous devez faire:
.\build-ios.ps1

# Et hop... app iOS prête! 🚀
```

---

## 🎓 Prochaines Étapes

1. ✅ Builder l'app (ce guide)
2. 📱 Tester sur iPhone
3. 🔑 Apple Developer Account ($99)
4. 📤 Uploader sur TestFlight
5. 🎉 App Store! 

**On le fait ensemble? Demandez!** 💪
