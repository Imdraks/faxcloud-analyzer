import Foundation
import Combine

class APIService: ObservableObject {
    static let shared = APIService()
    
    private var baseURL: String {
        UserDefaults.standard.string(forKey: "apiBaseURL") ?? "http://127.0.0.1:5000"
    }
    
    private var session: URLSession {
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = 30
        config.timeoutIntervalForResource = 300
        return URLSession(configuration: config)
    }
    
    // MARK: - Stats
    func fetchStats() -> AnyPublisher<APIStats, Error> {
        let url = URL(string: "\(baseURL)/api/stats")!
        
        return session.dataTaskPublisher(for: url)
            .map(\.data)
            .decode(type: APIStats.self, decoder: JSONDecoder())
            .eraseToAnyPublisher()
    }
    
    // MARK: - Reports
    func fetchReports(page: Int = 1, limit: Int = 10) -> AnyPublisher<[Report], Error> {
        let url = URL(string: "\(baseURL)/api/reports?page=\(page)&limit=\(limit)")!
        
        return session.dataTaskPublisher(for: url)
            .map(\.data)
            .decode(type: ReportListResponse.self, decoder: JSONDecoder())
            .map { $0.reports }
            .eraseToAnyPublisher()
    }
    
    // MARK: - Report Detail
    func fetchReportDetail(reportId: String) -> AnyPublisher<Report, Error> {
        let url = URL(string: "\(baseURL)/api/report/\(reportId)/data")!
        
        return session.dataTaskPublisher(for: url)
            .map(\.data)
            .decode(type: Report.self, decoder: JSONDecoder())
            .eraseToAnyPublisher()
    }
    
    // MARK: - QR Code
    func fetchQRCode(reportId: String) -> AnyPublisher<URL, Error> {
        let url = URL(string: "\(baseURL)/api/report/\(reportId)/qrcode")!
        
        return session.dataTaskPublisher(for: url)
            .map { (data: $0.data, response: $0.response) }
            .tryMap { data, response in
                guard let httpResponse = response as? HTTPURLResponse,
                      httpResponse.statusCode == 200 else {
                    throw URLError(.badServerResponse)
                }
                // The URL itself is the QR code endpoint
                return url
            }
            .eraseToAnyPublisher()
    }
    
    // MARK: - PDF Download
    func downloadPDF(reportId: String) -> AnyPublisher<URL, Error> {
        let url = URL(string: "\(baseURL)/api/report/\(reportId)/pdf")!
        let fileName = "rapport_\(reportId).pdf"
        
        return session.downloadTaskPublisher(for: url)
            .tryMap { (data, response) in
                guard let httpResponse = response as? HTTPURLResponse,
                      httpResponse.statusCode == 200 else {
                    throw URLError(.badServerResponse)
                }
                
                let documentsURL = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
                let fileURL = documentsURL.appendingPathComponent(fileName)
                
                try FileManager.default.moveItem(at: data, to: fileURL)
                return fileURL
            }
            .eraseToAnyPublisher()
    }
    
    // MARK: - API URL Builder
    func setBaseURL(_ url: String) {
        UserDefaults.standard.set(url, forKey: "apiBaseURL")
    }
    
    func getBaseURL() -> String {
        baseURL
    }
}

// MARK: - URLSession Extension for Download
extension URLSession {
    func downloadTaskPublisher(for url: URL) -> AnyPublisher<(URL, URLResponse), URLError> {
        return Future { [weak self] promise in
            let task = self?.downloadTask(with: url) { tempURL, response, error in
                if let error = error as? URLError {
                    promise(.failure(error))
                } else if let tempURL = tempURL, let response = response {
                    promise(.success((tempURL, response)))
                } else {
                    promise(.failure(.badServerResponse))
                }
            }
            task?.resume()
        }
        .eraseToAnyPublisher()
    }
}
