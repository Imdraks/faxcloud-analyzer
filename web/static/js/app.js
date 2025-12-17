/* ═══════════════════════════════════════════════════════════════════════════ */
/* FAXCLOUD ANALYZER - MAIN APPLICATION */
/* ═══════════════════════════════════════════════════════════════════════════ */

class FaxApp {
    constructor() {
        this.currentFilter = 'all';
        this.init();
    }

    // Helper pour les requêtes fetch avec header ngrok
    async fetchWithNgrokHeader(url, options = {}) {
        const headers = options.headers || {};
        headers['ngrok-skip-browser-warning'] = '69420';
        return fetch(url, { ...options, headers });
    }

    init() {
        this.setupEventListeners();
        this.loadStats();
        this.loadReports();
    }

    setupEventListeners() {
        // File input
        const fileInput = document.getElementById('fileInput');
        const dragDropZone = document.getElementById('dragDropZone');

        fileInput.addEventListener('change', (e) => this.handleFileSelect(e.target.files[0]));

        // Drag and drop
        dragDropZone.addEventListener('dragover', (e) => this.handleDragOver(e));
        dragDropZone.addEventListener('dragleave', (e) => this.handleDragLeave(e));
        dragDropZone.addEventListener('drop', (e) => this.handleDrop(e));

        // Filter buttons
        document.querySelectorAll('.filter-buttons .btn').forEach(btn => {
            btn.addEventListener('click', () => this.setFilter(btn.dataset.filter, btn));
        });

        // Clear button
        document.getElementById('clearBtn').addEventListener('click', () => this.clearData());
    }

    handleFileSelect(file) {
        if (!file) return;
        this.uploadFile(file);
    }

    handleDragOver(e) {
        e.preventDefault();
        e.stopPropagation();
        document.getElementById('dragDropZone').classList.add('drag-over');
    }

    handleDragLeave(e) {
        e.preventDefault();
        e.stopPropagation();
        document.getElementById('dragDropZone').classList.remove('drag-over');
    }

