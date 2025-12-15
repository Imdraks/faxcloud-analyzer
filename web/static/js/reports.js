/* ═══════════════════════════════════════════════════════════════════════════ */
/* FAXCLOUD ANALYZER - REPORTS LIST */
/* ═══════════════════════════════════════════════════════════════════════════ */

class ReportsApp {
    constructor() {
        this.init();
    }

    async init() {
        await this.loadReports();
    }

    async loadReports() {
        try {
            const response = await fetch('/api/entries?limit=100&filter=all');
            const data = await response.json();

            const reportsList = document.getElementById('reportsList');

            if (!data.entries || data.entries.length === 0) {
                reportsList.innerHTML = '<p class="text-center text-muted">Aucun rapport disponible</p>';
                return;
            }

            // Grouper par date et créer des rapports
            const reportMap = new Map();
            data.entries.forEach(entry => {
                const date = new Date(entry.date).toLocaleDateString('fr-FR');
                if (!reportMap.has(date)) {
                    reportMap.set(date, {
                        date: date,
                        total: 0,
                        sent: 0,
                        received: 0,
                        errors: 0
                    });
                }

                const report = reportMap.get(date);
                report.total++;
                if (entry.type === 'sent' || entry.status === 'sent') report.sent++;
                if (entry.type === 'received' || entry.status === 'received') report.received++;
                if (entry.status === 'error') report.errors++;
            });

            // Afficher les rapports
            reportsList.innerHTML = '';
            let reportId = 1;

            reportMap.forEach((report, date) => {
                const item = document.createElement('div');
                item.className = 'analysis-item';
                item.innerHTML = `
                    <h3>📅 Rapport du ${report.date}</h3>
                    <p class="text-muted">Total: <strong>${report.total}</strong> | 
                       Envoyés: <strong>${report.sent}</strong> | 
                       Reçus: <strong>${report.received}</strong> | 
                       Erreurs: <strong>${report.errors}</strong></p>
                    <p class="meta">
                        <a href="/report/report-${reportId++}" class="btn" style="margin: 0.5rem 0; margin-right: 0.5rem;">Voir le rapport →</a>
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
