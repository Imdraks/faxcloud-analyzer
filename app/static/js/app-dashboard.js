/* ═══════════════════════════════════════════════════════════════════════════ */
/* FAXCLOUD ANALYZER - DASHBOARD 2.0 */
/* ═══════════════════════════════════════════════════════════════════════════ */

class FaxDashboard {
    constructor() {
        this.init();
    }

    async fetchWithNgrokHeader(url, options = {}) {
        const headers = options.headers || {};
        headers['ngrok-skip-browser-warning'] = '69420';
        return fetch(url, { ...options, headers });
    }

    init() {
        this.setupClock();
        this.setupEventListeners();
        this.loadStats();
        this.loadReports();
        // Rafraîchir les stats toutes les 10 secondes
        setInterval(() => {
            this.loadStats();
            this.loadReports();
        }, 10000);
    }

    setupClock() {
        const updateTime = () => {
            const now = new Date();
            document.getElementById('currentTime').textContent = now.toLocaleTimeString('fr-FR');
        };
        updateTime();
        setInterval(updateTime, 1000);
    }

    setupEventListeners() {
        const fileInput = document.getElementById('fileInput');
        const dragDropZone = document.getElementById('dragDropZone');

        fileInput.addEventListener('change', (e) => this.handleFileSelect(e.target.files[0]));

        dragDropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dragDropZone.style.borderColor = 'rgba(59, 130, 246, 1)';
            dragDropZone.style.background = 'linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(139, 92, 246, 0.05))';
        });

        dragDropZone.addEventListener('dragleave', () => {
            dragDropZone.style.borderColor = 'rgba(59, 130, 246, 0.5)';
            dragDropZone.style.background = 'linear-gradient(135deg, rgba(59, 130, 246, 0.05), rgba(139, 92, 246, 0.02))';
        });

        dragDropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dragDropZone.style.borderColor = 'rgba(59, 130, 246, 0.5)';
            dragDropZone.style.background = 'linear-gradient(135deg, rgba(59, 130, 246, 0.05), rgba(139, 92, 246, 0.02))';
            const file = e.dataTransfer.files[0];
            if (file) this.handleFileSelect(file);
        });
    }

    handleFileSelect(file) {
        if (!file) return;

        if (!['text/csv', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'].includes(file.type) && !file.name.endsWith('.csv') && !file.name.endsWith('.xlsx')) {
            this.showMessage('error', '❌ Format non supporté. Utilisez CSV ou XLSX.');
            return;
        }

        if (file.size > 100 * 1024 * 1024) {
            this.showMessage('error', '❌ Fichier trop volumineux (max 100MB)');
            return;
        }

        this.uploadFile(file);
    }

    async uploadFile(file) {
        try {
            console.log('🎯 Upload lancé');
            
            // Afficher la barre de progression
            const progressDiv = document.getElementById('uploadProgress');
            progressDiv.classList.remove('hidden');
            document.getElementById('progressFill').style.width = '0%';
            document.getElementById('progressText').textContent = '0% - Préparation...';

            // Préparer le formulaire
            const formData = new FormData();
            formData.append('file', file);

            // Envoyer le fichier
            const xhr = new XMLHttpRequest();

            xhr.upload.addEventListener('progress', (e) => {
                if (e.lengthComputable) {
                    const percent = Math.round((e.loaded / e.total) * 50);
                    document.getElementById('progressFill').style.width = percent + '%';
                    document.getElementById('progressText').textContent = `${percent}% - Upload du fichier...`;
                }
            });

            xhr.addEventListener('load', () => {
                if (xhr.status === 200) {
                    try {
                        const data = JSON.parse(xhr.responseText);
                        console.log('✅ Upload réussi:', data);
                        
                        if (data.success) {
                            // Montrer 100%
                            document.getElementById('progressFill').style.width = '100%';
                            document.getElementById('progressText').textContent = '100% - Redirection...';
                            
                            // Succès!
                            this.showMessage('success', `✅ ${data.message}`);
                            document.getElementById('fileInput').value = '';
                            
                            // Mettre à jour l'interface
                            this.loadStats();
                            this.loadReports();
                            
                            // REDIRECTION DIRECTE VERS LE RAPPORT
                            console.log('🚀 Redirection vers /report/' + data.report_id);
                            setTimeout(() => {
                                window.location.href = `/report/${data.report_id}`;
                            }, 800);
                        } else {
                            this.showMessage('error', `❌ ${data.error || 'Erreur inconnue'}`);
                        }
                    } catch (e) {
                        this.showMessage('error', `❌ Erreur: ${e.message}`);
                    }
                } else {
                    this.showMessage('error', `❌ Erreur HTTP ${xhr.status}`);
                }
                document.getElementById('uploadProgress').classList.add('hidden');
            });

            xhr.addEventListener('error', () => {
                this.showMessage('error', '❌ Erreur réseau');
                document.getElementById('uploadProgress').classList.add('hidden');
            });

            xhr.open('POST', '/api/upload');
            xhr.send(formData);

        } catch (error) {
            console.error('❌ Erreur upload:', error);
            this.showMessage('error', `❌ ${error.message}`);
        }
    }
                });

                xhr.open('POST', '/api/upload', true);
                xhr.setRequestHeader('ngrok-skip-browser-warning', '69420');
                xhr.send(formData);
            });
        } catch (error) {
            this.showMessage('error', `❌ Erreur: ${error.message}`);
            document.getElementById('uploadProgress').classList.add('hidden');
        }
    }

    async loadStats() {
        try {
            const response = await this.fetchWithNgrokHeader('/api/stats');
            const data = await response.json();

            document.getElementById('totalFaxStat').textContent = (data.total || 0).toLocaleString('fr-FR');
            document.getElementById('sentFaxStat').textContent = (data.sent || 0).toLocaleString('fr-FR');
            document.getElementById('receivedFaxStat').textContent = (data.received || 0).toLocaleString('fr-FR');
            document.getElementById('errorFaxStat').textContent = (data.errors || 0).toLocaleString('fr-FR');

            const total = data.total || 1;
            document.getElementById('sentPercent').textContent = Math.round((data.sent / total) * 100) + '%';
            document.getElementById('receivedPercent').textContent = Math.round((data.received / total) * 100) + '%';
            document.getElementById('errorPercent').textContent = Math.round((data.errors / total) * 100) + '%';
        } catch (error) {
            console.error('Erreur stats:', error);
        }
    }

    async loadReports() {
        try {
            const response = await this.fetchWithNgrokHeader('/api/latest-reports');
            const data = await response.json();

            const container = document.getElementById('reportsContainer');
            container.innerHTML = '';

            if (!data.reports || data.reports.length === 0) {
                container.innerHTML = `
                    <div class="no-reports">
                        <div style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.3;">📭</div>
                        <p>Aucun rapport pour le moment</p>
                    </div>
                `;
                return;
            }

            data.reports.slice(0, 6).forEach(report => {
                let dateStr = '-';
                if (report.date_rapport) {
                    try {
                        const date = new Date(report.date_rapport);
                        if (!isNaN(date.getTime())) {
                            dateStr = date.toLocaleDateString('fr-FR', {
                                year: 'numeric',
                                month: '2-digit',
                                day: '2-digit',
                                hour: '2-digit',
                                minute: '2-digit'
                            });
                        }
                    } catch (e) {
                        console.error('Erreur date:', e);
                    }
                }

                const total = report.total_fax || 1;
                const success = (report.total_fax - (report.erreurs || 0)) || 0;
                const successRate = Math.round((success / total) * 100);

                const card = document.createElement('div');
                card.className = 'report-card';
                card.innerHTML = `
                    <div class="report-card-content">
                        <div class="report-date">📅 ${dateStr}</div>

                        <div class="report-stats">
                            <div class="stat-item">
                                <div class="stat-label">Total</div>
                                <div class="stat-value">${(report.total_fax || 0).toLocaleString('fr-FR')}</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-label">Envoyés</div>
                                <div class="stat-value">${(report.fax_envoyes || 0).toLocaleString('fr-FR')}</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-label">Reçus</div>
                                <div class="stat-value">${(report.fax_recus || 0).toLocaleString('fr-FR')}</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-label">Erreurs</div>
                                <div class="stat-value" style="color: ${report.erreurs > 0 ? '#ef4444' : '#10b981'}">${(report.erreurs || 0).toLocaleString('fr-FR')}</div>
                            </div>
                        </div>

                        <div style="background: rgba(0,0,0,0.2); padding: 0.75rem; border-radius: 8px; margin: 1rem 0; text-align: center;">
                            <div style="font-size: 0.7rem; opacity: 0.7; text-transform: uppercase; margin-bottom: 0.2rem;">Taux de Réussite</div>
                            <div style="font-size: 1.4rem; font-weight: 700; color: ${successRate >= 90 ? '#10b981' : successRate >= 70 ? '#f59e0b' : '#ef4444'}">${successRate}%</div>
                        </div>

                        <div class="report-actions">
                            <button class="report-btn report-btn-primary" onclick="window.location.href='/report/${report.report_id}'">
                                📊 Voir
                            </button>
                            <button class="report-btn report-btn-secondary" onclick="downloadPDF('${report.report_id}')">
                                📥 PDF
                            </button>
                        </div>
                    </div>
                `;
                container.appendChild(card);
            });
        } catch (error) {
            console.error('Erreur reports:', error);
        }
    }

    showMessage(type, message) {
        const msgDiv = document.getElementById('uploadMessage');
        msgDiv.innerHTML = `
            <div style="
                background: ${type === 'success' ? 'rgba(16, 185, 129, 0.2)' : 'rgba(239, 68, 68, 0.2)'};
                border: 1px solid ${type === 'success' ? 'rgba(16, 185, 129, 0.5)' : 'rgba(239, 68, 68, 0.5)'};
                border-radius: 12px;
                padding: 1rem;
                color: ${type === 'success' ? '#10b981' : '#ef4444'};
                font-weight: 500;
                animation: slideIn 0.3s ease;
            ">${message}</div>
        `;
        setTimeout(() => {
            msgDiv.innerHTML = '';
        }, 5000);
    }
}

// Fonctions globales
function downloadPDF(reportId) {
    window.location.href = `/api/report/${reportId}/pdf`;
}

function clearAllData() {
    if (!confirm('⚠️ Êtes-vous sûr? Cette action est irréversible!')) return;

    fetch('/api/clear', {
        method: 'POST',
        headers: { 'ngrok-skip-browser-warning': '69420' }
    })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                alert('✅ Données effacées');
                window.location.reload();
            } else {
                alert('❌ Erreur: ' + data.error);
            }
        })
        .catch(e => alert('❌ Erreur: ' + e.message));
}

function exportAllReports() {
    alert('📥 Fonctionnalité en développement');
}

function showDetailedStats() {
    alert('📊 Statistiques détaillées en développement');
}

// Initialiser au chargement
document.addEventListener('DOMContentLoaded', () => {
    new FaxDashboard();
});

// Animation slideIn
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(-10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
`;
document.head.appendChild(style);
