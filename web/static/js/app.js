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
            // Afficher la barre de progression
            const progressDiv = document.getElementById('uploadProgress');
            progressDiv.classList.remove('hidden');

            // Utiliser XMLHttpRequest pour avoir les événements de progression
            const formData = new FormData();
            formData.append('file', file);

            return new Promise((resolve, reject) => {
                const xhr = new XMLHttpRequest();

                // Événement de progression
                xhr.upload.addEventListener('progress', (e) => {
                    if (e.lengthComputable) {
                        const percentComplete = Math.round((e.loaded / e.total) * 100);
                        document.getElementById('progressFill').style.width = percentComplete + '%';
                        document.getElementById('progressText').textContent = percentComplete + '%';
                    }
                });

                xhr.addEventListener('load', () => {
                    if (xhr.status === 200) {
                        try {
                            const data = JSON.parse(xhr.responseText);
                            if (data.success) {
                                this.showMessage('success', `✓ ${data.message}`);
                                // Rediriger vers le rapport après 1 seconde
                                setTimeout(() => {
                                    window.location.href = `/report/${data.report_id}`;
                                }, 1000);
                            } else {
                                this.showMessage('error', `✗ Erreur: ${data.error}`);
                            }
                        } catch (e) {
                            this.showMessage('error', `✗ Erreur parse: ${e.message}`);
                        }
                        resolve();
                    } else {
                        reject(new Error(`HTTP ${xhr.status}`));
                    }
                });

                xhr.addEventListener('error', () => {
                    reject(new Error('Erreur réseau'));
                });

                xhr.addEventListener('abort', () => {
                    reject(new Error('Upload annulé'));
                });

                xhr.open('POST', '/api/upload', true);
                // Ajouter header ngrok APRÈS open()
                xhr.setRequestHeader('ngrok-skip-browser-warning', '69420');
                xhr.send(formData);
            }).finally(() => {
                document.getElementById('uploadProgress').classList.add('hidden');
                document.getElementById('progressFill').style.width = '0%';
                document.getElementById('progressText').textContent = '0%';
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

            const tbody = document.getElementById('reportsBody');
            tbody.innerHTML = '';

            if (!data.reports || data.reports.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">Aucun rapport</td></tr>';
                return;
            }

            data.reports.forEach(report => {
                const row = document.createElement('tr');
                // Formater la date: date_rapport peut être null
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
                        console.error('Erreur parsing date rapport:', e, report.date_rapport);
                    }
                }
                row.innerHTML = `
                    <td>${dateStr}</td>
                    <td>${report.total_fax || 0}</td>
                    <td>${report.fax_envoyes || 0}</td>
                    <td>${report.fax_recus || 0}</td>
                    <td>${report.erreurs || 0}</td>
                `;
                tbody.appendChild(row);
            });
        } catch (error) {
            console.error('Erreur entries:', error);
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
