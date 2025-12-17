// ============================================
// REPORT DETAIL PAGE - JavaScript
// ============================================

const reportId = window.location.pathname.split('/').pop();
let reportData = null;
let allEntries = [];

/**
 * Charger les détails du rapport
 */
async function loadReport() {
    try {
        reportData = await API.getReport(reportId);
        
        document.getElementById('report-name').textContent = reportData.name;
        document.getElementById('report-date').textContent = 
            `Date: ${Utils.formatDate(reportData.created_at)}`;
        
        await loadEntries();
    } catch (error) {
        console.error('Erreur:', error);
        document.getElementById('report-name').textContent = '❌ Erreur: Rapport non trouvé';
    }
}

/**
 * Charger les entrées du rapport
 */
async function loadEntries() {
    try {
        const entries = await API.get(`/api/reports/${reportId}/entries?limit=200`);
        allEntries = entries;
        
        // Calculer les stats
        let successCount = 0, errorCount = 0;
        entries.forEach(entry => {
            if (entry.status === 'success') successCount++;
            else errorCount++;
        });
        
        document.getElementById('total-entries').textContent = entries.length;
        document.getElementById('success-count').textContent = successCount;
        document.getElementById('error-count').textContent = errorCount;
        document.getElementById('success-rate').textContent = 
            Math.round((successCount / entries.length * 100)) + '%';
        
        renderEntriesTable(entries);
        initStatusChart(successCount, errorCount);
    } catch (error) {
        console.error('Erreur:', error);
        Utils.showNotification('Erreur lors du chargement des entrées', 'error');
    }
}

/**
 * Afficher les entrées dans la table
 */
function renderEntriesTable(entries) {
    const tbody = document.getElementById('entries-body');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    entries.forEach(entry => {
        const statusBadge = entry.status === 'success' 
            ? '<span class="badge badge-success">✓ Réussi</span>'
            : '<span class="badge badge-error">✗ Erreur</span>';
        
        tbody.innerHTML += `
            <tr>
                <td>#${entry.id}</td>
                <td>${entry.data.substring(0, 50)}...</td>
                <td>${statusBadge}</td>
                <td>${entry.message || '-'}</td>
                <td>${Utils.formatDate(entry.created_at)}</td>
            </tr>
        `;
    });
}

/**
 * Filtrer les entrées
 */
function filterEntries() {
    const searchTerm = document.getElementById('search')?.value.toLowerCase() || '';
    const statusFilter = document.getElementById('status-filter')?.value || '';
    
    let filtered = allEntries;
    
    if (searchTerm) {
        filtered = filtered.filter(entry =>
            entry.data.toLowerCase().includes(searchTerm) ||
            (entry.message && entry.message.toLowerCase().includes(searchTerm))
        );
    }
    
    if (statusFilter) {
        filtered = filtered.filter(entry => entry.status === statusFilter);
    }
    
    renderEntriesTable(filtered);
}

/**
 * Initialiser le graphique des statuts
 */
function initStatusChart(success, error) {
    const canvas = document.getElementById('statusChart');
    if (!canvas) return;
    
    // Détruire le graphique précédent s'il existe
    if (window.statusChartInstance) {
        window.statusChartInstance.destroy();
    }
    
    const ctx = canvas.getContext('2d');
    window.statusChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Réussis', 'Erreurs'],
            datasets: [{
                data: [success, error],
                backgroundColor: ['#00d4ff', '#ff006e'],
                borderColor: ['#0099cc', '#c9184a'],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#ffffff',
                        padding: 20
                    }
                }
            }
        }
    });
}

/**
 * Exporter le rapport
 */
async function exportReport() {
    try {
        const data = await API.get(`/api/reports/${reportId}/export`);
        
        const element = document.createElement('a');
        element.setAttribute('href', 'data:text/plain;charset=utf-8,' + 
            encodeURIComponent(JSON.stringify(data, null, 2)));
        element.setAttribute('download', `rapport_${reportId}_export.json`);
        element.style.display = 'none';
        document.body.appendChild(element);
        element.click();
        document.body.removeChild(element);
        
        Utils.showNotification('Rapport exporté avec succès', 'success');
    } catch (error) {
        console.error('Erreur:', error);
        Utils.showNotification('Erreur lors de l\'export', 'error');
    }
}

/**
 * Retour à la page précédente
 */
function goBack() {
    window.history.back();
}

/**
 * Initialisation
 */
document.addEventListener('DOMContentLoaded', () => {
    loadReport();
    
    const searchInput = document.getElementById('search');
    const statusFilter = document.getElementById('status-filter');
    
    if (searchInput) searchInput.addEventListener('input', filterEntries);
    if (statusFilter) statusFilter.addEventListener('change', filterEntries);
});
