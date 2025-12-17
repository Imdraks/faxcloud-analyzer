# Guide d'Installation - Projet iOS FaxCloud Analyzer

## 📋 Prérequis

- **Mac** avec Xcode 15+ installé
- **iOS 16.0+** sur l'appareil ou simulator
- **Swift 5.9+**
- **Projet FaxCloud backend** en cours d'exécution

## 🚀 Installation

### Étape 1: Ouvrir le projet dans Xcode

```bash
cd ios
open FaxCloudAnalyzer/FaxCloudAnalyzer.xcodeproj
```

### Étape 2: Configuration

1. **Sélectionner un target:**
   - Simulator: iPhone 15, iPhone 15 Pro, etc.
   - Ou un device iPhone réel connecté

2. **Vérifier l'URL du serveur:**
   - L'URL par défaut est `http://127.0.0.1:5000`
   - Si le backend est sur une autre machine, modifier dans Paramètres de l'app

### Étape 3: Build & Run

Appuyer sur **Cmd + R** ou cliquer le bouton Play

### Étape 4: Configurer l'API

Au premier lancement:
1. Aller à l'onglet "Paramètres"
2. Entrer l'URL du serveur (ex: `http://192.168.1.100:5000`)
3. Cliquer "Enregistrer"

## 📱 Utilisation

### Onglet Rapports
- Liste des rapports téléchargés
- Cliquer pour voir les détails
- Icône flèche bas = télécharger PDF

### Détails d'un Rapport
- Statistiques globales
- Filtrer par: Tous, Envoyés, Reçus, Erreurs
- Liste des entrées FAX

### Paramètres
- Configurer l'URL du serveur
- Voir la version de l'app

## 🔧 Dépannage

### L'app ne charge pas les rapports
**Solution:**
1. Vérifier que le serveur est en cours d'exécution
2. Vérifier l'URL du serveur dans Paramètres
3. Ouvrir Xcode Console (Cmd + Shift + C) pour les logs

### Erreur "Cannot connect to server"
**Cause:** URL incorrecte ou serveur down
**Solution:**
1. Vérifier avec `ping` ou `curl`
2. Utiliser l'IP locale (192.168.x.x) au lieu de localhost
3. Pour le simulator: `http://127.0.0.1:5000` fonctionne normalement

### L'app crash au démarrage
**Solution:**
1. Nettoyer le build: Cmd + Shift + K
2. Rebuild: Cmd + B
3. Vérifier la console Xcode pour les erreurs

## 📊 Structures de Fichiers

```
FaxCloudAnalyzer/
├── App.swift                    # Point d'entrée
├── Models/
│   ├── Report.swift             # Modèle Rapport
│   ├── FaxEntry.swift           # Modèle Entrée FAX
│   └── APIResponse.swift        # Réponses API
├── Views/
│   ├── ContentView.swift        # Vue principale (tabs)
│   ├── ReportListView.swift     # Liste des rapports
│   ├── ReportDetailView.swift   # Détails rapport
│   └── SettingsView.swift       # Paramètres
├── ViewModels/
│   └── ReportViewModel.swift    # Logique métier
├── Services/
│   └── APIService.swift         # Communication API
└── Utilities/
    └── (À compléter)
```

## 🌐 Endpoints API Utilisés

L'app communique avec:
- `GET /api/reports` - Liste des rapports
- `GET /api/report/{id}/data` - Détails rapport
- `GET /api/report/{id}/pdf` - Télécharger PDF

## 💾 Stockage Local

L'app utilise **UserDefaults** pour:
- URL du serveur (`apiBaseURL`)

## 🔒 Sécurité

**À implémenter:**
- [ ] HTTPS validation
- [ ] Token authentication
- [ ] Keychain storage for secrets
- [ ] SSL pinning

## 📈 Améliorations Futures

- [ ] Upload direct de fichiers CSV
- [ ] Notifications push
- [ ] Mode hors-ligne
- [ ] Dark/Light mode toggle
- [ ] Graphiques statistiques
- [ ] Export de rapports
- [ ] Partage de rapports via QR code

## 🐛 Logs & Debugging

### Activer verbose logging
Ajouter dans App.swift:
```swift
print("FaxCloud Analyzer started")
```

### Inspecter les requêtes réseau
Utiliser Network Link Conditioner ou Charles Proxy

## 📞 Support

Pour les problèmes:
1. Vérifier les logs Xcode (Cmd + Shift + C)
2. Tester l'URL API avec `curl`
3. Vérifier les permissions iOS (Network, Storage)

---

**Version**: 1.0.0  
**Dernière mise à jour**: 17/12/2025
