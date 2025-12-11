/* Report page */

function loadReport() {
    const reportId = window.location.pathname.split('/').pop();
    
    fetch(`/api/report/${reportId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayReport(data);
            } else {
                document.getElementById('reportContent').innerHTML = 
                    '<p class="error">Rapport non trouvé</p>';
            }
        })
        .catch(err => {
            document.getElementById('reportContent').innerHTML = 
                '<p class="error">Erreur: ' + err.message + '</p>';
        });
}

function displayReport(data) {
    const report = data.report;
    const stats = report.statistics || {};
    
    const html = `
        <div class="section">
            <h2>Rapport #${(report.rapport_id || report.report_id || 'N/A').substring(0, 8)}</h2>
            
            <div class="report-details">
                <p><strong>Contrat:</strong> ${report.contract_id}</p>
                <p><strong>Période:</strong> ${report.date_debut} à ${report.date_fin}</p>
                <p><strong>Date de génération:</strong> ${new Date(report.timestamp).toLocaleDateString('fr-FR')}</p>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <h4>Total FAX</h4>
                    <p class="stat-value">${stats.total_fax || 0}</p>
                </div>
                <div class="stat-card">
                    <h4>Envoyés</h4>
                    <p class="stat-value">${stats.fax_envoyes || 0}</p>
                </div>
                <div class="stat-card">
                    <h4>Reçus</h4>
                    <p class="stat-value">${stats.fax_recus || 0}</p>
                </div>
                <div class="stat-card">
                    <h4>Erreurs</h4>
                    <p class="stat-value">${stats.erreurs_totales || 0}</p>
                </div>
                <div class="stat-card">
                    <h4>Pages</h4>
                    <p class="stat-value">${stats.pages_totales || 0}</p>
                </div>
                <div class="stat-card">
                    <h4>Taux réussite</h4>
                    <p class="stat-value">${(stats.taux_reussite || 0).toFixed(1)}%</p>
                </div>
            </div>
            
            <h3>Résumé</h3>
            <table class="table">
                <tr>
                    <td>Total FAX:</td>
                    <td>${stats.total_fax || 0}</td>
                </tr>
                <tr>
                    <td>Erreurs totales:</td>
                    <td>${stats.erreurs_totales || 0}</td>
                </tr>
                <tr>
                    <td>Taux de réussite:</td>
                    <td>${(stats.taux_reussite || 0).toFixed(2)}%</td>
                </tr>
            </table>
        </div>
    `;
    
    document.getElementById('reportContent').innerHTML = html;
}

document.addEventListener('DOMContentLoaded', loadReport);
