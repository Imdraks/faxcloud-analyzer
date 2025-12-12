/* Report page */

let allEntries = [];
let currentFilter = 'all';

function loadReport() {
    const reportId = window.location.pathname.split('/').pop();
    
    fetch(`/api/report/${reportId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayReport(data);
                loadEntries(reportId);
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
            <div class="report-header">
                <div class="report-info">
                    <h2>Rapport #${(report.rapport_id || report.report_id || 'N/A').substring(0, 8)}</h2>
                    
                    <div class="report-details">
                        <p><strong>Contrat:</strong> ${report.contract_id}</p>
                        <p><strong>Période:</strong> ${report.date_debut} à ${report.date_fin}</p>
                        <p><strong>Date de génération:</strong> ${new Date(report.timestamp).toLocaleDateString('fr-FR')}</p>
                    </div>
                </div>
                ${report.qr_path ? `
                <div class="report-qrcode">
                    <img src="/qrcode/${report.rapport_id}" alt="QR Code" title="Scannez ce code QR pour accéder au rapport">
                    <small>Scanner pour accéder</small>
                </div>
                ` : ''}
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

function loadEntries(reportId) {
    // Ajouter un loader
    let content = document.getElementById('reportContent');
    const loaderHtml = `
        <div id="entries-section" class="entries-section">
            <h3>Détail des entrées</h3>
            <div class="loader">
                <div class="spinner"></div>
                <p>Chargement des entrées...</p>
            </div>
        </div>
    `;
    content.innerHTML += loaderHtml;
    
    fetch(`/api/report/${reportId}/entries`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                allEntries = data.entries || [];
                displayEntries('all');
            } else {
                document.getElementById('entries-section').innerHTML = 
                    '<p class="error">Erreur lors du chargement des entrées</p>';
            }
        })
        .catch(err => {
            console.error('Erreur chargement entrées:', err);
            document.getElementById('entries-section').innerHTML = 
                '<p class="error">Erreur: ' + err.message + '</p>';
        });
}

function displayEntries(filter) {
    currentFilter = filter;
    
    let filteredEntries = allEntries;
    
    if (filter === 'sent') {
        filteredEntries = allEntries.filter(e => e.mode === 'SF');
    } else if (filter === 'received') {
        filteredEntries = allEntries.filter(e => e.mode === 'RF');
    } else if (filter === 'errors') {
        filteredEntries = allEntries.filter(e => !e.valide);
    }
    
    const filterButtons = `
        <div class="filter-buttons">
            <button class="btn ${filter === 'all' ? 'active' : ''}" onclick="displayEntries('all')">
                📋 Tous (${allEntries.length})
            </button>
            <button class="btn ${filter === 'sent' ? 'active' : ''}" onclick="displayEntries('sent')">
                📤 Envoyés (${allEntries.filter(e => e.mode === 'SF').length})
            </button>
            <button class="btn ${filter === 'received' ? 'active' : ''}" onclick="displayEntries('received')">
                📥 Reçus (${allEntries.filter(e => e.mode === 'RF').length})
            </button>
            <button class="btn ${filter === 'errors' ? 'active' : ''}" onclick="displayEntries('errors')">
                ⚠️ Erreurs (${allEntries.filter(e => !e.valide).length})
            </button>
        </div>
    `;
    
    let entriesHtml = `
        <h3>Détail des entrées - ${filteredEntries.length} ligne(s)</h3>
        ${filterButtons}
        <div class="entries-list">
    `;
    
    if (filteredEntries.length === 0) {
        entriesHtml += '<p class="text-muted">Aucune entrée à afficher</p>';
    } else {
        entriesHtml += '<table class="entries-table"><thead><tr>' +
            '<th>FAX ID</th>' +
            '<th>Utilisateur</th>' +
            '<th>Mode</th>' +
            '<th>Date/Heure</th>' +
            '<th>Numéro</th>' +
            '<th>Pages</th>' +
            '<th>Statut</th>' +
            '</tr></thead><tbody>';
        
        filteredEntries.forEach(entry => {
            const statusClass = entry.valide ? 'success' : 'error';
            const statusText = entry.valide ? '✓ OK' : '✗ Erreur';
            const errorsText = entry.erreurs ? entry.erreurs.join('<br>') : '';
            
            entriesHtml += `
                <tr class="${statusClass}">
                    <td>${entry.fax_id || '-'}</td>
                    <td>${entry.utilisateur || '-'}</td>
                    <td>${entry.mode || '-'}</td>
                    <td>${entry.date_heure ? new Date(entry.date_heure).toLocaleString('fr-FR') : '-'}</td>
                    <td>${entry.numero_normalise || entry.numero || '-'}</td>
                    <td>${entry.pages || 0}</td>
                    <td>
                        <span class="status ${statusClass}">${statusText}</span>
                        ${errorsText ? `<div class="error-details">${errorsText}</div>` : ''}
                    </td>
                </tr>
            `;
        });
        
        entriesHtml += '</tbody></table>';
    }
    
    entriesHtml += '</div>';
    
    // Remplacer le contenu de la section entries
    let entriesSection = document.getElementById('entries-section');
    if (entriesSection) {
        entriesSection.innerHTML = entriesHtml;
    }
}

document.addEventListener('DOMContentLoaded', loadReport);
