import SwiftUI

struct ReportDetailView: View {
    let report: Report
    @StateObject private var viewModel = ReportViewModel()
    @State private var selectedFilter: FilterType = .all
    @Environment(\.dismiss) var dismiss
    
    var filteredEntries: [FaxEntry] {
        guard let entries = viewModel.selectedReport?.entries else { return [] }
        return entries.filter { selectedFilter.matches(entry: $0) }
    }
    
    var body: some View {
        ZStack {
            LiquidGlassTheme.Colors.background
                .ignoresSafeArea()
            
            ScrollView {
                VStack(spacing: 16) {
                    // Header
                    VStack(alignment: .leading, spacing: 8) {
                        HStack {
                            Text(viewModel.selectedReport?.title ?? report.title)
                                .font(LiquidGlassTheme.Typography.title2)
                            Spacer()
                            Button(action: { viewModel.downloadPDF(reportId: report.id) }) {
                                Image(systemName: "arrow.down.circle.fill")
                                    .font(.title3)
                                    .foregroundColor(LiquidGlassTheme.Colors.primary)
                            }
                            .glassProminentButton()
                        }
                        Text(viewModel.selectedReport?.formattedDate ?? report.formattedDate)
                            .font(LiquidGlassTheme.Typography.caption)
                            .foregroundColor(.gray)
                    }
                    .glassCard()
                    
                    // Statistics
                    if let selectedReport = viewModel.selectedReport {
                        VStack(spacing: 12) {
                            HStack(spacing: 12) {
                                StatCard(
                                    icon: "📊",
                                    title: "Total",
                                    value: selectedReport.total,
                                    color: .blue
                                )
                                StatCard(
                                    icon: "📤",
                                    title: "Envoyés",
                                    value: selectedReport.sent,
                                    color: .green
                                )
                            }
                            HStack(spacing: 12) {
                                StatCard(
                                    icon: "📥",
                                    title: "Reçus",
                                    value: selectedReport.received,
                                    color: .orange
                                )
                                StatCard(
                                    icon: "⚠️",
                                    title: "Erreurs",
                                    value: selectedReport.errors,
                                    color: .red
                                )
                            }
                            StatCard(
                                icon: "📈",
                                title: "Taux de Réussite",
                                value: Int(selectedReport.success_rate),
                                valueFormatted: selectedReport.successRatePercentage,
                                color: .green
                            )
                        }
                    }
                    
                    // Filters
                    VStack(spacing: 12) {
                        Text("Filtrer par:")
                            .font(LiquidGlassTheme.Typography.headline)
                            .frame(maxWidth: .infinity, alignment: .leading)
                        
                        HStack(spacing: 8) {
                            ForEach(FilterType.allCases, id: \.self) { filter in
                                Button(action: { selectedFilter = filter }) {
                                    HStack(spacing: 4) {
                                        Text(filter.emoji)
                                        Text(filter.displayName)
                                            .font(LiquidGlassTheme.Typography.caption)
                                    }
                                    .frame(maxWidth: .infinity)
                                    .padding(.vertical, 8)
                                    .background(
                                        selectedFilter == filter ?
                                        LiquidGlassTheme.Colors.primary :
                                        LiquidGlassTheme.Colors.glassLight
                                    )
                                    .cornerRadius(LiquidGlassTheme.CornerRadius.medium)
                                }
                                .glassButton()
                            }
                        }
                    }
                    .padding(LiquidGlassTheme.Spacing.lg)
                    .background(LiquidGlassTheme.Colors.cardBackground.opacity(0.6))
                    .modifier(LiquidGlassEffect())
                    
                    // Entries List
                    if viewModel.isLoading {
                        ProgressView()
                    } else if filteredEntries.isEmpty {
                        Text("Aucune entrée")
                            .foregroundColor(.gray)
                            .frame(maxWidth: .infinity, alignment: .center)
                            .padding()
                    } else {
                        VStack(spacing: 8) {
                            ForEach(filteredEntries) { entry in
                                EntryRowView(entry: entry)
                            }
                        }
                    }
                }
                .padding()
            }
        }
        .navigationBarBackButtonHidden(false)
        .onAppear {
            viewModel.fetchReportDetail(reportId: report.id)
        }
    }
}

struct StatCard: View {
    let icon: String
    let title: String
    let value: Int
    var valueFormatted: String?
    let color: Color
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Text(icon)
                    .font(.title3)
                Text(title)
                    .font(LiquidGlassTheme.Typography.caption2)
                    .foregroundColor(.gray)
                Spacer()
            }
            Text(valueFormatted ?? String(value))
                .font(LiquidGlassTheme.Typography.headline)
                .fontWeight(.semibold)
                .foregroundColor(color)
        }
        .padding(LiquidGlassTheme.Spacing.lg)
        .frame(maxWidth: .infinity, alignment: .leading)
        .glassCard()
    }
}

struct EntryRowView: View {
    let entry: FaxEntry
    
    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text(entry.numero ?? "-")
                        .font(LiquidGlassTheme.Typography.caption)
                        .fontWeight(.semibold)
                    Text(entry.formattedDate)
                        .font(LiquidGlassTheme.Typography.caption2)
                        .foregroundColor(.gray)
                }
                Spacer()
                HStack(spacing: 8) {
                    Text(entry.modeDisplayName)
                        .font(LiquidGlassTheme.Typography.caption2)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(entry.isSent ? LiquidGlassTheme.Colors.primary.opacity(0.2) : Color.blue.opacity(0.2))
                        .cornerRadius(LiquidGlassTheme.CornerRadius.small)
                    
                    Image(systemName: entry.hasError ? "xmark.circle.fill" : "checkmark.circle.fill")
                        .foregroundColor(entry.hasError ? .red : LiquidGlassTheme.Colors.primary)
                        .font(.caption)
                }
            }
            
            if let erreur = entry.erreur, !erreur.isEmpty {
                Text(erreur)
                    .font(LiquidGlassTheme.Typography.caption2)
                    .foregroundColor(.red)
                    .lineLimit(2)
            }
        }
        .padding(LiquidGlassTheme.Spacing.lg)
        .glassCard()
    }
}

#Preview {
    ReportDetailView(report: Report(
        id: "import_123",
        title: "Rapport Test",
        date: Date().ISO8601Format(),
        summary: nil,
        total: 100,
        sent: 60,
        received: 35,
        errors: 5,
        success_rate: 95.0,
        entries_count: 100
    ))
}
