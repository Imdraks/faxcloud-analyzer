# FaxCloud Analyzer - Client iOS

Application iOS native pour accéder à FaxCloud Analyzer.

## Structure

```
ios/
├── FaxCloudAnalyzer/          # Projet Xcode principal
│   ├── FaxCloudAnalyzer/
│   │   ├── App.swift          # Point d'entrée
│   │   ├── ContentView.swift   # Vue principale
│   │   ├── Models/            # Modèles de données
│   │   ├── Views/             # Vues SwiftUI
│   │   ├── Services/          # Services API
│   │   └── Assets/            # Images, couleurs
│   ├── FaxCloudAnalyzerTests/
│   └── FaxCloudAnalyzer.xcodeproj
├── README.md
└── requirements.md
```

## Technologies

- **Language**: Swift 5.9+
- **Framework UI**: SwiftUI
- **Networking**: URLSession
- **Stockage**: Core Data / UserDefaults
- **iOS Target**: iOS 16.0+

## Fonctionnalités Principales

- [ ] Connexion à l'API FaxCloud
- [ ] Consultation des rapports
- [ ] Filtrage des entrées (envoyés/reçus/erreurs)
- [ ] Téléchargement des rapports PDF
- [ ] Génération QR code
- [ ] Stockage local des données

## Installation

### Prérequis
- Xcode 15+
- iOS 16.0+

### Étapes

1. Ouvrir le projet dans Xcode:
```bash
open FaxCloudAnalyzer/FaxCloudAnalyzer.xcodeproj
```

2. Sélectionner un simulator ou device

3. Build & Run (Cmd + R)

## Configuration API

Modifier `Services/APIService.swift` avec l'URL de votre serveur:

```swift
let baseURL = "http://your-server:5000"
```

## Architecture

### MVVM Pattern
- **Model**: Structures de données
- **View**: Interfaces SwiftUI
- **ViewModel**: Logique métier

### Services
- **APIService**: Communication avec le backend
- **StorageService**: Gestion du stockage local
- **NetworkMonitor**: Détection du statut réseau

## Développement

### Structure des fichiers à créer

```
FaxCloudAnalyzer/
├── App.swift
├── Models/
│   ├── Report.swift
│   ├── FaxEntry.swift
│   └── APIResponse.swift
├── Views/
│   ├── ContentView.swift
│   ├── ReportListView.swift
│   ├── ReportDetailView.swift
│   ├── EntryListView.swift
│   └── SettingsView.swift
├── ViewModels/
│   ├── ReportViewModel.swift
│   ├── EntryViewModel.swift
│   └── SettingsViewModel.swift
├── Services/
│   ├── APIService.swift
│   ├── StorageService.swift
│   └── NetworkMonitor.swift
├── Utilities/
│   ├── Constants.swift
│   ├── Extensions.swift
│   └── DateFormatter.swift
└── Assets.xcassets/
```

## API Endpoints Utilisés

- `GET /api/stats` - Statistiques globales
- `GET /api/reports` - Liste des rapports
- `GET /api/report/{id}/data` - Détails d'un rapport
- `GET /api/report/{id}/qrcode` - QR code
- `GET /api/report/{id}/pdf` - Téléchargement PDF

## Testing

```bash
xcodebuild test -scheme FaxCloudAnalyzer
```

## Debugging

- Utiliser Xcode Debugger (Cmd + Y)
- Network Link Conditioner pour simuler des connexions lentes
- Logs: `print()` ou `os_log()`

## Distribution

### Testflight
1. Archive le projet
2. Utiliser Xcode Organizer
3. Distribuer via TestFlight

### App Store
1. Créer un App Store Connect account
2. Configurer le code signing
3. Soumettre la version finale

## Notes de Performance

- Utiliser LazyVStack pour les listes longues
- Cacher les images
- Implémenter la pagination
- Utiliser Combine pour les requêtes

## Support

Pour les problèmes:
1. Vérifier la connexion API
2. Consulter les logs Xcode
3. Vérifier les permissions iOS (réseau, stockage)

---

**Version**: 1.0.0
**Dernière mise à jour**: 16/12/2025
