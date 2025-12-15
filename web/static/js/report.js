/* ═══════════════════════════════════════════════════════════════════════════ */
/* FAXCLOUD ANALYZER - REPORT DETAIL */
/* ═══════════════════════════════════════════════════════════════════════════ */

class ReportApp {
    constructor(reportId) {
        this.reportId = reportId;
        this.loaded = false;
        this.allEntries = [];
        this.currentFilter = 'all';
    }

    async init() {
        if (this.loaded) return;  // Éviter les double-chargements
        this.loaded = true;
        
        await this.loadReportData();
        this.setupEventListeners();
        await this.loadQRCode();
    }

    setupEventListeners() {
        const downloadBtn = document.getElementById('downloadPdfBtn');
        if (downloadBtn) {
            downloadBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.downloadPdf();
            });
        }
        
        // Ajouter les listeners pour les filtres
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.setFilter(e.target.closest('.filter-btn').dataset.filter);
            });
        });
    }

    async loadReportData() {
        try {
            const response = await fetch(`/api/report/${this.reportId}/data`);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const report = await response.json();
            this.displayReport(report);
        } catch (error) {
            console.error('Erreur chargement rapport:', error);
            document.getElementById('reportDetails').innerHTML = 
                '<p class="text-muted">Erreur lors du chargement du rapport</p>';
        }
    }

    displayReport(report) {
        // Remplir les infos du rapport
        document.getElementById('reportTitle').textContent = report.title || 'Rapport d\'Analyse';
        document.getElementById('reportDate').textContent = `Date: ${report.date}`;
        document.getElementById('reportSummary').textContent = report.summary;

        // Remplir les statistiques
        document.getElementById('statTotal').textContent = report.total || 0;
        document.getElementById('statSent').textContent = report.sent || 0;
        document.getElementById('statReceived').textContent = report.received || 0;
        document.getElementById('statErrors').textContent = report.errors || 0;
        
        // Afficher le taux de réussite
        const successRate = report.success_rate || 0;
        document.getElementById('statSuccessRate').textContent = successRate.toFixed(2) + '%';

        // Stocker toutes les entrées
        this.allEntries = report.entries || [];
        
        // Afficher avec le filtre par défaut
        this.setFilter('all');
    }

    setFilter(filterType) {
        this.currentFilter = filterType;
        
        // Mettre à jour les boutons
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.classList.remove('active');
            if (btn.dataset.filter === filterType) {
                btn.classList.add('active');
            }
        });
        
        // Afficher les entrées filtrées
        this.displayFilteredEntries();
    }

    displayFilteredEntries() {
        const detailsDiv = document.getElementById('reportDetails');
        let filteredEntries = this.allEntries;

        // Appliquer le filtre
        if (this.currentFilter === 'sent') {
            filteredEntries = this.allEntries.filter(e => e.mode === 'SF');
        } else if (this.currentFilter === 'received') {
            filteredEntries = this.allEntries.filter(e => e.mode === 'RF');
        } else if (this.currentFilter === 'error') {
            filteredEntries = this.allEntries.filter(e => e.valide === 0);
        }

        if (!filteredEntries || filteredEntries.length === 0) {
            detailsDiv.innerHTML = '<p class="text-muted">Aucune entrée disponible</p>';
            return;
        }

        // Créer le tableau
        let html = `
            <table class="entries-table">
                <thead>
                    <tr>
                        <th>ID FAX</th>
                        <th>Utilisateur</th>
                        <th>Date</th>
                        <th>Mode</th>
                        <th>Numéro</th>
                        <th>Pages</th>
                        <th>État</th>
                        <th>Erreurs</th>
                    </tr>
                </thead>
                <tbody>
        `;

        filteredEntries.forEach(entry => {
            const status = entry.valide === 1 ? 'Succès' : 'Erreur';
            const statusColor = entry.valide === 1 ? '#10b981' : '#ef4444';
            const mode = entry.mode === 'SF' ? 'Envoyé' : entry.mode === 'RF' ? 'Reçu' : entry.mode;
            
            html += `
                <tr>
                    <td>${entry.fax_id || '-'}</td>
                    <td>${entry.utilisateur || '-'}</td>
                    <td>${entry.date_heure || '-'}</td>
                    <td>${mode}</td>
                    <td>${entry.numero_normalise || entry.numero_original || '-'}</td>
                    <td>${entry.pages || '-'}</td>
                    <td><span style="color: ${statusColor}; font-weight: bold;">${status}</span></td>
                    <td>${entry.erreurs || '-'}</td>
                </tr>
            `;
        });

        html += `
                </tbody>
            </table>
        `;

        detailsDiv.innerHTML = html;
    }

    async loadQRCode() {
        try {
            const response = await fetch(`/api/report/${this.reportId}/qrcode`);
            if (response.ok) {
                const blob = await response.blob();
                const url = URL.createObjectURL(blob);
                
                const img = document.getElementById('reportQRCode');
                const loading = document.getElementById('qrLoading');
                
                if (img) {
                    img.src = url;
                    img.style.display = 'block';
                }
                if (loading) {
                    loading.style.display = 'none';
                }
            } else {
                throw new Error(`HTTP ${response.status}`);
            }
        } catch (error) {
            console.error('Erreur QR code:', error);
            const loading = document.getElementById('qrLoading');
            if (loading) {
                loading.textContent = 'QR Code indisponible';
                loading.style.color = '#ff6b6b';
            }
        }
    }

    downloadPdf() {
        window.location.href = `/api/report/${this.reportId}/pdf`;
    }
}

// Initialiser l'app au chargement de la page
document.addEventListener('DOMContentLoaded', () => {
    const app = new ReportApp(REPORT_ID);
    app.init();
});
