"""
API v3 ADVANCED
Features avancees : Export, Statistiques Detaillees, Webhooks, Alertes
"""

import json
from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

api_v3 = Blueprint('api_v3', __name__, url_prefix='/api/v3')


# ═══════════════════════════════════════════════════════════════════════════
# 📊 STATISTIQUES AVANCÉES
# ═══════════════════════════════════════════════════════════════════════════

@api_v3.route('/analytics/report/<report_id>', methods=['GET'])
def analytics_report(report_id):
    """Statistiques détaillées d'un rapport"""
    from src.core.db_mysql import DatabaseMySQL
    db = DatabaseMySQL()
    db.initialize()
    
    try:
        # Récupérer le rapport
        report = db.get_report(report_id)
        if not report:
            return jsonify({'error': 'Report not found'}), 404
        
        # Calculer les statistiques détaillées
        entries = db.get_entries(report_id)
        
        stats = {
            'report_id': report_id,
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_entries': len(entries),
                'valid_entries': sum(1 for e in entries if e.get('valide', 0) == 1),
                'error_entries': sum(1 for e in entries if e.get('valide', 0) == 0),
                'success_rate': (sum(1 for e in entries if e.get('valide', 0) == 1) / len(entries) * 100) if entries else 0
            },
            'breakdown': {
                'by_mode': {
                    'SF': sum(1 for e in entries if e.get('mode') == 'SF'),
                    'RF': sum(1 for e in entries if e.get('mode') == 'RF'),
                    'OTHER': sum(1 for e in entries if e.get('mode') not in ['SF', 'RF'])
                },
                'by_status': {
                    'valid': sum(1 for e in entries if e.get('valide', 0) == 1),
                    'invalid': sum(1 for e in entries if e.get('valide', 0) == 0)
                }
            },
            'pages': {
                'total': sum(e.get('pages', 0) or 0 for e in entries),
                'average': (sum(e.get('pages', 0) or 0 for e in entries) / len(entries)) if entries else 0,
                'by_mode': {
                    'SF': sum(e.get('pages', 0) or 0 for e in entries if e.get('mode') == 'SF'),
                    'RF': sum(e.get('pages', 0) or 0 for e in entries if e.get('mode') == 'RF')
                }
            }
        }
        
        return jsonify(stats), 200
    
    except Exception as e:
        logger.error(f"Analytics error: {e}")
        return jsonify({'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════
# 📥 EXPORT AVANCÉ
# ═══════════════════════════════════════════════════════════════════════════

@api_v3.route('/export/<report_id>/csv', methods=['GET'])
def export_csv(report_id):
    """Export du rapport en CSV"""
    from src.core.db_mysql import DatabaseMySQL
    import csv
    from io import StringIO
    from flask import make_response
    
    db = DatabaseMySQL()
    db.initialize()
    
    try:
        entries = db.get_entries(report_id)
        if not entries:
            return jsonify({'error': 'No entries found'}), 404
        
        # Créer CSV
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=[
            'fax_id', 'mode', 'numero_original', 'numero_normalise', 
            'pages', 'valide', 'erreurs', 'date_heure'
        ])
        writer.writeheader()
        writer.writerows(entries)
        
        response = make_response(output.getvalue())
        response.headers['Content-Disposition'] = f'attachment; filename=report_{report_id}.csv'
        response.headers['Content-Type'] = 'text/csv'
        return response
    
    except Exception as e:
        logger.error(f"Export error: {e}")
        return jsonify({'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════
# 🔍 RECHERCHE & FILTRAGE AVANCÉ
# ═══════════════════════════════════════════════════════════════════════════

@api_v3.route('/search/<report_id>', methods=['GET'])
def search_entries(report_id):
    """Recherche et filtrage avancé"""
    from src.core.db_mysql import DatabaseMySQL
    
    db = DatabaseMySQL()
    db.initialize()
    
    try:
        # Paramètres de recherche
        query = request.args.get('q', '').lower()
        mode = request.args.get('mode')  # SF, RF
        status = request.args.get('status')  # valid, invalid
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        
        # Récupérer tous les entries
        all_entries = db.get_entries(report_id)
        
        # Filtrer
        filtered = all_entries
        
        if query:
            filtered = [e for e in filtered if 
                       query in str(e.get('numero', '')).lower() or
                       query in str(e.get('fax_id', '')).lower()]
        
        if mode:
            filtered = [e for e in filtered if e.get('mode') == mode]
        
        if status == 'valid':
            filtered = [e for e in filtered if e.get('valide', 0) == 1]
        elif status == 'invalid':
            filtered = [e for e in filtered if e.get('valide', 0) == 0]
        
        # Pagination
        total = len(filtered)
        start = (page - 1) * per_page
        end = start + per_page
        paginated = filtered[start:end]
        
        return jsonify({
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page,
            'results': paginated
        }), 200
    
    except Exception as e:
        logger.error(f"Search error: {e}")
        return jsonify({'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════
# ⚠️ RAPPORT D'ERREURS DÉTAILLÉ
# ═══════════════════════════════════════════════════════════════════════════

@api_v3.route('/errors/<report_id>', methods=['GET'])
def get_errors_report(report_id):
    """Rapport détaillé des erreurs"""
    from src.core.db_mysql import DatabaseMySQL
    
    db = DatabaseMySQL()
    db.initialize()
    
    try:
        entries = db.get_entries(report_id)
        
        # Grouper les erreurs
        error_types = {}
        for entry in entries:
            if entry.get('erreurs'):
                errors = entry['erreurs'].split('|')
                for err in errors:
                    err = err.strip()
                    if err:
                        error_types[err] = error_types.get(err, 0) + 1
        
        return jsonify({
            'report_id': report_id,
            'total_errors': sum(error_types.values()),
            'error_breakdown': error_types,
            'error_entries': [e for e in entries if e.get('valide', 0) == 0]
        }), 200
    
    except Exception as e:
        logger.error(f"Error report: {e}")
        return jsonify({'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════
# 📈 HEALTH CHECK & METRICS
# ═══════════════════════════════════════════════════════════════════════════

@api_v3.route('/health', methods=['GET'])
def health_check():
    """Vérification de l'état du système"""
    from src.core.db_mysql import DatabaseMySQL
    
    db = DatabaseMySQL()
    db.initialize()
    
    try:
        # Tester la connexion DB
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM reports")
        report_count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'database': 'connected',
            'reports_count': report_count
        }), 200
    
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500


# ═══════════════════════════════════════════════════════════════════════════
# 🔔 WEBHOOKS & ALERTES
# ═══════════════════════════════════════════════════════════════════════════

_webhooks = {}  # Stockage simple des webhooks

@api_v3.route('/webhooks/register', methods=['POST'])
def register_webhook():
    """Enregistrer un webhook"""
    data = request.json
    webhook_url = data.get('url')
    event_type = data.get('event')  # 'upload_complete', 'error', etc.
    
    if not webhook_url or not event_type:
        return jsonify({'error': 'Missing url or event'}), 400
    
    webhook_id = f"webhook_{len(_webhooks) + 1}"
    _webhooks[webhook_id] = {
        'url': webhook_url,
        'event': event_type,
        'created_at': datetime.now().isoformat()
    }
    
    logger.info(f"Webhook registered: {webhook_id} -> {event_type}")
    return jsonify({'webhook_id': webhook_id}), 201


@api_v3.route('/webhooks', methods=['GET'])
def list_webhooks():
    """Lister les webhooks"""
    return jsonify({
        'webhooks': _webhooks,
        'count': len(_webhooks)
    }), 200


def trigger_webhook(event_type, data):
    """Déclencher les webhooks"""
    for webhook_id, webhook in _webhooks.items():
        if webhook['event'] == event_type:
            try:
                import requests
                requests.post(webhook['url'], json=data, timeout=5)
                logger.info(f"Webhook triggered: {webhook_id}")
            except Exception as e:
                logger.error(f"Webhook error: {e}")
