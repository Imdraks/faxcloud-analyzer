import SwiftUI

struct ContentView: View {
    @StateObject private var viewModel = ReportViewModel()
    @State private var selectedTab = 0
    
    var body: some View {
        TabView(selection: $selectedTab) {
            // Reports Tab
            ReportListView()
                .tabItem {
                    Label("Rapports", systemImage: "doc.text.magnifyingglass")
                }
                .tag(0)
            
            // Settings Tab
            SettingsView()
                .tabItem {
                    Label("Paramètres", systemImage: "gear")
                }
                .tag(1)
        }
        .accentColor(LiquidGlassTheme.Colors.primary)
        .background(LiquidGlassTheme.Colors.background)
    }
}

#Preview {
    ContentView()
}
