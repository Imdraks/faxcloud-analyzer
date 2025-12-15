/* ═══════════════════════════════════════════════════════════════════════════ */
/* FAXCLOUD ANALYZER - MAIN APPLICATION */
/* ═══════════════════════════════════════════════════════════════════════════ */

class FaxApp {
    constructor() {
        this.currentFilter = 'all';
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadStats();
        this.loadEntries();
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
        const formData = new FormData();
        formData.append('file', file);

        try {
            // Afficher la barre de progression
            const progressDiv = document.getElementById('uploadProgress');
            progressDiv.classList.remove('hidden');

            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                this.showMessage('success', `✓ ${data.message}`);
                // Rediriger vers le rapport après 1 seconde
                setTimeout(() => {
                    window.location.href = `/report/${data.report_id}`;
                }, 1000);
            } else {
                this.showMessage('error', `✗ Erreur: ${data.error}`);
            }
        } catch (error) {
            this.showMessage('error', `✗ Erreur upload: ${error.message}`);
        } finally {
            document.getElementById('uploadProgress').classList.add('hidden');
            document.getElementById('progressFill').style.width = '0%';
            document.getElementById('progressText').textContent = '0%';
        }
    }

    async loadStats() {
        try {
            const response = await fetch('/api/stats');
            const stats = await response.json();

            document.getElementById('totalFax').textContent = stats.total || 0;
            document.getElementById('sentFax').textContent = stats.sent || 0;
            document.getElementById('receivedFax').textContent = stats.received || 0;
            document.getElementById('errorFax').textContent = stats.errors || 0;
        } catch (error) {
            console.error('Erreur stats:', error);
        }
    }

    async loadEntries() {
        try {
            const response = await fetch(`/api/entries?filter=${this.currentFilter}&limit=10`);
            const data = await response.json();

            const tbody = document.getElementById('entriesBody');
            tbody.innerHTML = '';

            if (data.entries.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">Aucun enregistrement</td></tr>';
                return;
            }

            data.entries.forEach(entry => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${new Date(entry.date).toLocaleDateString('fr-FR')}</td>
                    <td>${entry.number || '-'}</td>
                    <td>${entry.type || '-'}</td>
                    <td>${entry.duration || '-'}</td>
                    <td>
                        <span style="display: inline-block; padding: 0.25rem 0.75rem; border-radius: 4px; 
                        background: ${entry.status === 'error' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(16, 185, 129, 0.2)'}; 
                        color: ${entry.status === 'error' ? '#fca5a5' : '#86efac'};">
                            ${entry.status || '-'}
                        </span>
                    </td>
                `;
                tbody.appendChild(row);
            });
        } catch (error) {
            console.error('Erreur entries:', error);
        }
    }

    setFilter(filter, btn) {
        this.currentFilter = filter;
        
        // Mettre à jour les boutons
        document.querySelectorAll('.filter-buttons .btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        // Recharger les entrées
        this.loadEntries();
    }

    async clearData() {
        if (!confirm('⚠️ Êtes-vous sûr? Toutes les données seront effacées de manière permanente.')) {
            return;
        }

        try {
            const response = await fetch('/api/clear', { method: 'POST' });
            const data = await response.json();

            if (data.success) {
                this.showMessage('success', '✓ Données effacées');
                this.loadStats();
                this.loadEntries();
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
