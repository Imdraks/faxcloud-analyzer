import SwiftUI

struct ReportListView: View {
    @StateObject private var viewModel = ReportViewModel()
    @State private var showDetail = false
    
    var body: some View {
        NavigationStack {
            ZStack {
                // Background
                LiquidGlassTheme.Colors.background
                    .ignoresSafeArea()
                
                VStack {
                    if viewModel.isLoading && viewModel.reports.isEmpty {
                        VStack(spacing: 20) {
                            ProgressView()
                                .scaleEffect(1.5)
                            Text("Chargement des rapports...")
                                .foregroundColor(.gray)
                        }
                    } else if let error = viewModel.errorMessage {
                        VStack(spacing: 12) {
                            Image(systemName: "exclamationmark.triangle.fill")
                                .font(.system(size: 40))
                                .foregroundColor(.orange)
                            Text("Erreur")
                                .font(LiquidGlassTheme.Typography.headline)
                            Text(error)
                                .font(LiquidGlassTheme.Typography.caption)
                                .lineLimit(3)
                            Button(action: { viewModel.fetchReports() }) {
                                Label("Réessayer", systemImage: "arrow.clockwise")
                                    .frame(maxWidth: .infinity)
                                    .padding()
                                    .background(LiquidGlassTheme.Colors.primary)
                                    .foregroundColor(.black)
                                    .cornerRadius(LiquidGlassTheme.CornerRadius.medium)
                            }
                            .glassProminentButton()
                        }
                        .padding()
                    } else if viewModel.reports.isEmpty {
                        VStack(spacing: 12) {
                            Image(systemName: "doc.text")
                                .font(.system(size: 40))
                                .foregroundColor(.gray)
                            Text("Aucun rapport")
                                .font(LiquidGlassTheme.Typography.headline)
                            Text("Les rapports apparaîtront ici")
                                .font(LiquidGlassTheme.Typography.caption)
                                .foregroundColor(.gray)
                        }
                    } else {
                        List {
                            ForEach(viewModel.reports) { report in
                                NavigationLink(destination: ReportDetailView(report: report)) {
                                    ReportRowView(report: report)
                                }
                            }
                        }
                        .listStyle(.plain)
                    }
                }
                .navigationTitle("📊 Rapports")
                .navigationBarTitleDisplayMode(.inline)
                .toolbar {
                    ToolbarItem(placement: .navigationBarTrailing) {
                        Button(action: { viewModel.fetchReports() }) {
                            Image(systemName: "arrow.clockwise")
                                .foregroundColor(LiquidGlassTheme.Colors.primary)
                        }
                    }
                }
            }
        }
        .onAppear {
            viewModel.fetchReports()
        }
    }
}

struct ReportRowView: View {
    let report: Report
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text(report.title)
                        .font(LiquidGlassTheme.Typography.headline)
                    Text(report.formattedDate)
                        .font(LiquidGlassTheme.Typography.caption)
                        .foregroundColor(.gray)
                }
                Spacer()
                VStack(alignment: .trailing, spacing: 4) {
                    HStack(spacing: 8) {
                        Image(systemName: "checkmark.circle.fill")
                            .foregroundColor(LiquidGlassTheme.Colors.primary)
                        Text("\(report.sent)")
                            .font(LiquidGlassTheme.Typography.caption2)
                    }
                    HStack(spacing: 8) {
                        Image(systemName: "xmark.circle.fill")
                            .foregroundColor(.red)
                        Text("\(report.errors)")
                            .font(LiquidGlassTheme.Typography.caption2)
                    }
                }
            }
            
            HStack(spacing: 12) {
                StatBadge(icon: "📊", title: "Total", value: report.total)
                StatBadge(icon: "📈", title: "Succès", value: Int(report.success_rate))
            }
        }
        .padding(.vertical, 8)
        .glassCard()
    }
}

struct StatBadge: View {
    let icon: String
    let title: String
    let value: Int
    
    var body: some View {
        HStack(spacing: 4) {
            Text(icon)
                .font(.caption)
            VStack(alignment: .leading, spacing: 2) {
                Text(title)
                    .font(LiquidGlassTheme.Typography.caption2)
                    .foregroundColor(.gray)
                Text(String(value))
                    .font(LiquidGlassTheme.Typography.caption)
                    .fontWeight(.semibold)
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(8)
        .background(LiquidGlassTheme.Colors.glassLight)
        .cornerRadius(LiquidGlassTheme.CornerRadius.small)
    }
}

#Preview {
    ReportListView()
}
