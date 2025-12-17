# 📱 FaxCloud Analyzer - Client iOS

Projet iOS natif SwiftUI pour l'application FaxCloud Analyzer.

## ✨ Fonctionnalités

- ✅ Liste des rapports d'analyse FAX
- ✅ Consultation détaillée des rapports
- ✅ Filtrage des entrées (Tous, Envoyés, Reçus, Erreurs)
- ✅ Statistiques en temps réel
- ✅ Téléchargement de PDF
- ✅ Configuration de l'API serveur
- ✅ Interface dark mode

## 🛠️ Stack Technologique

| Component | Technologie |
|-----------|-------------|
| Framework | SwiftUI |
| Networking | URLSession + Combine |
| Architecture | MVVM |
| Storage | UserDefaults |
| Minimum iOS | 16.0 |
| Swift Version | 5.9+ |

## 📁 Structure du Projet

```
ios/
├── FaxCloudAnalyzer/              # Source code
│   ├── App.swift                  # Entry point
│   ├── Models/                    # Data models
│   │   ├── Report.swift
│   │   ├── FaxEntry.swift
│   │   └── APIResponse.swift
│   ├── Views/                     # SwiftUI views
│   │   ├── ContentView.swift
│   │   ├── ReportListView.swift
│   │   ├── ReportDetailView.swift
│   │   └── SettingsView.swift
│   ├── ViewModels/                # Business logic
│   │   └── ReportViewModel.swift
│   ├── Services/                  # API & Services
│   │   └── APIService.swift
│   └── Utilities/                 # Helpers
├── FaxCloudAnalyzerTests/         # Unit tests
├── FaxCloudAnalyzer.xcodeproj     # Xcode project
├── Package.swift                  # Swift Package config
├── README.md                      # Documentation principale
├── SETUP.md                       # Guide d'installation
└── ARCHITECTURE.md                # Documentation architecture
```

## 🚀 Démarrage Rapide

### Prérequis
- Xcode 15+
- macOS 13+
- iOS 16+ device/simulator

### Installation

```bash
# Cloner le repo
git clone <repo-url>
cd ios

# Ouvrir dans Xcode
open FaxCloudAnalyzer/FaxCloudAnalyzer.xcodeproj

# Build & Run (Cmd + R)
```

### Configuration

1. Lancer le serveur backend:
```bash
cd ..
python -m web.app
```

2. Dans l'app iOS:
   - Aller à Paramètres
   - Entrer l'URL du serveur: `http://127.0.0.1:5000`
   - Enregistrer

3. Retourner à Rapports pour voir les données

## 📊 Endpoints Utilisés

| Méthode | Endpoint | Utilité |
|---------|----------|---------|
| GET | `/api/stats` | Stats globales |
| GET | `/api/reports` | Liste rapports |
| GET | `/api/report/{id}/data` | Détails rapport |
| GET | `/api/report/{id}/pdf` | Télécharger PDF |
| GET | `/api/report/{id}/qrcode` | QR code |

## 🎯 Fonctionnalités par Vue

### ContentView (Racine)
- TabView avec 2 onglets
- Navigation entre Rapports et Paramètres

### ReportListView
- List scrollable des rapports
- Pull-to-refresh
- Navigation vers détails
- Stats résumées (sent, errors)

### ReportDetailView
- Statistiques complètes
- Filtrage des entrées (4 boutons)
- Tableau des FAX avec détails
- Bouton télécharger PDF
- Gestion du loading

### SettingsView
- Configuration URL serveur
- Validation d'URL
- À propos de l'application

## 🔄 Flux de Données

```
ContentView (State)
    ├── ReportListView
    │   └── ReportViewModel
    │       └── APIService
    │           └── URLSession
    └── SettingsView
```

## 💾 Stockage Local

L'app utilise **UserDefaults** pour:
- URL du serveur: clé `apiBaseURL`

Format sauvegardé:
```swift
UserDefaults.standard.set("http://192.168.1.100:5000", forKey: "apiBaseURL")
```

## 🎨 Thème & Design

### Couleurs
- **Primaire Verte**: `RGB(0, 255, 136)` → `#00FF88`
- **Background**: `RGB(10, 10, 30)` → `#0A0A1E`
- **Cards**: `RGB(25, 25, 40)` → `#191928`

### Typography
- Titre: `.title2`, `.bold`
- Sous-titre: `.headline`
- Corps: `.caption` to `.body`
- Dark mode par défaut

## 🧪 Testing

### Structures testables

```swift
// Models
- Report encoding/decoding
- FaxEntry filtering
- FilterType matching

// ViewModels
- fetchReports()
- fetchReportDetail()
- filterEntries()

// Services
- URL building
- Response parsing
```

### Lancer les tests

```bash
xcodebuild test -scheme FaxCloudAnalyzer
```

## 🐛 Debugging

### Logs à vérifier
- Console Xcode (Cmd + Shift + C)
- Network tab dans Xcode
- Error messages dans l'app

### Problèmes courants

| Problème | Solution |
|----------|----------|
| "Cannot connect to server" | Vérifier URL + serveur running |
| "No entries shown" | Vérifier les données du serveur |
| App crashes at startup | Clean build (Cmd + Shift + K) |
| SSL certificate error | Use http:// not https:// |

## 📈 Roadmap

### Phase 1 (Actuel)
- [x] List & detail views
- [x] Filtering
- [x] PDF download
- [x] API integration

### Phase 2 (Planifié)
- [ ] Upload CSV files
- [ ] Offline mode
- [ ] Push notifications
- [ ] Charts & graphs
- [ ] Share reports
- [ ] Dark/Light toggle

### Phase 3 (Futur)
- [ ] App Store release
- [ ] Multi-user support
- [ ] Advanced analytics
- [ ] Cloud sync
- [ ] Widget support

## 📞 Support & Contact

Pour les problèmes, consulter:
1. [SETUP.md](./SETUP.md) - Installation
2. [ARCHITECTURE.md](./ARCHITECTURE.md) - Architecture
3. [README.md](./README.md) - Documentation complète

## 📄 Licence

Même licence que le projet FaxCloud Analyzer

---

**Status**: 🟢 En développement  
**Version**: 1.0.0  
**Dernière mise à jour**: 17/12/2025  
**Mainteneur**: FaxCloud Team
