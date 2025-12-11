/* Reports list page */

function loadReports() {
    fetch('/api/reports?limit=50')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayReports(data.reports);
            } else {
                document.getElementById('reportsList').innerHTML = 
                    '<p class="error">Erreur lors du chargement</p>';
            }
        })
        .catch(err => {
            document.getElementById('reportsList').innerHTML = 
                '<p class="error">Erreur: ' + err.message + '</p>';
        });
}

function displayReports(reports) {
    if (!reports || reports.length === 0) {
        document.getElementById('reportsList').innerHTML = 
            '<p class="text-muted">Aucun rapport disponible</p>';
        return;
    }
    
    const html = reports.map(report => `
        <div class="report-item">
            <h3>${report.contract_id || 'N/A'}</h3>
            <p><strong>ID:</strong> <code>${report.id}</code></p>
            <p><strong>Date:</strong> ${new Date(report.timestamp).toLocaleDateString('fr-FR')} à ${new Date(report.timestamp).toLocaleTimeString('fr-FR')}</p>
            <p><strong>Total FAX:</strong> ${report.total_fax || 0} | <strong>Erreurs:</strong> ${report.erreurs_totales || 0}</p>
            <p><strong>Taux réussite:</strong> ${(report.taux_reussite || 0).toFixed(1)}%</p>
            <a href="/report/${report.id}" class="btn">Consulter le rapport</a>
        </div>
    `).join('');
    
    document.getElementById('reportsList').innerHTML = html;
}

document.addEventListener('DOMContentLoaded', loadReports);
