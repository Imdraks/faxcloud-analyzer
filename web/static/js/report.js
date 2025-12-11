// FaxCloud Analyzer - Report Detail Page Script

document.addEventListener('DOMContentLoaded', function() {
    const reportId = getReportIdFromUrl();
    
    if (reportId) {
        loadReport(reportId);
    }
});

function getReportIdFromUrl() {
    const path = window.location.pathname;
    const match = path.match(/\/report\/([a-f0-9\-]+)$/);
    return match ? match[1] : null;
}

function loadReport(reportId) {
    fetch(`/api/report/${reportId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayReport(data.report);
                displayErrors(data.entries.filter(e => !e.valide));
            }
        })
        .catch(error => console.error('Erreur:', error));
}

function displayReport(report) {
    const stats = report.statistics;
    
    const html = `
        <div class="report-header">
            <div>
                <h3>Informations</h3>
                <p><strong>Rapport ID:</strong> ${report.rapport_id}</p>
                <p><strong>Contrat:</strong> ${report.contract_id}</p>
                <p><strong>Généré:</strong> ${new Date(report.timestamp).toLocaleString('fr-FR')}</p>
                <p><strong>Période:</strong> ${report.date_debut} à ${report.date_fin}</p>
            </div>
            <div style="text-align: right;">
                ${report.qr_path ? `<img src="${report.qr_path}" alt="QR Code" style="max-width: 200px; border: 1px solid #ddd; padding: 8px; border-radius: 8px;">` : ''}
            </div>
        </div>

        <h3 style="margin-top: 24px; margin-bottom: 16px;">📊 Statistiques FAX</h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px;">
            <div class="report-stat">
                <span class="report-stat-label">Total FAX</span>
                <span class="report-stat-value">${stats.total_fax}</span>
            </div>
            <div class="report-stat">
                <span class="report-stat-label">Envoyés (SF)</span>
                <span class="report-stat-value">${stats.fax_envoyes}</span>
            </div>
            <div class="report-stat">
                <span class="report-stat-label">Reçus (RF)</span>
                <span class="report-stat-value">${stats.fax_recus}</span>
            </div>
            <div class="report-stat">
                <span class="report-stat-label">Pages Totales</span>
                <span class="report-stat-value">${stats.pages_totales}</span>
            </div>
            <div class="report-stat">
                <span class="report-stat-label">Pages Envoyées</span>
                <span class="report-stat-value">${stats.pages_envoyees}</span>
            </div>
            <div class="report-stat">
                <span class="report-stat-label">Pages Reçues</span>
                <span class="report-stat-value">${stats.pages_recues}</span>
            </div>
        </div>

        <h3 style="margin-top: 24px; margin-bottom: 16px;">⚠️ Qualité et Erreurs</h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px;">
            <div class="report-stat">
                <span class="report-stat-label">Taux de Réussite</span>
                <span class="report-stat-value" style="color: ${stats.taux_reussite >= 95 ? '#28a745' : stats.taux_reussite >= 80 ? '#ffc107' : '#dc3545'};">
                    ${stats.taux_reussite.toFixed(2)}%
                </span>
            </div>
            <div class="report-stat">
                <span class="report-stat-label">Erreurs Détectées</span>
                <span class="report-stat-value" style="color: ${stats.erreurs_totales > 0 ? '#dc3545' : '#28a745'};">
                    ${stats.erreurs_totales}
                </span>
            </div>
        </div>
    `;
    
    document.getElementById('reportContent').innerHTML = html;
}

function displayErrors(errors) {
    if (errors.length === 0) {
        return;
    }
    
    const section = document.getElementById('errorsSection');
    section.style.display = 'block';
    
    const html = errors.slice(0, 50).map(entry => `
        <div class="error-item">
            <h4>FAX ${entry.fax_id} - ${entry.utilisateur}</h4>
            <p><strong>Numéro:</strong> ${entry.numero_original}</p>
            <p><strong>Mode:</strong> ${entry.mode}</p>
            <p><strong>Erreurs:</strong> ${entry.erreurs.join(', ')}</p>
        </div>
    `).join('');
    
    if (errors.length > 50) {
        html += `<p class="text-muted" style="text-align: center; margin-top: 16px;">... et ${errors.length - 50} autres erreurs</p>`;
    }
    
    document.getElementById('errorsList').innerHTML = html;
}
