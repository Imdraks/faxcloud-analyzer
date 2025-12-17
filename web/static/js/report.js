/* ═══════════════════════════════════════════════════════════════════════════ */
/* FAXCLOUD ANALYZER - REPORT DETAIL */
/* ═══════════════════════════════════════════════════════════════════════════ */

class ReportApp {
    constructor(reportId) {
        this.reportId = reportId;
        this.loaded = false;
        this.allEntries = [];
        this.currentFilter = 'all';
        this.currentPage = 1;
        this.entriesPerPage = 20;
        this.searchQuery = '';
    }

    // Helper pour les requêtes fetch avec header ngrok
    async fetchWithNgrokHeader(url, options = {}) {
        const headers = options.headers || {};
        headers['ngrok-skip-browser-warning'] = '69420';
        return fetch(url, { ...options, headers });
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

        // Listener pour la recherche avec debounce
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            let searchTimeout;
            searchInput.addEventListener('input', (e) => {
                this.searchQuery = e.target.value;
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => {
                    this.currentPage = 1;  // Réinitialiser à la page 1
                    this.displayFilteredEntries();
                }, 300);
            });
        }

        // Listener pour l'export CSV
        const exportBtn = document.getElementById('exportBtn');
        if (exportBtn) {
            exportBtn.addEventListener('click', () => {
                this.exportToCSV();
            });
        }
    }

    async loadReportData() {
        try {
            const response = await this.fetchWithNgrokHeader(`/api/report/${this.reportId}/data`);
            
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

        // Stocker toutes les entrées
        this.allEntries = report.entries || [];

        // Remplir les statistiques
        document.getElementById('statTotal').textContent = report.total || 0;
        document.getElementById('statSent').textContent = report.sent || 0;
        document.getElementById('statReceived').textContent = report.received || 0;
        document.getElementById('statErrors').textContent = report.errors || 0;
        
        // Afficher le taux de réussite
        const successRate = report.success_rate || 0;
        document.getElementById('statSuccessRate').textContent = successRate.toFixed(2) + '%';
        
        // Afficher les pages SF et RF depuis le serveur
        document.getElementById('statPagesSF').textContent = report.pages_sf || 0;
        document.getElementById('statPagesRF').textContent = report.pages_rf || 0;
        
        // Afficher avec le filtre par défaut
        this.setFilter('all');
    }

    setFilter(filterType) {
        this.currentFilter = filterType;
        this.currentPage = 1;  // Réinitialiser à la page 1
        
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

        // Appliquer la recherche
        if (this.searchQuery.trim()) {
            const query = this.searchQuery.toLowerCase();
            filteredEntries = filteredEntries.filter(e => 
                (e.fax_id && e.fax_id.toLowerCase().includes(query)) ||
                (e.utilisateur && e.utilisateur.toLowerCase().includes(query)) ||
                (e.numero_normalise && e.numero_normalise.toLowerCase().includes(query)) ||
                (e.numero_original && e.numero_original.toLowerCase().includes(query))
            );
        }

        if (!filteredEntries || filteredEntries.length === 0) {
            detailsDiv.innerHTML = '<p class="text-muted">Aucune entrée disponible</p>';
            document.getElementById('paginationContainer').style.display = 'none';
            document.getElementById('filterStats').style.display = 'none';
            return;
        }

        // Calculer les statistiques du filtre
        this.updateFilterStats(filteredEntries);

        // Calculer la pagination
        const totalPages = Math.ceil(filteredEntries.length / this.entriesPerPage);
        const startIndex = (this.currentPage - 1) * this.entriesPerPage;
        const endIndex = startIndex + this.entriesPerPage;
        const pageEntries = filteredEntries.slice(startIndex, endIndex);

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

        pageEntries.forEach(entry => {
            const status = entry.valide === 1 ? 'Succès' : 'Erreur';
            const statusColor = entry.valide === 1 ? '#10b981' : '#ef4444';
            const mode = entry.mode === 'SF' ? 'Envoyé' : entry.mode === 'RF' ? 'Reçu' : entry.mode;
            
            html += `
                <tr>
                    <td>${entry.fax_id || '-'}</td>
                    <td>${entry.utilisateur || '-'}</td>
                    <td>${entry.date_heure ? new Date(entry.date_heure).toLocaleString('fr-FR') : '-'}</td>
                    <td>${mode}</td>
                    <td>${entry.numero_normalise || entry.numero_original || '-'}</td>
                    <td>${entry.pages || '-'}</td>
                    <td><span style="color: ${statusColor}; font-weight: bold;">${status}</span></td>
                    <td>${entry.erreurs ? (typeof entry.erreurs === 'string' ? entry.erreurs : JSON.stringify(entry.erreurs)) : '-'}</td>
                </tr>
            `;
        });

        html += `
                </tbody>
            </table>
        `;

        detailsDiv.innerHTML = html;

        // Afficher et mettre à jour la pagination
        this.updatePagination(totalPages, filteredEntries.length);
    }

    updateFilterStats(filteredEntries) {
        const total = filteredEntries.length;
        const success = filteredEntries.filter(e => e.valide === 1).length;
        const errors = filteredEntries.filter(e => e.valide === 0).length;
        const successRate = total > 0 ? ((success / total) * 100).toFixed(1) : 0;

        document.getElementById('statTotal').textContent = total;
        document.getElementById('statSuccess').textContent = success;
        document.getElementById('statErrors').textContent = errors;
        document.getElementById('statSuccessRate').textContent = successRate + '%';
        document.getElementById('filterStats').style.display = 'grid';
    }

    updatePagination(totalPages, totalEntries) {
        const paginationContainer = document.getElementById('paginationContainer');
        const pageButtonsDiv = document.getElementById('pageButtons');
        const currentPageSpan = document.getElementById('currentPage');
        const totalPagesSpan = document.getElementById('totalPages');

        // Afficher le conteneur de pagination
        paginationContainer.style.display = totalPages > 1 ? 'block' : 'none';

        if (totalPages <= 1) return;

        // Mettre à jour le texte
        currentPageSpan.textContent = this.currentPage;
        totalPagesSpan.textContent = totalPages;

        // Créer les boutons de page
        pageButtonsDiv.innerHTML = '';
        
        // Déterminer la plage de pages à afficher (max 10)
        let startPage = Math.max(1, this.currentPage - 4);
        let endPage = Math.min(totalPages, this.currentPage + 5);

        for (let i = startPage; i <= endPage; i++) {
            const btn = document.createElement('button');
            btn.className = i === this.currentPage ? 'page-btn active' : 'page-btn';
            btn.textContent = i;
            btn.onclick = () => this.goToPage(i);
            pageButtonsDiv.appendChild(btn);
        }

        // Mettre à jour les boutons précédent/suivant
        document.getElementById('prevBtn').disabled = this.currentPage === 1;
        document.getElementById('nextBtn').disabled = this.currentPage === totalPages;
        document.getElementById('firstBtn').disabled = this.currentPage === 1;
        document.getElementById('lastBtn').disabled = this.currentPage === totalPages;
        
        document.getElementById('firstBtn').onclick = () => {
            if (this.currentPage !== 1) {
                this.goToPage(1);
            }
        };
        
        document.getElementById('prevBtn').onclick = () => {
            if (this.currentPage > 1) {
                this.goToPage(this.currentPage - 1);
            }
        };
        
        document.getElementById('nextBtn').onclick = () => {
            if (this.currentPage < totalPages) {
                this.goToPage(this.currentPage + 1);
            }
        };
        
        document.getElementById('lastBtn').onclick = () => {
            if (this.currentPage !== totalPages) {
                this.goToPage(totalPages);
            }
        };
    }

    goToPage(pageNumber) {
        this.currentPage = pageNumber;
        this.displayFilteredEntries();
        // Scroll vers le haut du tableau
        document.getElementById('reportDetails').scrollIntoView({ behavior: 'smooth' });
    }

    async loadQRCode() {
        try {
            const response = await this.fetchWithNgrokHeader(`/api/report/${this.reportId}/qrcode`);
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

    exportToCSV() {
        // Récupérer les entrées filtrées et recherchées
        let filteredEntries = this.allEntries;

        // Appliquer le filtre
        if (this.currentFilter === 'sent') {
            filteredEntries = this.allEntries.filter(e => e.mode === 'SF');
        } else if (this.currentFilter === 'received') {
            filteredEntries = this.allEntries.filter(e => e.mode === 'RF');
        } else if (this.currentFilter === 'error') {
            filteredEntries = this.allEntries.filter(e => e.valide === 0);
        }

        // Appliquer la recherche
        if (this.searchQuery.trim()) {
            const query = this.searchQuery.toLowerCase();
            filteredEntries = filteredEntries.filter(e => 
                (e.fax_id && e.fax_id.toLowerCase().includes(query)) ||
                (e.utilisateur && e.utilisateur.toLowerCase().includes(query)) ||
                (e.numero_normalise && e.numero_normalise.toLowerCase().includes(query)) ||
                (e.numero_original && e.numero_original.toLowerCase().includes(query))
            );
        }

        if (!filteredEntries.length) {
            alert('Aucune donnée à exporter');
            return;
        }

        // En-têtes CSV
        const headers = ['ID FAX', 'Utilisateur', 'Date', 'Mode', 'Numéro', 'Pages', 'État', 'Erreurs'];
        
        // Construire les lignes CSV
        let csv = headers.join(',') + '\n';
        filteredEntries.forEach(entry => {
            const row = [
                this.escapeCSV(entry.fax_id || ''),
                this.escapeCSV(entry.utilisateur || ''),
                entry.date_heure ? new Date(entry.date_heure).toLocaleString('fr-FR') : '',
                entry.mode === 'SF' ? 'Envoyé' : entry.mode === 'RF' ? 'Reçu' : entry.mode || '',
                this.escapeCSV(entry.numero_normalise || entry.numero_original || ''),
                entry.pages || '',
                entry.valide === 1 ? 'Succès' : 'Erreur',
                this.escapeCSV(entry.erreurs ? (typeof entry.erreurs === 'string' ? entry.erreurs : JSON.stringify(entry.erreurs)) : '')
            ];
            csv += row.join(',') + '\n';
        });

        // Créer le fichier et le télécharger
        const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);
        
        link.setAttribute('href', url);
        link.setAttribute('download', `rapport_${this.reportId}_${new Date().toISOString().split('T')[0]}.csv`);
        link.style.visibility = 'hidden';
        
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }

    escapeCSV(str) {
        if (!str) return '';
        str = String(str);
        if (str.includes(',') || str.includes('"') || str.includes('\n')) {
            return '"' + str.replace(/"/g, '""') + '"';
        }
        return str;
    }
}

// Initialiser l'app au chargement de la page
document.addEventListener('DOMContentLoaded', () => {
    const app = new ReportApp(REPORT_ID);
    app.init();
});
