// ============================================
// FAXCLOUD ANALYZER - Main Application JS
// ============================================

console.log('✅ FaxCloud Analyzer v3.0 initialized');

/**
 * API Wrapper - Handles all API calls
 */
class API {
    static async get(endpoint) {
        try {
            const response = await fetch(endpoint);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error('API GET Error:', error);
            throw error;
        }
    }

    static async post(endpoint, data) {
        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error('API POST Error:', error);
            throw error;
        }
    }

    static async getReports(limit = 20, offset = 0) {
        return this.get(`/api/reports?limit=${limit}&offset=${offset}`);
    }

    static async getReport(id) {
        return this.get(`/api/reports/${id}`);
    }

    static async createReport(name, fileSize) {
        return this.post('/api/reports', { name, file_size: fileSize });
    }

    static async getStats() {
        return this.get('/api/stats');
    }

    static async getTrends(days = 7) {
        return this.get(`/api/trends?days=${days}`);
    }

    static async getHealth() {
        return this.get('/api/health');
    }

    static async getAdminMetrics() {
        return this.get('/api/admin/metrics');
    }
}

/**
 * Utils - Utility functions
 */
class Utils {
    static formatDate(date) {
        return new Date(date).toLocaleDateString('fr-FR', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    }

    static formatTime(date) {
        return new Date(date).toLocaleTimeString('fr-FR', {
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    static formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
    }

    static getStatusBadge(status) {
        const badges = {
            'success': '<span class="badge badge-success">✓ Réussi</span>',
            'error': '<span class="badge badge-error">✗ Erreur</span>',
            'pending': '<span class="badge badge-warning">⏳ En attente</span>',
            'completed': '<span class="badge badge-success">✓ Complété</span>'
        };
        return badges[status] || '<span class="badge">Inconnu</span>';
    }

    static showNotification(message, type = 'info', duration = 3000) {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 16px 24px;
            background: var(--bg-secondary);
            border: 1px solid var(--border-${type === 'error' ? 'error' : 'color'});
            border-radius: 8px;
            color: var(--text-primary);
            z-index: 1000;
            animation: slideIn 0.3s ease;
        `;
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, duration);
    }
}

/**
 * Data Service Mock - Pour les tests
 */
class DataService {
    static createMockReport(name = 'Nouveau Rapport') {
        return {
            id: Math.floor(Math.random() * 10000),
            name,
            created_at: new Date().toISOString(),
            entry_count: Math.floor(Math.random() * 500),
            file_size: Math.floor(Math.random() * 5000000)
        };
    }

    static createMockEntry(reportId) {
        return {
            id: Math.floor(Math.random() * 100000),
            report_id: reportId,
            data: 'Sample fax data entry',
            status: Math.random() > 0.1 ? 'success' : 'error',
            message: 'Validation completed',
            created_at: new Date().toISOString()
        };
    }
}

/**
 * Event Listeners
 */
document.addEventListener('DOMContentLoaded', () => {
    console.log('Document ready');
    
    // Auto-refresh stats toutes les 30 secondes
    // setInterval(() => {
    //     console.log('Auto-refreshing stats...');
    // }, 30000);
});

/**
 * Export pour utilisation dans d'autres scripts
 */
window.API = API;
window.Utils = Utils;
window.DataService = DataService;
