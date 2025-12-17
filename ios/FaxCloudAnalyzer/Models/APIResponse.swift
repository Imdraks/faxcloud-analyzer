import Foundation

// MARK: - API Response Models
struct APIStats: Codable {
    let total: Int
    let sent: Int
    let received: Int
    let errors: Int
    let success_rate: Double
    
    enum CodingKeys: String, CodingKey {
        case total = "total_fax"
        case sent = "fax_envoyes"
        case received = "fax_recus"
        case errors = "erreurs_totales"
        case success_rate = "taux_reussite"
    }
}

// MARK: - API Error Response
struct APIError: Codable {
    let success: Bool
    let message: String
    let error: String?
}

// MARK: - Generic API Response
struct APIResponse<T: Codable>: Codable {
    let success: Bool
    let data: T?
    let message: String?
    let error: String?
}

// MARK: - Upload Response
struct UploadResponse: Codable {
    let success: Bool
    let report_id: String?
    let imported: Int?
    let total: Int?
    let errors: Int?
    let message: String?
}

// MARK: - QR Code Response
struct QRCodeResponse: Codable {
    let success: Bool
    let qrcode_url: String?
    let message: String?
}

// MARK: - PDF Response
struct PDFResponse: Codable {
    let success: Bool
    let pdf_url: String?
    let message: String?
}
