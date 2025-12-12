/* ═══════════════════════════════════════════════════════════════════════════ */
/* FAXCLOUD ANALYZER - MAIN APPLICATION */
/* ═══════════════════════════════════════════════════════════════════════════ */

// Elements
const dragDropZone = document.getElementById('dragDropZone');
const fileInput = document.getElementById('fileInput');
const uploadProgress = document.getElementById('uploadProgress');
const resultSection = document.getElementById('resultSection');
const errorSection = document.getElementById('errorSection');
const reportsList = document.getElementById('reportsList');

// ═══════════════════════════════════════════════════════════════════════════
// DRAG & DROP HANDLERS
// ═══════════════════════════════════════════════════════════════════════════

dragDropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dragDropZone.classList.add('dragover');
});

dragDropZone.addEventListener('dragleave', () => {
    dragDropZone.classList.remove('dragover');
});

dragDropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dragDropZone.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        uploadFile(files[0]);
    }
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        uploadFile(e.target.files[0]);
    }
});

// ═══════════════════════════════════════════════════════════════════════════
// FILE UPLOAD
// ═══════════════════════════════════════════════════════════════════════════

function uploadFile(file) {
    // Validate file type
    const validTypes = ['.csv', '.xlsx', '.xls'];
    const fileExt = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
    
    if (!validTypes.includes(fileExt)) {
        showError('Format de fichier non supporté. Acceptés: CSV, XLSX');
        return;
    }
    
    // Show progress
    uploadProgress.classList.remove('hidden');
    resultSection.classList.add('hidden');
    errorSection.classList.add('hidden');
    
    // Upload file
    const formData = new FormData();
    formData.append('file', file);
    
    fetch('/api/import', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        uploadProgress.classList.add('hidden');
        
        if (data.success) {
            showResult(data);
            loadReports();
        } else {
            showError(data.error || 'Erreur lors de l\'import');
        }
    })
    .catch(err => {
        uploadProgress.classList.add('hidden');
        showError('Erreur réseau: ' + err.message);
    });
}

// ═══════════════════════════════════════════════════════════════════════════
// DISPLAY RESULTS
// ═══════════════════════════════════════════════════════════════════════════

function showResult(data) {
    const stats = data.stats || {};
    
    document.getElementById('totalFax').textContent = stats.total_fax || 0;
    document.getElementById('faxEnvoyes').textContent = stats.fax_envoyes || 0;
    document.getElementById('faxRecus').textContent = stats.fax_recus || 0;
    document.getElementById('errorsCount').textContent = stats.erreurs_totales || 0;
    document.getElementById('successRate').textContent = (stats.taux_reussite || 0).toFixed(1) + '%';
    document.getElementById('totalPages').textContent = stats.pages_totales || 0;
    
    document.getElementById('reportLink').href = data.report_url;
    
    resultSection.classList.remove('hidden');
}

function showError(message) {
    document.getElementById('errorText').textContent = message;
    errorSection.classList.remove('hidden');
}

// ═══════════════════════════════════════════════════════════════════════════
// LOAD REPORTS
// ═══════════════════════════════════════════════════════════════════════════

function loadReports() {
    fetch('/api/reports?limit=5')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayReports(data.reports, data.stats);
            }
        })
        .catch(err => console.error('Erreur chargement rapports:', err));
}

function displayReports(reports, stats) {
    if (!reports || reports.length === 0) {
        reportsList.innerHTML = '<p class="text-muted">Aucun rapport disponible</p>';
        return;
    }
    
    const html = reports.map(report => `
        <div class="report-item">
            <h3>${report.contract_id || 'N/A'}</h3>
            <p><strong>ID:</strong> ${report.id}</p>
            <p><strong>Date:</strong> ${new Date(report.timestamp).toLocaleDateString('fr-FR')}</p>
            <p><strong>Total FAX:</strong> ${report.total_fax || 0}</p>
            <p><strong>Taux réussite:</strong> ${(report.taux_reussite || 0).toFixed(1)}%</p>
            <a href="/report/${report.id}" class="btn">Voir le rapport</a>
        </div>
    `).join('');
    
    reportsList.innerHTML = html;
    
    // Update global stats
    if (stats) {
        document.getElementById('globReports').textContent = stats.total_reports || 0;
        document.getElementById('globTotalFax').textContent = stats.total_fax || 0;
        document.getElementById('globAvgRate').textContent = (stats.avg_success_rate || 0).toFixed(1) + '%';
    }
}

// ═══════════════════════════════════════════════════════════════════════════
// LOAD ANALYSES
// ═══════════════════════════════════════════════════════════════════════════

function loadAnalyses() {
    fetch('/api/analysis_history?limit=10&page=1')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayAnalyses(data.analyses);
            } else {
                console.error('Erreur chargement analyses:', data.error);
                document.getElementById('analysisList').innerHTML = '<p class="error">Erreur lors du chargement des analyses</p>';
            }
        })
        .catch(err => {
            console.error('Erreur chargement analyses:', err);
            document.getElementById('analysisList').innerHTML = '<p class="error">Erreur réseau lors du chargement des analyses</p>';
        });
}

function displayAnalyses(analyses) {
    const analysisList = document.getElementById('analysisList');
    
    if (!analyses || analyses.length === 0) {
        analysisList.innerHTML = '<p class="text-muted">Aucune analyse disponible</p>';
        return;
    }
    
    const html = analyses.map(analysis => `
        <div class="analysis-item">
            <h3>📁 ${analysis.fichier_source || 'Sans nom'}</h3>
            <p><strong>Date:</strong> ${new Date(analysis.date_analyse).toLocaleDateString('fr-FR', { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' })}</p>
            <div class="analysis-stats-simple">
                <div><strong>Total FAX:</strong> ${analysis.total_fax || 0}</div>
                <div><strong>Envoyés:</strong> ${analysis.fax_envoyes || 0}</div>
                <div><strong>Reçus:</strong> ${analysis.fax_recus || 0}</div>
                <div><strong>Erreurs:</strong> ${analysis.erreurs || 0}</div>
                <div><strong>Taux réussite:</strong> ${(analysis.taux_reussite || 0).toFixed(1)}%</div>
            </div>
            ${analysis.report_id ? `<a href="/report/${analysis.report_id}" class="btn btn-small">Voir le rapport</a>` : ''}
        </div>
    `).join('');
    
    analysisList.innerHTML = html;
}

// ═══════════════════════════════════════════════════════════════════════════
// INIT
// ═══════════════════════════════════════════════════════════════════════════

document.addEventListener('DOMContentLoaded', () => {
    loadAnalyses();
});
