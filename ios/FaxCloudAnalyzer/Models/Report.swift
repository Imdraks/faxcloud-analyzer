import Foundation

// MARK: - Report Model
struct Report: Identifiable, Codable {
    let id: String
    let title: String
    let date: String
    let summary: String?
    
    // Statistics
    let total: Int
    let sent: Int
    let received: Int
    let errors: Int
    let success_rate: Double
    let entries_count: Int
    
    // Entries
    var entries: [FaxEntry]?
    
    var formattedDate: String {
        let formatter = ISO8601DateFormatter()
        if let date = formatter.date(from: date) {
            let displayFormatter = DateFormatter()
            displayFormatter.locale = Locale(identifier: "fr_FR")
            displayFormatter.dateStyle = .medium
            displayFormatter.timeStyle = .short
            return displayFormatter.string(from: date)
        }
        return date
    }
    
    var successRatePercentage: String {
        String(format: "%.1f%%", success_rate)
    }
}

// MARK: - Report List Response
struct ReportListResponse: Codable {
    let reports: [Report]
    let total: Int
    let page: Int
    let pages: Int
}

// MARK: - Report Detail Response
struct ReportDetailResponse: Codable {
    let id: String
    let title: String
    let date: String
    let summary: String?
    let total: Int
    let sent: Int
    let received: Int
    let errors: Int
    let success_rate: Double
    let entries_count: Int
    let entries: [FaxEntry]
}
