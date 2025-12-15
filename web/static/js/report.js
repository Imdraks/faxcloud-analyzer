/* ═══════════════════════════════════════════════════════════════════════════ */
/* FAXCLOUD ANALYZER - REPORT DETAIL */
/* ═══════════════════════════════════════════════════════════════════════════ */

class ReportApp {
    constructor(reportId) {
        this.reportId = reportId;
        this.init();
    }

    async init() {
        await this.loadReport();
        this.setupEventListeners();
    }

    setupEventListeners() {
        const downloadBtn = document.getElementById('downloadPdfBtn');
        if (downloadBtn) {
            downloadBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.downloadPdf();
            });
        }
    }

    async loadReport() {
        try {
            // Charger les données du rapport
            const response = await fetch(`/api/report/${this.reportId}/data`);
            
            if (!response.ok && response.status === 404) {
                // Si le rapport spécifique n'existe pas, charger les stats générales
                await this.loadGeneralStats();
                return;
            }

            const report = await response.json();
            this.displayReport(report);
        } catch (error) {
            console.error('Erreur rapport:', error);
            await this.loadGeneralStats();
        }
    }

    async loadGeneralStats() {
        try {
            const response = await fetch('/api/stats');
            const stats = await response.json();

            document.getElementById('reportTitle').textContent = 'Rapport d\'Analyse';
            document.getElementById('reportDate').textContent = `Date: ${new Date().toLocaleDateString('fr-FR')}`;
            document.getElementById('reportSummary').textContent = 'Rapport complet d\'analyse FAX';

            document.getElementById('statTotal').textContent = stats.total || 0;
            document.getElementById('statSent').textContent = stats.sent || 0;
            document.getElementById('statReceived').textContent = stats.received || 0;
            document.getElementById('statErrors').textContent = stats.errors || 0;

            // Charger les entrées détaillées
            const entriesResponse = await fetch('/api/entries?limit=50&filter=all');
            const entriesData = await entriesResponse.json();

            const detailsDiv = document.getElementById('reportDetails');
            if (entriesData.entries.length === 0) {
                detailsDiv.innerHTML = '<p class="text-muted">Aucune donnée disponible</p>';
                return;
            }

            let html = '';
            entriesData.entries.forEach(entry => {
                html += `
                    <div class="report-item">
                        <h4>📞 ${entry.number || 'N/A'}</h4>
                        <p><strong>Date:</strong> ${new Date(entry.date).toLocaleString('fr-FR')}</p>
                        <p><strong>Type:</strong> ${entry.type || '-'}</p>
                        <p><strong>Durée:</strong> ${entry.duration || '-'}</p>
                        <p><strong>État:</strong> 
                            <span style="padding: 0.25rem 0.75rem; border-radius: 4px; 
                            background: ${entry.status === 'error' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(16, 185, 129, 0.2)'}; 
                            color: ${entry.status === 'error' ? '#fca5a5' : '#86efac'};">
                                ${entry.status || '-'}
                            </span>
                        </p>
                    </div>
                `;
            });

            detailsDiv.innerHTML = html;
        } catch (error) {
            console.error('Erreur stats:', error);
            document.getElementById('reportDetails').innerHTML = 
                '<p class="text-muted">Erreur lors du chargement</p>';
        }
    }

    displayReport(report) {
        // Remplir les infos
        document.getElementById('reportTitle').textContent = report.title || 'Rapport d\'Analyse';
        document.getElementById('reportDate').textContent = `Date: ${report.date || new Date().toLocaleDateString('fr-FR')}`;
        document.getElementById('reportSummary').textContent = report.summary || 'Rapport d\'analyse FAX';

        // Remplir les stats
        document.getElementById('statTotal').textContent = report.total || 0;
        document.getElementById('statSent').textContent = report.sent || 0;
        document.getElementById('statReceived').textContent = report.received || 0;
        document.getElementById('statErrors').textContent = report.errors || 0;

        // Charger le QR code
        this.loadQRCode();
    }

    async loadQRCode() {
        try {
            const response = await fetch(`/api/report/${this.reportId}/qrcode`);
            if (response.ok) {
                const blob = await response.blob();
                const url = URL.createObjectURL(blob);
                
                const img = document.getElementById('reportQRCode');
                const loading = document.getElementById('qrLoading');
                
                img.src = url;
                img.style.display = 'block';
                if (loading) loading.style.display = 'none';
            }
        } catch (error) {
            console.error('Erreur QR code:', error);
            const loading = document.getElementById('qrLoading');
            if (loading) {
                loading.textContent = 'Erreur QR code';
            }
        }
    }

    downloadPdf() {
        window.location.href = `/api/report/${this.reportId}/pdf`;
    }
}

// Initialiser l'app
document.addEventListener('DOMContentLoaded', () => {
    new ReportApp(REPORT_ID);
});
