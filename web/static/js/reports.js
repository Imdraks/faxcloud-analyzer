/* ═══════════════════════════════════════════════════════════════════════════ */
/* FAXCLOUD ANALYZER - REPORTS LIST */
/* ═══════════════════════════════════════════════════════════════════════════ */

class ReportsApp {
    constructor() {
        this.init();
    }

    // Helper pour les requêtes fetch avec header ngrok
    async fetchWithNgrokHeader(url, options = {}) {
        const headers = options.headers || {};
        headers['ngrok-skip-browser-warning'] = '69420';
        return fetch(url, { ...options, headers });
    }

    async init() {
        await this.loadReports();
    }

    async loadReports() {
        try {
            const response = await this.fetchWithNgrokHeader('/api/latest-reports');
            const data = await response.json();

            const reportsList = document.getElementById('reportsList');

            if (!data.reports || data.reports.length === 0) {
                reportsList.innerHTML = '<p class="text-center text-muted">Aucun rapport disponible</p>';
                return;
            }

            // Afficher les rapports
            reportsList.innerHTML = '';

            data.reports.forEach((report) => {
                const item = document.createElement('div');
                item.className = 'analysis-item';
                
                // Formater la date
                let dateStr = '-';
                if (report.date_rapport) {
                    try {
                        const date = new Date(report.date_rapport);
                        if (!isNaN(date.getTime())) {
                            dateStr = date.toLocaleDateString('fr-FR', { 
                                year: 'numeric', 
                                month: 'long', 
                                day: 'numeric',
                                hour: '2-digit',
                                minute: '2-digit'
                            });
                        }
                    } catch (e) {
                        console.error('Erreur parsing date:', e);
                    }
                }
                
                const taux = report.taux_reussite ? (report.taux_reussite * 100).toFixed(1) : '0';
                
                item.innerHTML = `
                    <h3>📅 Rapport du ${dateStr}</h3>
                    <p class="text-muted">
                        Total: <strong>${report.total_fax}</strong> | 
                        Envoyés: <strong>${report.fax_envoyes}</strong> | 
                        Reçus: <strong>${report.fax_recus}</strong> | 
                        Erreurs: <strong>${report.erreurs}</strong> | 
                        Taux: <strong>${taux}%</strong>
                    </p>
                    <p class="meta">
                        <a href="/report/${report.id}" class="btn" style="margin: 0.5rem 0; margin-right: 0.5rem;">Voir le rapport →</a>
                    </p>
                `;
                reportsList.appendChild(item);
            });
        } catch (error) {
            console.error('Erreur reports:', error);
            document.getElementById('reportsList').innerHTML = 
                '<p class="text-center text-muted">Erreur lors du chargement</p>';
        }
    }
}

// Initialiser l'app
document.addEventListener('DOMContentLoaded', () => {
    new ReportsApp();
});
