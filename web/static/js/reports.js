// FaxCloud Analyzer - Reports Page Script

let currentPage = 1;
const itemsPerPage = 10;

document.addEventListener('DOMContentLoaded', function() {
    loadReports();
});

function loadReports(page = 1) {
    currentPage = page;
    
    fetch(`/api/reports?page=${page}&limit=${itemsPerPage}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                displayReports(data.reports);
                updatePagination(data.reports.length);
            }
        })
        .catch(error => console.error('Erreur:', error));
}

function displayReports(reports) {
    const container = document.getElementById('reportsList');
    
    if (reports.length === 0) {
        container.innerHTML = '<p class="text-muted">Aucun rapport disponible</p>';
        return;
    }
    
    const html = reports.map(report => `
        <a href="/report/${report.id}" class="report-item">
            <h3>📋 ${report.id}</h3>
            <p><strong>Contrat:</strong> ${report.contract_id}</p>
            <p><strong>Généré:</strong> ${new Date(report.date_rapport).toLocaleString('fr-FR')}</p>
            <p>
                FAX: ${report.total_fax} |
                Erreurs: ${report.erreurs} |
                Réussite: <strong>${report.taux_reussite.toFixed(1)}%</strong>
            </p>
        </a>
    `).join('');
    
    container.innerHTML = html;
}

function updatePagination(itemCount) {
    const pagination = document.getElementById('pagination');
    
    if (itemCount < itemsPerPage) {
        pagination.classList.add('hidden');
        return;
    }
    
    pagination.classList.remove('hidden');
    
    document.getElementById('pageInfo').textContent = `Page ${currentPage}`;
    document.getElementById('prevPage').disabled = currentPage === 1;
    document.getElementById('nextPage').disabled = itemCount < itemsPerPage;
    
    document.getElementById('prevPage').onclick = () => loadReports(currentPage - 1);
    document.getElementById('nextPage').onclick = () => loadReports(currentPage + 1);
}
