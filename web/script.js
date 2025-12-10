/**
 * FaxCloud Analyzer - Script principal
 * Interface web dynamique
 */

// ═══════════════════════════════════════════════════════════════════════════
// VARIABLES GLOBALES
// ═══════════════════════════════════════════════════════════════════════════

let reports = [];
let currentSection = 'dashboard';

// Configuration
const API_BASE = 'http://localhost:8000';
const REPORTS_API = `${API_BASE}/api/reports`;

// ═══════════════════════════════════════════════════════════════════════════
// NAVIGATION
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Affiche une section et masque les autres
 */
function showSection(sectionId) {
    // Masquer toutes les sections
    document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('active');
    });

    // Désactiver tous les boutons nav
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    // Afficher la section sélectionnée
    const section = document.getElementById(sectionId);
    if (section) {
        section.classList.add('active');
    }

    // Activer le bouton nav correspondant
    event.target.classList.add('active');

    currentSection = sectionId;

    // Actions spécifiques
    if (sectionId === 'reports') {
        loadReports();
    } else if (sectionId === 'stats') {
        loadStatistics();
    }
}

// ═══════════════════════════════════════════════════════════════════════════
// IMPORT
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Initialiser le formulaire d'import
 */
function initImportForm() {
    const today = new Date();
    const startDate = new Date(today);
    startDate.setMonth(today.getMonth() - 1); // Un mois en arrière

    document.getElementById('start-date').valueAsDate = startDate;
    document.getElementById('end-date').valueAsDate = today;

    document.getElementById('import-form').addEventListener('submit', handleImport);
}

/**
 * Gérer l'import de fichier
 */
function handleImport(e) {
    e.preventDefault();

    const contract = document.getElementById('contract').value;
    const startDate = document.getElementById('start-date').value;
    const endDate = document.getElementById('end-date').value;
    const file = document.getElementById('file').files[0];

    if (!file) {
        showStatus('Veuillez sélectionner un fichier', 'error');
        return;
    }

    const statusDiv = document.getElementById('import-status');
    statusDiv.style.display = 'block';
    statusDiv.classList = 'status-message loading';
    statusDiv.textContent = '⏳ Traitement en cours...';

    // Simuler l'import (en réalité, ce serait un appel API)
    setTimeout(() => {
        const reportId = generateUUID();
        const success = Math.random() > 0.2; // 80% de succès

        if (success) {
            showStatus(
                `✅ Rapport généré: ${reportId.substring(0, 8)}...`,
                'success'
            );
            // Recharger la liste des rapports
            setTimeout(() => loadReports(), 1000);
        } else {
            showStatus(
                '❌ Erreur lors du traitement du fichier',
                'error'
            );
        }
    }, 2000);
}

/**
 * Afficher un message de statut
 */
function showStatus(message, type) {
    const statusDiv = document.getElementById('import-status');
    statusDiv.style.display = 'block';
    statusDiv.classList = `status-message ${type}`;
    statusDiv.textContent = message;
}

// ═══════════════════════════════════════════════════════════════════════════
// RAPPORTS
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Charger et afficher la liste des rapports
 */
function loadReports() {
    // Simuler le chargement (en réalité, appel API)
    reports = generateMockReports();
    displayReports(reports);
}

/**
 * Générer des rapports fictifs pour la démo
 */
function generateMockReports() {
    return [
        {
            id: 'a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6',
            contract: 'CONTRACT_001',
            timestamp: new Date(Date.now() - 3600000).toISOString(),
            totalFax: 20,
            errors: 3,
            successRate: 85.0,
            pages: 97
        },
        {
            id: 'b2c3d4e5-f6g7-h8i9-j0k1-l2m3n4o5p6a1',
            contract: 'CONTRACT_002',
            timestamp: new Date(Date.now() - 86400000).toISOString(),
            totalFax: 150,
            errors: 12,
            successRate: 92.0,
            pages: 412
        },
        {
            id: 'c3d4e5f6-g7h8-i9j0-k1l2-m3n4o5p6a1b2',
            contract: 'CONTRACT_001',
            timestamp: new Date(Date.now() - 172800000).toISOString(),
            totalFax: 85,
            errors: 5,
            successRate: 94.1,
            pages: 256
        }
    ];
}

/**
 * Afficher les rapports dans la grille
 */
