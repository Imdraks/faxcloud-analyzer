// ============================================
// REPORTS PAGE - JavaScript
// ============================================

let allReports = [];
let filteredReports = [];

/**
 * Charger tous les rapports
 */
async function loadReports() {
    try {
        const reports = await API.getReports(100);
        allReports = reports;
        filteredReports = [...reports];
        renderReportsTable(filteredReports);
    } catch (error) {
        console.error('Erreur:', error);
        Utils.showNotification('Erreur lors du chargement des rapports', 'error');
    }
}

/**
 * Afficher les rapports dans la table
 */
function renderReportsTable(reports) {
    const tbody = document.getElementById('reports-body');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    if (reports.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center">Aucun rapport trouvé</td></tr>';
        return;
    }
    
    reports.forEach(report => {
        tbody.innerHTML += `
            <tr>
                <td>#${report.id}</td>
                <td>${report.name}</td>
                <td>${Utils.formatDate(report.created_at)}</td>
                <td>${report.entry_count || 0}</td>
                <td>${Utils.formatFileSize(report.file_size || 0)}</td>
                <td><span class="badge badge-success">✓ Complété</span></td>
                <td>
                    <a href="/report/${report.id}" class="btn btn-sm">📋 Voir</a>
                    <button onclick="exportReport(${report.id})" class="btn btn-sm btn-secondary">💾 Export</button>
                </td>
            </tr>
        `;
    });
}

/**
 * Filtrer les rapports par recherche
 */
function filterReports() {
    const searchTerm = document.getElementById('search')?.value.toLowerCase() || '';
    const statusFilter = document.getElementById('status-filter')?.value || '';
    
    filteredReports = allReports.filter(report => {
        const matchesSearch = !searchTerm || 
            report.name.toLowerCase().includes(searchTerm);
        
        const matchesStatus = !statusFilter || 
            report.status === statusFilter || 
            statusFilter === 'completed';
        
        return matchesSearch && matchesStatus;
    });
    
    renderReportsTable(filteredReports);
}

/**
 * Exporter un rapport
 */
async function exportReport(reportId) {
    try {
        const data = await API.get(`/api/reports/${reportId}/export`);
        
        // Créer un blob et télécharger
        const element = document.createElement('a');
        element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(JSON.stringify(data, null, 2)));
        element.setAttribute('download', `rapport_${reportId}.json`);
        element.style.display = 'none';
        document.body.appendChild(element);
        element.click();
        document.body.removeChild(element);
        
        Utils.showNotification('Rapport exporté avec succès', 'success');
    } catch (error) {
        console.error('Erreur:', error);
        Utils.showNotification('Erreur lors de l\'export', 'error');
    }
}

/**
 * Charger les rapports au démarrage
 */
document.addEventListener('DOMContentLoaded', () => {
    loadReports();
    
    // Attachers les listeners de filtre
    const searchInput = document.getElementById('search');
    const statusFilter = document.getElementById('status-filter');
    
    if (searchInput) searchInput.addEventListener('input', filterReports);
    if (statusFilter) statusFilter.addEventListener('change', filterReports);
});