    handleDrop(e) {
        e.preventDefault();
        e.stopPropagation();
        document.getElementById('dragDropZone').classList.remove('drag-over');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            this.uploadFile(files[0]);
        }
    }

    async uploadFile(file) {
        try {
            // Générer une session_id unique
            const sessionId = 'upload_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
            
            // Afficher la barre de progression
            const progressDiv = document.getElementById('uploadProgress');
            progressDiv.classList.remove('hidden');

            // Ouvrir la connexion SSE AVANT d'uploader
            const eventSource = new EventSource(`/api/upload-progress/${sessionId}`);
            
            eventSource.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    const percent = data.percent || 0;
                    const step = data.step || 'Traitement';
                    const message = data.message || '';
                    
                    document.getElementById('progressFill').style.width = percent + '%';
                    document.getElementById('progressText').textContent = percent + '% - ' + step;
                    
                    // Fermer la SSE à 100%
                    if (percent >= 100) {
                        eventSource.close();
                    }
                } catch (e) {
                    console.error('Erreur parsing SSE:', e);
                }
            };
            
            eventSource.onerror = () => {
                console.error('Erreur SSE');
                eventSource.close();
            };

            // PUIS envoyer l'upload avec XMLHttpRequest (0-30%)
            const formData = new FormData();
            formData.append('file', file);
            formData.append('session_id', sessionId);

            return new Promise((resolve, reject) => {
                const xhr = new XMLHttpRequest();

                // Événement de progression UPLOAD (0-30%)
                xhr.upload.addEventListener('progress', (e) => {
                    if (e.lengthComputable) {
                        const percentComplete = Math.round((e.loaded / e.total) * 30); // Max 30%
                        document.getElementById('progressFill').style.width = percentComplete + '%';
                        document.getElementById('progressText').textContent = percentComplete + '% - Upload du fichier';
                    }
                });

                xhr.addEventListener('load', () => {
                    if (xhr.status === 200) {
                        try {
                            const data = JSON.parse(xhr.responseText);
                            if (data.success) {
                                // SSE va continuer jusqu'à 100%
                                setTimeout(() => {
                                    window.location.href = `/report/${data.report_id}`;
                                }, 2000); // Attendre que SSE atteigne 100%
                            } else {
                                this.showMessage('error', `✗ Erreur: ${data.error}`);
                                eventSource.close();
                            }
                        } catch (e) {
                            this.showMessage('error', `✗ Erreur parse: ${e.message}`);
                            eventSource.close();
                        }
                        resolve();
                    } else {
                        reject(new Error(`HTTP ${xhr.status}`));
                        eventSource.close();
                    }
                });

                xhr.addEventListener('error', () => {
                    reject(new Error('Erreur réseau'));
                    eventSource.close();
                });

                xhr.addEventListener('abort', () => {
                    reject(new Error('Upload annulé'));
                    eventSource.close();
                });

                xhr.open('POST', '/api/upload', true);
                xhr.setRequestHeader('ngrok-skip-browser-warning', '69420');
                xhr.send(formData);
            }).finally(() => {
                // Garder la barre visible jusqu'à ce que SSE la ferme
            });
        } catch (error) {
            this.showMessage('error', `✗ Erreur upload: ${error.message}`);
            document.getElementById('uploadProgress').classList.add('hidden');
        }
    }

    async loadStats() {
        try {
            const response = await this.fetchWithNgrokHeader('/api/stats');
            const stats = await response.json();

            document.getElementById('totalFax').textContent = stats.total || 0;
            document.getElementById('sentFax').textContent = stats.sent || 0;
            document.getElementById('receivedFax').textContent = stats.received || 0;
            document.getElementById('errorFax').textContent = stats.errors || 0;
        } catch (error) {
            console.error('Erreur stats:', error);
        }
    }

    async loadReports() {
        try {
            const response = await this.fetchWithNgrokHeader('/api/latest-reports');
            const data = await response.json();

            const container = document.getElementById('reportsContainer');
            const countSpan = document.getElementById('reportsCount');
            container.innerHTML = '';

            if (!data.reports || data.reports.length === 0) {
                container.innerHTML = `
                    <div class="no-reports">
                        <div class="no-reports-icon">📭</div>
                        <p>Aucun rapport pour le moment</p>
                        <p style="font-size: 0.9rem; margin-top: 0.5rem;">Importez un fichier CSV pour commencer</p>
                    </div>
                `;
                countSpan.textContent = '0 rapport(s)';
                return;
            }

            countSpan.textContent = `${data.reports.length} rapport(s)`;

            data.reports.forEach(report => {
                // Formater la date
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
                        console.error('Erreur parsing date rapport:', e);
                    }
                }

                // Calculer le taux de réussite
                const total = report.total_fax || 1;
                const reussi = (report.total_fax - (report.erreurs || 0)) || 0;
                const tauxReussite = Math.round((reussi / total) * 100);

                // Créer la card
                const card = document.createElement('div');
                card.className = 'report-card';
                card.innerHTML = `
                    <div class="report-card-content">
                        <div class="report-date">
                            <span>📅</span>
                            <span>${dateStr}</span>
                        </div>
                        
                        <div class="report-stats">
                            <div class="stat-item">
                                <div class="stat-label">Total</div>
                                <div class="stat-value">${report.total_fax || 0}</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-label">Envoyés</div>
                                <div class="stat-value">${report.fax_envoyes || 0}</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-label">Reçus</div>
                                <div class="stat-value">${report.fax_recus || 0}</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-label">Erreurs</div>
                                <div class="stat-value" style="color: ${report.erreurs > 0 ? '#ef4444' : '#10b981'}">${report.erreurs || 0}</div>
                            </div>
                        </div>

                        <div style="background: rgba(0,0,0,0.2); padding: 0.75rem; border-radius: 10px; margin: 1rem 0; text-align: center;">
                            <div style="font-size: 0.75rem; opacity: 0.7; text-transform: uppercase; margin-bottom: 0.3rem;">Taux de Réussite</div>
                            <div style="font-size: 1.5rem; font-weight: 700; color: ${tauxReussite >= 90 ? '#10b981' : tauxReussite >= 70 ? '#f59e0b' : '#ef4444'}">${tauxReussite}%</div>
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
    }

    setFilter(filter, btn) {
        // Non utilisé pour les rapports (pas de filtres)
    }

    async clearData() {
        if (!confirm('⚠️ Êtes-vous sûr? Toutes les données seront effacées de manière permanente.')) {
            return;
        }

        try {
            const response = await this.fetchWithNgrokHeader('/api/clear', { method: 'POST' });
            const data = await response.json();

            if (data.success) {
                this.showMessage('success', '✓ Données effacées');
                this.loadStats();
                this.loadReports();
            }
        } catch (error) {
            this.showMessage('error', `✗ Erreur: ${error.message}`);
        }
    }

    showMessage(type, message) {
        const msgDiv = document.getElementById('uploadMessage');
        msgDiv.innerHTML = `<div class="${type}">${message}</div>`;
        setTimeout(() => {
            msgDiv.innerHTML = '';
        }, 5000);
    }
}

// Initialiser l'app au chargement
document.addEventListener('DOMContentLoaded', () => {
    new FaxApp();
});
