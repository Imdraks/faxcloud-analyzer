import Foundation
import Combine

class ReportViewModel: ObservableObject {
    @Published var reports: [Report] = []
    @Published var selectedReport: Report?
    @Published var isLoading = false
    @Published var errorMessage: String?
    
    private let apiService = APIService.shared
    private var cancellables = Set<AnyCancellable>()
    
    // MARK: - Fetch Reports List
    func fetchReports() {
        isLoading = true
        errorMessage = nil
        
        apiService.fetchReports()
            .receive(on: DispatchQueue.main)
            .sink { [weak self] completion in
                self?.isLoading = false
                switch completion {
                case .finished:
                    break
                case .failure(let error):
                    self?.errorMessage = "Erreur: \(error.localizedDescription)"
                }
            } receiveValue: { [weak self] reports in
                self?.reports = reports
            }
            .store(in: &cancellables)
    }
    
    // MARK: - Fetch Report Detail
    func fetchReportDetail(reportId: String) {
        isLoading = true
        errorMessage = nil
        
        apiService.fetchReportDetail(reportId: reportId)
            .receive(on: DispatchQueue.main)
            .sink { [weak self] completion in
                self?.isLoading = false
                switch completion {
                case .finished:
                    break
                case .failure(let error):
                    self?.errorMessage = "Erreur: \(error.localizedDescription)"
                }
            } receiveValue: { [weak self] report in
                self?.selectedReport = report
            }
            .store(in: &cancellables)
    }
    
    // MARK: - Download PDF
    func downloadPDF(reportId: String) {
        isLoading = true
        errorMessage = nil
        
        apiService.downloadPDF(reportId: reportId)
            .receive(on: DispatchQueue.main)
            .sink { [weak self] completion in
                self?.isLoading = false
                switch completion {
                case .finished:
                    break
                case .failure(let error):
                    self?.errorMessage = "Erreur téléchargement: \(error.localizedDescription)"
                }
            } receiveValue: { url in
                // Open the file
                #if os(iOS)
                UIApplication.shared.open(url)
                #endif
            }
            .store(in: &cancellables)
    }
    
    // MARK: - Filter Entries
    func filterEntries(_ filter: FilterType) -> [FaxEntry] {
        guard let entries = selectedReport?.entries else { return [] }
        return entries.filter { filter.matches(entry: $0) }
    }
    
    // MARK: - Clear
    func clearSelection() {
        selectedReport = nil
        errorMessage = nil
    }
}
