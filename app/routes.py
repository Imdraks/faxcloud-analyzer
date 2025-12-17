"""
Routes de l'application - Web et API
"""
from flask import Blueprint, render_template, jsonify, request
from app.utils.data_service import data_service
import logging

logger = logging.getLogger(__name__)

# ========== BLUEPRINTS ==========
bp_web = Blueprint('web', __name__, template_folder='../templates')
bp_api = Blueprint('api', __name__, url_prefix='/api')

# ========== WEB ROUTES ==========
@bp_web.route('/')
def index():
    """Page d'accueil"""
    return render_template('dashboard.html')

@bp_web.route('/reports')
def reports():
    """Liste des rapports"""
    return render_template('reports.html')

@bp_web.route('/report/<int:report_id>')
def report_detail(report_id):
    """Détail d'un rapport"""
    return render_template('report.html')

@bp_web.route('/admin')
def admin():
    """Dashboard administrateur"""
    return render_template('admin.html')

# ========== API REPORTS ==========
@bp_api.route('/reports', methods=['GET'])
def api_get_reports():
    """Récupérer tous les rapports"""
    limit = request.args.get('limit', 20, type=int)
    offset = request.args.get('offset', 0, type=int)
    reports = data_service.get_all_reports(limit, offset)
    return jsonify(reports), 200

@bp_api.route('/reports/<int:report_id>', methods=['GET'])
def api_get_report(report_id):
    """Récupérer les détails d'un rapport"""
    report = data_service.get_report(report_id)
    if not report:
        return jsonify({'error': 'Report not found'}), 404
    return jsonify(report), 200

@bp_api.route('/reports', methods=['POST'])
def api_create_report():
    """Créer un nouveau rapport"""
    data = request.get_json()
    name = data.get('name', 'Nouveau rapport')
    file_size = data.get('file_size', 0)
    report = data_service.create_report(name, file_size)
    return jsonify(report), 201

@bp_api.route('/reports/<int:report_id>/entries', methods=['GET'])
def api_get_entries(report_id):
    """Récupérer les entrées d'un rapport"""
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)
    entries = data_service.get_report_entries(report_id, limit, offset)
    return jsonify(entries), 200

@bp_api.route('/reports/<int:report_id>/entries', methods=['POST'])
def api_add_entry(report_id):
    """Ajouter une entrée à un rapport"""
    report = data_service.get_report(report_id)
    if not report:
        return jsonify({'error': 'Report not found'}), 404
    
    data = request.get_json()
    entry = data_service.add_entry(report_id, data)
    return jsonify(entry), 201

@bp_api.route('/reports/<int:report_id>/export', methods=['GET'])
def api_export_report(report_id):
    """Exporter un rapport"""
    report = data_service.get_report(report_id)
    if not report:
        return jsonify({'error': 'Report not found'}), 404
    
    entries = data_service.get_report_entries(report_id)
    export_data = {
        'report': report,
        'entries': entries
    }
    return jsonify(export_data), 200

# ========== API STATS ==========
@bp_api.route('/stats', methods=['GET'])
def api_stats():
    """Statistiques globales"""
    stats = data_service.get_stats()
    return jsonify(stats), 200

@bp_api.route('/trends', methods=['GET'])
def api_trends():
    """Tendances"""
    days = request.args.get('days', 7, type=int)
    trends = data_service.get_trends(days)
    return jsonify(trends), 200

# ========== API HEALTH ==========
@bp_api.route('/health', methods=['GET'])
def api_health():
    """Vérifier l'état du serveur"""
    return jsonify({
        'status': 'online',
        'version': '3.0',
        'service': 'FaxCloud Analyzer'
    }), 200

# ========== API ADMIN ROUTES ==========
@bp_api.route('/admin/health/detailed', methods=['GET'])
def admin_health_detailed():
    """Santé détaillée du système"""
    stats = data_service.get_stats()
    return jsonify({
        'status': 'healthy',
        'database': {
            'reports': stats['total_reports'],
            'entries': stats['total_entries']
        },
        'uptime': 3600
    }), 200

@bp_api.route('/admin/metrics', methods=['GET'])
def admin_metrics():
    """Métriques pour le dashboard admin"""
    stats = data_service.get_stats()
    return jsonify({
        'cpu_usage': 35,
        'memory_usage': 42,
        'disk_usage': 28,
        'database_size': 2048,
        'reports_today': 5,
        'entries_today': 1250,
        'avg_processing_time': 12.5,
        'error_rate': round((stats['error_entries'] / stats['total_entries'] * 100) if stats['total_entries'] > 0 else 0, 2),
        'success_rate': stats['success_rate']
    }), 200

# ========== REGISTER BLUEPRINTS ==========
def register_routes(app):
    """Enregistrer tous les blueprints"""
    app.register_blueprint(bp_web)
    app.register_blueprint(bp_api)


# ========== API ADMIN ROUTES ==========
@bp_api.route('/admin/health/detailed', methods=['GET'])
def admin_health_detailed():
    """Santé détaillée du système"""
    stats = data_service.get_stats()
    return jsonify({
        'status': 'healthy',
        'database': {
            'reports': stats['total_reports'],
            'entries': stats['total_entries']
        },
        'uptime': 3600
    }), 200

@bp_api.route('/admin/metrics', methods=['GET'])
def admin_metrics():
    """Métriques système"""
    return jsonify({
        'system': {
            'cpu_percent': 12.5,
            'memory_mb': 256.3
        },
        'requests': {
            'total': 1250,
            'errors': 5
        }
    }), 200
