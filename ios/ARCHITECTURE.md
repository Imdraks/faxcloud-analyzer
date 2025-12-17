# Architecture iOS - FaxCloud Analyzer

## 🏗️ Architecture MVVM

```
┌─────────────────────────────────────────────┐
│         SwiftUI Views (Présentation)        │
│  ContentView, ReportListView, DetailView... │
└────────────────────────┬────────────────────┘
                         │
┌─────────────────────────▼────────────────────┐
│      ViewModels (Logique Métier)            │
│  ReportViewModel, EntryViewModel...         │
└────────────────────────┬────────────────────┘
                         │
┌─────────────────────────▼────────────────────┐
│      Models (Structures de Données)         │
│  Report, FaxEntry, APIResponse...          │
└────────────────────────┬────────────────────┘
                         │
┌─────────────────────────▼────────────────────┐
│      Services (Métier)                      │
│  APIService, StorageService...             │
└────────────────────────┬────────────────────┘
                         │
┌─────────────────────────▼────────────────────┐
│    Utilitaires & Extensions                 │
│  Constants, DateFormatter, Network...       │
└─────────────────────────────────────────────┘
```

## 📦 Couches

### 1. **Presentation Layer (Views)**
- **ContentView**: Point d'entrée avec TabView
- **ReportListView**: Liste scrollable des rapports
- **ReportDetailView**: Détails avec filtrage
- **SettingsView**: Configuration

**Responsabilités:**
- Afficher l'UI
- Accepter les inputs utilisateur
- Afficher les états de chargement

### 2. **ViewModel Layer**
- **ReportViewModel**: 
  - Fetch rapports
  - Fetch détails
  - Télécharger PDF
  - Filtrer entries
  
**Responsabilités:**
- Observer les changements
- Appeler les services
- Mettre à jour les @Published properties
- Gérer les erreurs

### 3. **Model Layer**
- **Report**: Rapport principal
- **FaxEntry**: Entrée FAX individual
- **APIResponse**: Réponses API génériques
- **FilterType**: Énumération des filtres

**Responsabilités:**
- Représenter les données
- Codable pour la sérialisation JSON
- Computed properties pour les transformations

### 4. **Service Layer**
- **APIService**: 
  - Requêtes HTTP (URLSession)
  - Combine Publishers
  - Gestion des erreurs réseau

**Responsabilités:**
- Communication avec l'API
- Parsing JSON
- Gestion du cache optionnel

### 5. **Utilities Layer**
- **Constants**: URLs, clés
- **Extensions**: Date, String formatting
- **NetworkMonitor**: Statut connectivité (optionnel)

## 🔄 Flux de Données

```
User Action (Button Tap)
        ↓
View Call ViewModel Method
        ↓
ViewModel Call APIService
        ↓
APIService Make HTTP Request
        ↓
Server Response
        ↓
APIService Decode JSON → Model
        ↓
ViewModel Update @Published Properties
        ↓
SwiftUI Re-render View with New Data
```

## 🔌 Combine Publishers

### Pattern utilisé:

```swift
apiService.fetchReports()
    .receive(on: DispatchQueue.main)  // UI updates
    .sink { completion in              // Erreur ou succès
        switch completion {
        case .finished: break
        case .failure(let error): 
            self.errorMessage = error.description
        }
    } receiveValue: { reports in       // Données reçues
        self.reports = reports
    }
    .store(in: &cancellables)          // Memory management
```

## 🧪 Testabilité

### Points testables:

1. **ViewModel Tests**
```swift
func testFetchReports() {
    viewModel.fetchReports()
    XCTAssertFalse(viewModel.reports.isEmpty)
}
```

2. **Model Tests**
```swift
func testReportDecoding() {
    let json = """
    {"id": "123", "title": "Test", ...}
    """
    let report = try JSONDecoder().decode(Report.self, from: json.data(using: .utf8)!)
    XCTAssertEqual(report.id, "123")
}
```

3. **Service Tests** (Mock URLSession)
```swift
class MockURLSession: URLSession {
    // Override dataTaskPublisher
}
```

## 🚀 Performance

### Optimisations Implémentées:

1. **LazyVStack** pour listes longues (optionnel)
2. **@StateObject** pour éviter les re-créations
3. **Combine** pour les async/await élégants
4. **Image Caching** (optionnel, URLCache)

### À implémenter:

- [ ] Pagination des rapports
- [ ] Lazy loading des images
- [ ] Débouncing des recherches
- [ ] Caching des réponses API

## 🔐 Sécurité

### Actuels:

- ✅ Erreurs gérées sans crash
- ✅ URL validation
- ✅ UserDefaults pour config non-sensible

### À ajouter:

- [ ] HTTPS enforcement
- [ ] Certificate pinning
- [ ] Token authentication
- [ ] Keychain pour secrets
- [ ] Input validation

## 📊 État Global (optionnel)

Actuellement chaque vue a son propre ViewModel.

Pour un état global:
```swift
@StateObject private var appState = AppState()

// AppState.swift
class AppState: ObservableObject {
    @Published var user: User?
    @Published var recentReports: [Report] = []
}
```

## 🎨 Theme

### Couleurs définies:
```swift
Primary Green: RGB(0, 255, 136) = #00FF88
Background: RGB(10, 10, 30) = #0A0A1E
Cards: RGB(25, 25, 40) = #191928
```

À mettre dans Color Extension:
```swift
extension Color {
    static let primaryGreen = Color(red: 0, green: 1, blue: 0.533)
    static let appBackground = Color(red: 0.04, green: 0.04, blue: 0.12)
}
```

## 🗂️ Arborescence Idéale

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
│   ├── Components/
│   │   ├── StatCard.swift
│   │   ├── EntryRow.swift
│   │   └── FilterButton.swift
│   └── SettingsView.swift
├── ViewModels/
│   ├── ReportViewModel.swift
│   ├── EntryViewModel.swift (optionnel)
│   └── SettingsViewModel.swift (optionnel)
├── Services/
│   ├── APIService.swift
│   ├── StorageService.swift
│   └── NetworkMonitor.swift (optionnel)
├── Utilities/
│   ├── Constants.swift
│   ├── Extensions/
│   │   ├── DateExtension.swift
│   │   ├── StringExtension.swift
│   │   └── ColorExtension.swift
│   └── Helpers/
│       └── NetworkHelper.swift
└── Resources/
    └── Localizable.strings (i18n)
```

## 🔗 Références

- [SwiftUI Documentation](https://developer.apple.com/xcode/swiftui/)
- [Combine Framework](https://developer.apple.com/documentation/combine)
- [URLSession](https://developer.apple.com/documentation/foundation/urlsession)
- [MVVM Pattern](https://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93viewmodel)

---

**Version**: 1.0.0  
**Dernière mise à jour**: 17/12/2025
