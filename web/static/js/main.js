// FaxCloud Analyzer - Main Script

document.addEventListener('DOMContentLoaded', function() {
    // Initialiser les dates
    const today = new Date();
    const firstDay = new Date(today.getFullYear(), today.getMonth(), 1);
    const lastDay = new Date(today.getFullYear(), today.getMonth() + 1, 0);
    
    document.getElementById('dateDebut').valueAsDate = firstDay;
    document.getElementById('dateFin').valueAsDate = today;
    
    // Charger les statistiques globales
    loadGlobalStats();
    
    // Charger le dernier rapport
    loadLatestReport();
    
    // Gestion du formulaire
    document.getElementById('uploadForm').addEventListener('submit', handleFileUpload);
    
    // Gestion de l'input file
    const fileInput = document.getElementById('fileInput');
    const fileLabel = document.querySelector('.file-input-label');
    
    fileInput.addEventListener('change', function(e) {
        if (this.files.length > 0) {
            fileLabel.textContent = this.files[0].name;
        }
    });
});

// Charger les statistiques globales
function loadGlobalStats() {
    fetch('/api/reports')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const stats = data.stats;
                document.getElementById('totalReports').textContent = stats.total_reports;
                document.getElementById('totalFax').textContent = stats.total_fax;
                document.getElementById('totalErrors').textContent = stats.total_errors;
                document.getElementById('avgSuccessRate').textContent = stats.avg_success_rate.toFixed(1) + '%';
            }
        })
        .catch(error => console.error('Erreur:', error));
}

// Charger le dernier rapport
function loadLatestReport() {
    fetch('/api/reports?limit=1')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.reports.length > 0) {
                const report = data.reports[0];
                const html = `
                    <div style="padding: 16px 0;">
                        <h3>📋 ${report.id}</h3>
                        <p><strong>Contrat:</strong> ${report.contract_id}</p>
                        <p><strong>Généré:</strong> ${new Date(report.date_rapport).toLocaleString('fr-FR')}</p>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 16px;">
                            <div>
                                <strong>FAX:</strong> ${report.total_fax}
                                <p style="font-size: 0.9rem; margin-top: 4px;">
                                    Envoyés: ${report.fax_envoyes} | Reçus: ${report.fax_recus}
                                </p>
                            </div>
                            <div>
                                <strong>Réussite:</strong> ${report.taux_reussite.toFixed(1)}%
                                <p style="font-size: 0.9rem; margin-top: 4px;">
                                    Erreurs: ${report.erreurs}
                                </p>
                            </div>
                        </div>
                        <a href="/report/${report.id}" class="btn btn-primary" style="margin-top: 16px;">Consulter</a>
                    </div>
                `;
                document.getElementById('latestReport').innerHTML = html;
            } else {
                document.getElementById('latestReport').innerHTML = '<p class="text-muted">Aucun rapport disponible</p>';
            }
        })
        .catch(error => console.error('Erreur:', error));
}

// Gérer l'upload de fichier
function handleFileUpload(e) {
    e.preventDefault();
    
    const fileInput = document.getElementById('fileInput');
    const contractId = document.getElementById('contractId').value;
    const dateDebut = document.getElementById('dateDebut').value;
    const dateFin = document.getElementById('dateFin').value;
    
    if (!fileInput.files.length) {
        showError('Veuillez sélectionner un fichier');
        return;
    }
    
    // Afficher la progression
    const progressDiv = document.getElementById('uploadProgress');
    const resultDiv = document.getElementById('uploadResult');
    progressDiv.classList.remove('hidden');
    resultDiv.classList.add('hidden');
    
    // Créer FormData
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    formData.append('contract_id', contractId);
    formData.append('date_debut', dateDebut);
    formData.append('date_fin', dateFin);
    
    // Envoyer le fichier
    fetch('/api/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        progressDiv.classList.add('hidden');
        
        if (data.success) {
            showSuccess(
                `Rapport généré avec succès!<br>` +
                `ID: ${data.rapport_id}<br>` +
                `<a href="/report/${data.rapport_id}" class="btn btn-primary" style="margin-top: 8px;">Consulter le rapport</a>`
            );
            
            // Réinitialiser le formulaire
            document.getElementById('uploadForm').reset();
            document.querySelector('.file-input-label').textContent = 'Choisir un fichier...';
            
            // Recharger les statistiques
            loadGlobalStats();
            loadLatestReport();
        } else {
            showError('Erreur: ' + data.error);
        }
    })
    .catch(error => {
        progressDiv.classList.add('hidden');
        showError('Erreur: ' + error.message);
    });
}

// Afficher une erreur
function showError(message) {
    const resultDiv = document.getElementById('uploadResult');
    resultDiv.classList.remove('success', 'hidden');
    resultDiv.classList.add('error');
    resultDiv.innerHTML = `❌ ${message}`;
}

// Afficher un succès
function showSuccess(message) {
    const resultDiv = document.getElementById('uploadResult');
    resultDiv.classList.remove('error', 'hidden');
    resultDiv.classList.add('success');
    resultDiv.innerHTML = `✅ ${message}`;
}
