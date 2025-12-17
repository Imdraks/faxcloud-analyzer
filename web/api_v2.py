"""
API v2 Endpoints - Routes API modernes et scalables
À intégrer dans web/app.py
"""

# Cet exemple montre comment structurer les nouveaux endpoints

def register_api_v2_routes(app, get_db, logger, cache_service, api_service):
    """Enregistre les routes API v2"""
    from flask import request, jsonify
    
    # ═══════════════════════════════════════════════════════════════════════════
    # V2 API - STATS AMÉLIORÉES AVEC CACHE
    # ═══════════════════════════════════════════════════════════════════════════
    
    @app.route('/api/v2/stats', methods=['GET'])
    @cache_service.cached(ttl_seconds=60)  # Cache 60 secondes
    def api_v2_stats():
        """Récupérer les statistiques globales avec cache"""
        try:
            db_conn = get_db()
            if db_conn is None:
                resp = api_service.error("Base de données indisponible", status_code=503)
                return jsonify(resp.to_dict()), resp.status_code
            
            stats = db_conn.get_stats()
            formatted = api_service.format_stats(
                stats.get('total', 0),
                stats.get('sent', 0),
                stats.get('received', 0),
                stats.get('errors', 0)
            )
            
            resp = api_service.success(formatted, meta={'cached': False})
            return jsonify(resp.to_dict()), 200
        except Exception as e:
            logger.error(f"Erreur stats v2: {e}")
            resp = api_service.error(str(e))
            return jsonify(resp.to_dict()), 500
    
    # ═══════════════════════════════════════════════════════════════════════════
    # V2 API - RAPPORTS AVEC PAGINATION AVANCÉE
    # ═══════════════════════════════════════════════════════════════════════════
    
    @app.route('/api/v2/reports', methods=['GET'])
    def api_v2_reports():
        """Récupérer les rapports avec pagination et filtres"""
        try:
            # Validation des paramètres
            page = int(request.args.get('page', 1))
            limit = int(request.args.get('limit', 20))
            page, limit = api_service.validate_pagination(page, limit)
            
            search = request.args.get('search', '').strip()
            sort_by = request.args.get('sort_by', 'date_rapport')
            sort_order = request.args.get('sort_order', 'DESC').upper()
            
            db_conn = get_db()
            if db_conn is None:
                resp = api_service.error("Base de données indisponible", status_code=503)
                return jsonify(resp.to_dict()), resp.status_code
            
            # Récupérer les rapports
            reports, total = db_conn.get_reports_paginated(
                page=page,
                limit=limit,
                search=search,
                sort_by=sort_by,
                sort_order=sort_order
            )
            
            # Formater les rapports
            formatted_reports = [api_service.format_report(r) for r in reports]
            
            # Réponse paginée
            paginated = api_service.paginated(formatted_reports, total, page, limit)
            resp = api_service.success(paginated)
            
            return jsonify(resp.to_dict()), 200
        except Exception as e:
            logger.error(f"Erreur reports v2: {e}")
            resp = api_service.error(str(e))
            return jsonify(resp.to_dict()), 500
    
    # ═══════════════════════════════════════════════════════════════════════════
    # V2 API - ENTRÉES FAX AVEC FILTRES AVANCÉS
    # ═══════════════════════════════════════════════════════════════════════════
    
    @app.route('/api/v2/entries', methods=['GET'])
    def api_v2_entries():
        """Récupérer les entrées FAX avec filtres avancés"""
        try:
            page = int(request.args.get('page', 1))
            limit = int(request.args.get('limit', 50))
            page, limit = api_service.validate_pagination(page, limit)
            
            report_id = request.args.get('report_id')
            status = request.args.get('status')  # 'ok', 'error', 'all'
            search = request.args.get('search', '').strip()
            
            db_conn = get_db()
            if db_conn is None:
                resp = api_service.error("Base de données indisponible", status_code=503)
                return jsonify(resp.to_dict()), resp.status_code
            
            # Récupérer les entrées
            entries, total = db_conn.get_entries_filtered(
                report_id=report_id,
                status=status,
                search=search,
                page=page,
                limit=limit
            )
            
            paginated = api_service.paginated(entries, total, page, limit)
            resp = api_service.success(paginated)
            
            return jsonify(resp.to_dict()), 200
        except Exception as e:
            logger.error(f"Erreur entries v2: {e}")
            resp = api_service.error(str(e))
            return jsonify(resp.to_dict()), 500
    
    # ═══════════════════════════════════════════════════════════════════════════
    # V2 API - ANALYTICS AVANCÉES
    # ═══════════════════════════════════════════════════════════════════════════
    
    @app.route('/api/v2/analytics/summary', methods=['GET'])
    @cache_service.cached(ttl_seconds=300)  # Cache 5 minutes
    def api_v2_analytics_summary():
        """Récupérer un résumé analytique complet"""
        try:
            db_conn = get_db()
            if db_conn is None:
                resp = api_service.error("Base de données indisponible", status_code=503)
                return jsonify(resp.to_dict()), resp.status_code
            
            stats = db_conn.get_stats()
            
            analytics = {
                'overview': api_service.format_stats(
                    stats.get('total', 0),
                    stats.get('sent', 0),
                    stats.get('received', 0),
                    stats.get('errors', 0)
                ),
                'trends': {
                    'top_errors': db_conn.get_top_errors(10),
                    'reports_count': db_conn.count_reports(),
                },
                'timestamp': __import__('datetime').datetime.now().isoformat()
            }
            
            resp = api_service.success(analytics)
            return jsonify(resp.to_dict()), 200
        except Exception as e:
            logger.error(f"Erreur analytics: {e}")
            resp = api_service.error(str(e))
            return jsonify(resp.to_dict()), 500
    
    # ═══════════════════════════════════════════════════════════════════════════
    # V2 API - CACHE INVALIDATION (Admin)
    # ═══════════════════════════════════════════════════════════════════════════
    
    @app.route('/api/v2/cache/clear', methods=['POST'])
    def api_v2_cache_clear():
        """Vider le cache (devrait être protégé en production)"""
        try:
            pattern = request.json.get('pattern', '*') if request.json else '*'
            cache_service.invalidate(pattern)
            
            resp = api_service.success(message=f"Cache nettoyé (pattern: {pattern})")
            return jsonify(resp.to_dict()), 200
        except Exception as e:
            logger.error(f"Erreur cache clear: {e}")
            resp = api_service.error(str(e))
            return jsonify(resp.to_dict()), 500

# Ligne à ajouter dans app.py après l'initialisation de Flask:
# register_api_v2_routes(app, get_db, logger, cache_service, api_service)