function displayReports(reportsToShow) {
    const container = document.getElementById('reports-list');

    if (reportsToShow.length === 0) {
        container.innerHTML = '<p class="empty-message">Aucun rapport disponible</p>';
        return;
    }

    container.innerHTML = reportsToShow.map(report => `
        <div class="report-card" onclick="viewReport('${report.id}')">
            <div class="report-id">ID: ${report.id.substring(0, 20)}...</div>
            
            <div class="report-stats">
                <div class="report-stat">
                    <div class="report-stat-value">${report.totalFax}</div>
                    <div>FAX</div>
                </div>
                <div class="report-stat">
                    <div class="report-stat-value">${report.pages}</div>
                    <div>Pages</div>
                </div>
                <div class="report-stat">
                    <div class="report-stat-value">${report.errors}</div>
                    <div>Erreurs</div>
                </div>
            </div>
            
            <div class="report-info" style="margin-top: 1rem; font-size: 0.9rem;">
                <p><strong>Contrat:</strong> ${report.contract}</p>
                <p><strong>Généré:</strong> ${new Date(report.timestamp).toLocaleString('fr-FR')}</p>
                <p><span class="success-rate">${report.successRate.toFixed(1)}% ✓</span></p>
            </div>
        </div>
    `).join('');
}

/**
 * Afficher un rapport détaillé (simulation)
 */
function viewReport(reportId) {
    alert(`Rapport: ${reportId}\n\n(Détails complets à venir dans l'interface détaillée)`);
}

/**
 * Filtrer les rapports par recherche
 */
function filterReports() {
    const searchTerm = document.getElementById('search-reports').value.toLowerCase();
    const filtered = reports.filter(report =>
        report.id.toLowerCase().includes(searchTerm) ||
        report.contract.toLowerCase().includes(searchTerm)
    );
    displayReports(filtered);
}

// ═══════════════════════════════════════════════════════════════════════════
// STATISTIQUES
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Charger les statistiques
 */
function loadStatistics() {
    // Calculer les stats globales
    const stats = calculateGlobalStats();
    
    displayErrorStats(stats.errorStats);
    displayUserStats(stats.userStats);
    updateDashboard(stats.dashboardStats);
}

/**
 * Calculer les statistiques globales
 */
function calculateGlobalStats() {
    // Données simulées
    const errorStats = [
        { label: 'Numéros vides', value: 5 },
        { label: 'Longueur incorrecte', value: 8 },
        { label: 'Ne commence pas 33', value: 4 },
        { label: 'Caractères invalides', value: 2 }
    ];

    const userStats = [
        { label: 'Jean Dupont', value: 45, errors: 2 },
        { label: 'Marie Martin', value: 38, errors: 4 },
        { label: 'Pierre Leblanc', value: 67, errors: 6 }
    ];

    const dashboardStats = {
        totalReports: 3,
        totalFax: 255,
        errors: 19,
        users: 10,
        avgSuccessRate: 90.5
    };

    return { errorStats, userStats, dashboardStats };
}

/**
 * Afficher les stats d'erreurs
 */
function displayErrorStats(errorStats) {
    const container = document.getElementById('error-stats');
    container.innerHTML = errorStats.map(stat => `
        <div class="stat-item">
            <span class="stat-label">${stat.label}</span>
            <span class="stat-value">${stat.value}</span>
        </div>
    `).join('');
}

/**
 * Afficher les stats d'utilisateurs
 */
function displayUserStats(userStats) {
    const container = document.getElementById('user-stats');
    container.innerHTML = userStats.map(stat => `
        <div class="stat-item">
            <span class="stat-label">
                ${stat.label}
                <br><small style="opacity: 0.7;">${stat.errors} erreurs</small>
            </span>
            <span class="stat-value">${stat.value}</span>
        </div>
    `).join('');
}

/**
 * Mettre à jour le dashboard
 */
function updateDashboard(stats) {
    document.getElementById('total-reports').textContent = stats.totalReports;
    document.getElementById('total-fax').textContent = stats.totalFax;
    document.getElementById('success-rate').textContent = stats.avgSuccessRate.toFixed(1) + '%';
    document.getElementById('users-count').textContent = stats.users;
}

// ═══════════════════════════════════════════════════════════════════════════
# UTILITAIRES
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Générer un UUID simple
 */
function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
        const r = Math.random() * 16 | 0;
        const v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

// ═══════════════════════════════════════════════════════════════════════════
// INITIALISATION
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Initialiser l'application
 */
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 FaxCloud Analyzer - Démarrage');
    
    // Initialiser le formulaire
    initImportForm();
    
    // Charger les statistiques initiales
    loadStatistics();
    
    // Charger la liste des rapports
    loadReports();
    
    console.log('✅ Application prête');
});

// ═══════════════════════════════════════════════════════════════════════════
