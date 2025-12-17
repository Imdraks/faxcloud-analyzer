import SwiftUI

struct SettingsView: View {
    @State private var serverURL = UserDefaults.standard.string(forKey: "apiBaseURL") ?? "http://127.0.0.1:5000"
    @State private var showAlert = false
    @State private var alertMessage = ""
    
    var body: some View {
        NavigationStack {
            ZStack {
                LiquidGlassTheme.Colors.background
                    .ignoresSafeArea()
                
                Form {
                    Section(header: Text("Connexion API")) {
                        TextField("URL du serveur", text: $serverURL)
                            .textInputAutocapitalization(.never)
                            .keyboardType(.URL)
                            .textFieldStyle(.roundedBorder)
                        
                        Text("Ex: http://192.168.1.100:5000")
                            .font(LiquidGlassTheme.Typography.caption)
                            .foregroundColor(.gray)
                    }
                    
                    Section {
                        Button(action: saveSettings) {
                            HStack {
                                Image(systemName: "checkmark.circle.fill")
                                    .foregroundColor(LiquidGlassTheme.Colors.primary)
                                Text("Enregistrer")
                            }
                            .frame(maxWidth: .infinity)
                            .foregroundColor(.black)
                        }
                        .listRowBackground(LiquidGlassTheme.Colors.primary)
                    }
                    
                    Section(header: Text("À propos")) {
                        HStack {
                            Text("Version")
                            Spacer()
                            Text("1.0.0")
                                .foregroundColor(.gray)
                        }
                        
                        HStack {
                            Text("Application")
                            Spacer()
                            Text("FaxCloud Analyzer")
                                .foregroundColor(.gray)
                        }
                        
                        HStack {
                            Text("Plateforme")
                            Spacer()
                            Text("iOS 16+")
                                .foregroundColor(.gray)
                        }
                    }
                }
                .navigationTitle("⚙️ Paramètres")
                .navigationBarTitleDisplayMode(.inline)
            }
            .alert("Succès", isPresented: $showAlert) {
                Button("OK") { }
            } message: {
                Text(alertMessage)
            }
        }
    }
    
    private func saveSettings() {
        if serverURL.isEmpty {
            alertMessage = "Veuillez entrer une URL"
            showAlert = true
            return
        }
        
        // Validate URL
        if !serverURL.starts(with: "http://") && !serverURL.starts(with: "https://") {
            serverURL = "http://\(serverURL)"
        }
        
        UserDefaults.standard.set(serverURL, forKey: "apiBaseURL")
        APIService.shared.setBaseURL(serverURL)
        
        alertMessage = "Paramètres enregistrés avec succès"
        showAlert = true
    }
}

#Preview {
    SettingsView()
}
