/**
 * FaxCloud Analyzer - Import Simplifié avec Drag & Drop
 */

document.addEventListener('DOMContentLoaded', function() {
    const dragDropZone = document.getElementById('dragDropZone');
    const fileInput = document.getElementById('fileInput');
    const uploadProgress = document.getElementById('uploadProgress');
    const uploadStatus = document.getElementById('uploadStatus');
    const uploadResult = document.getElementById('uploadResult');
    const resultSection = document.getElementById('resultSection');
    const resultContent = document.getElementById('resultContent');

    // =========================================================================
    // DRAG & DROP
    // =========================================================================

    dragDropZone.addEventListener('click', () => fileInput.click());

    dragDropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        e.stopPropagation();
        dragDropZone.classList.add('dragover');
    });

    dragDropZone.addEventListener('dragleave', (e) => {
        e.preventDefault();
        e.stopPropagation();
        dragDropZone.classList.remove('dragover');
    });

    dragDropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        e.stopPropagation();
        dragDropZone.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            fileInput.files = files;
            uploadFile(files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            uploadFile(e.target.files[0]);
        }
    });

    // =========================================================================
    // UPLOAD
    // =========================================================================

    function uploadFile(file) {
        // Vérifier format
        if (!file.name.match(/\.(csv|xlsx|xls)$/i)) {
            showError('Format non supporté. Utilisez CSV ou XLSX.');
            return;
        }

        // Afficher progression
        uploadProgress.classList.remove('hidden');
        uploadResult.classList.add('hidden');
        resultSection.style.display = 'none';

        // Créer FormData
        const formData = new FormData();
        formData.append('file', file);
        // Pas de date ni de contrat ID requis

        // Envoyer
        fetch('/api/import', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showSuccess(data);
                setTimeout(() => loadReports(), 1000);
            } else {
                showError(data.message || 'Erreur lors de l\'analyse');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showError('Erreur réseau: ' + error.message);
        });
    }

    // =========================================================================
    // AFFICHAGE RÉSULTATS
    // =========================================================================

    function showSuccess(data) {
        uploadProgress.classList.add('hidden');
        
        const stats = data.statistics || {};
        const report = data.report || {};

        let html = `
            <div class="result-success">
                <h4>✓ Analyse Réussie!</h4>
                <p><strong>Rapport ID:</strong></p>
                <p class="report-id">${report.report_id || 'N/A'}</p>
            </div>

            <div class="result-stats">
                <div class="result-stat-card">
                    <h4>Total FAX</h4>
                    <p class="result-stat-value">${stats.total_fax || 0}</p>
                </div>
                <div class="result-stat-card">
                    <h4>Envoyés (SF)</h4>
                    <p class="result-stat-value">${stats.fax_envoyes || 0}</p>
                </div>
                <div class="result-stat-card">
                    <h4>Reçus (RF)</h4>
                    <p class="result-stat-value">${stats.fax_recus || 0}</p>
                </div>
                <div class="result-stat-card">
                    <h4>Pages</h4>
                    <p class="result-stat-value">${stats.pages_totales || 0}</p>
                </div>
                <div class="result-stat-card">
                    <h4>Erreurs</h4>
                    <p class="result-stat-value error">${stats.erreurs_totales || 0}</p>
                </div>
                <div class="result-stat-card">
                    <h4>Taux Réussite</h4>
                    <p class="result-stat-value success">${(stats.taux_reussite || 0).toFixed(1)}%</p>
                </div>
            </div>
        `;

        // Erreurs détaillées
        if (stats.erreurs_par_type && Object.keys(stats.erreurs_par_type).length > 0) {
            html += `<div class="result-errors">
                <h4>Détail des Erreurs:</h4>
                <ul>`;
            
            for (const [type, count] of Object.entries(stats.erreurs_par_type)) {
                if (count > 0) {
                    html += `<li>${type}: ${count}</li>`;
                }
            }
            
            html += `</ul></div>`;
        }

        resultContent.innerHTML = html;
        resultSection.style.display = 'block';
        uploadResult.innerHTML = '<p style="color: #28a745;">✓ Analyse terminée avec succès!</p>';
        uploadResult.classList.remove('hidden');
    }

    function showError(message) {
        uploadProgress.classList.add('hidden');
        uploadResult.innerHTML = `<p style="color: #dc3545;">✗ Erreur: ${message}</p>`;
        uploadResult.classList.remove('hidden');
    }

    // =========================================================================
    // CHARGEMENT RAPPORTS
    // =========================================================================

    function loadReports() {
        fetch('/api/reports')
            .then(response => response.json())
            .then(data => {
                if (data.success && data.reports) {
                    updateLatestReport(data.reports);
                    updateStats(data.reports);
                }
            })
            .catch(error => console.error('Error:', error));
    }

    function updateLatestReport(reports) {
        const latestReport = document.getElementById('latestReport');
        if (!reports || reports.length === 0) {
            latestReport.innerHTML = '<p class="text-muted">Aucun rapport</p>';
            return;
        }

        const latest = reports[0];
        latestReport.innerHTML = `
            <div style="background: white; padding: 1rem; border-radius: 8px; border-left: 4px solid #0066cc;">
                <p><strong>ID:</strong> ${latest.id}</p>
                <p><strong>Date:</strong> ${latest.date_rapport}</p>
                <p><strong>Contrat:</strong> ${latest.contract_id}</p>
                <p><strong>FAX:</strong> ${latest.total_fax}</p>
                <p><strong>Taux:</strong> <span style="color: #28a745;">${latest.taux_reussite.toFixed(1)}%</span></p>
            </div>
        `;
    }

    function updateStats(reports) {
        if (!reports || reports.length === 0) {
            return;
        }

        const totalReports = reports.length;
        const totalFax = reports.reduce((sum, r) => sum + (r.total_fax || 0), 0);
        const totalErrors = reports.reduce((sum, r) => sum + (r.erreurs_totales || 0), 0);
        const avgRate = reports.length > 0 
            ? reports.reduce((sum, r) => sum + (r.taux_reussite || 0), 0) / reports.length 
            : 0;

        document.getElementById('totalReports').textContent = totalReports;
        document.getElementById('totalFax').textContent = totalFax;
        document.getElementById('totalErrors').textContent = totalErrors;
        document.getElementById('avgSuccessRate').textContent = avgRate.toFixed(1) + '%';
    }

    // Charger les données au démarrage
    loadReports();
});
