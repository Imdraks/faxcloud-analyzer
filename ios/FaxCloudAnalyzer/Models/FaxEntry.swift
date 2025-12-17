import Foundation

// MARK: - Fax Entry Model
struct FaxEntry: Identifiable, Codable {
    let id: String
    let report_id: String
    let utilisateur: String?
    let date_envoi: String?
    let mode: String? // 'SF' = Sent, 'RF' = Received
    let numero: String?
    let pages: Int?
    let valide: Int? // 0 = error, 1 = success
    let erreur: String?
    
    var modeDisplayName: String {
        switch mode?.uppercased() {
        case "SF":
            return "Envoyé"
        case "RF":
            return "Reçu"
        default:
            return mode ?? "-"
        }
    }
    
    var statusDisplayName: String {
        switch valide {
        case 0:
            return "Erreur"
        case 1:
            return "Succès"
        default:
            return "-"
        }
    }
    
    var statusColor: String {
        switch valide {
        case 0:
            return "red"
        case 1:
            return "green"
        default:
            return "gray"
        }
    }
    
    var formattedDate: String {
        guard let dateString = date_envoi else { return "-" }
        let formatter = ISO8601DateFormatter()
        if let date = formatter.date(from: dateString) {
            let displayFormatter = DateFormatter()
            displayFormatter.locale = Locale(identifier: "fr_FR")
            displayFormatter.dateStyle = .short
            displayFormatter.timeStyle = .short
            return displayFormatter.string(from: date)
        }
        return dateString
    }
    
    var hasError: Bool {
        valide == 0
    }
    
    var isSent: Bool {
        mode?.uppercased() == "SF"
    }
    
    var isReceived: Bool {
        mode?.uppercased() == "RF"
    }
}

// MARK: - Filter Type
enum FilterType: String, CaseIterable {
    case all = "all"
    case sent = "sent"
    case received = "received"
    case error = "error"
    
    var displayName: String {
        switch self {
        case .all:
            return "Tous"
        case .sent:
            return "Envoyés"
        case .received:
            return "Reçus"
        case .error:
            return "Erreurs"
        }
    }
    
    var emoji: String {
        switch self {
        case .all:
            return "📌"
        case .sent:
            return "📤"
        case .received:
            return "📥"
        case .error:
            return "⚠️"
        }
    }
    
    func matches(entry: FaxEntry) -> Bool {
        switch self {
        case .all:
            return true
        case .sent:
            return entry.isSent
        case .received:
            return entry.isReceived
        case .error:
            return entry.hasError
        }
    }
}
