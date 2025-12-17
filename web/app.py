#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FaxCloud Analyzer - Web Application
Backend moderne avec Flask
"""

import sys
import json
import io
from pathlib import Path
from datetime import datetime

from flask import Flask, render_template, request, jsonify, send_file
from flask_compress import Compress
from werkzeug.utils import secure_filename

# Ajouter src au chemin Python
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.config import Config
from core.importer import FileImporter
from core.analyzer import FaxAnalyzer
from core.reporter import ReportGenerator
from core.pdf_generator import PDFReportGenerator
from core.db_mysql import DatabaseMySQL
from core.ngrok_helper import NgrokHelper

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION FLASK
# ═══════════════════════════════════════════════════════════════════════════

app = Flask(__name__, 
    template_folder='templates',
    static_folder='static',
    static_url_path='/static')

# Activer la compression GZIP pour réduire la bande passante
Compress(app)

app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB
app.config['UPLOAD_FOLDER'] = Config.IMPORTS_DIR
app.config['COMPRESS_LEVEL'] = 6  # Compression niveau 6 (bon équilibre)
app.config['COMPRESS_MIN_SIZE'] = 1024  # Compresser les réponses > 1KB

# Setup logging
Config.ensure_directories()
Config.setup_logging()
logger = Config.get_logger(__name__)

# Initialiser la base de données
db = None

def get_db():
    """Récupère ou initialise la base de données"""
    global db
    if db is None:
        try:
            db = DatabaseMySQL()
            db.initialize()
            logger.info("Base de donnees initialisee")
        except Exception as e:
            logger.error(f"Erreur BD: {e}")
            return None
    return db

# ═══════════════════════════════════════════════════════════════════════════
# MIDDLEWARE NGROK & PERFORMANCE
# ═══════════════════════════════════════════════════════════════════════════

@app.after_request
def add_ngrok_bypass_header(response):
    """Ajoute le header pour contourner l'avertissement ngrok et optimisations"""
    response.headers['ngrok-skip-browser-warning'] = 'true'
    # Headers de cache pour les assets statiques
    if request.path.startswith('/static/'):
        response.headers['Cache-Control'] = 'public, max-age=86400'  # 1 jour
    return response

# ═══════════════════════════════════════════════════════════════════════════
# ROUTES PRINCIPALES
# ═══════════════════════════════════════════════════════════════════════════

@app.route('/', methods=['GET'])
def index():
    """Page d'accueil - Import CSV"""
    try:
        db_conn = get_db()
        stats = db_conn.get_stats() if db_conn else {}
        return render_template('index.html', stats=stats)
    except Exception as e:
        logger.error(f"Erreur index: {e}")
        return render_template('index.html', stats={})


@app.route('/reports', methods=['GET'])
def reports():
    """Page liste des rapports"""
    try:
        db_conn = get_db()
        reports_list = db_conn.get_reports_list() if db_conn else []
        return render_template('reports.html', reports=reports_list)
    except Exception as e:
        logger.error(f"Erreur reports: {e}")
        return render_template('reports.html', reports=[])


@app.route('/report/<report_id>', methods=['GET'])
def report(report_id):
    """Page détail d'un rapport"""
    try:
        db_conn = get_db()
        if db_conn is None:
            return render_template('500.html'), 500
        report_data = db_conn.get_report(report_id)
        if not report_data:
            return render_template('404.html'), 404
        return render_template('report.html', report=report_data, report_id=report_id)
    except Exception as e:
        logger.error(f"Erreur report: {e}")
        return render_template('500.html'), 500


# ═══════════════════════════════════════════════════════════════════════════
# API ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

@app.route('/api/upload', methods=['POST'])
def api_upload():
    """Upload et import de fichiers CSV"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'Pas de fichier'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'Fichier vide'}), 400
        
        filename = secure_filename(file.filename)
        filepath = Path(app.config['UPLOAD_FOLDER']) / filename
        file.save(str(filepath))
        
        # Importer le fichier
        importer = FileImporter()
        result = importer.import_file(str(filepath))
        
        if not result.get('success', False):
            return jsonify({
                'success': False,
                'error': result.get('errors', ['Erreur inconnue'])[0]
            }), 400
        
        # Sauvegarder dans la base de données
        entries = result.get('data', [])
        saved_count = 0
        
        try:
            from uuid import uuid4
            import json
            
            db_conn = get_db()
            if db_conn is None:
                return jsonify({'success': False, 'error': 'Base de données indisponible'}), 503
            
            # Créer un rapport d'import
            report_id = 'import_' + str(uuid4())[:12]
            conn = db_conn.get_connection()
            cursor = conn.cursor()
            
            # Calculer les stats avant d'insérer
            total_fax = len(entries)
            fax_envoyes = sum(1 for e in entries if e.get('mode') == 'SF')
            fax_recus = sum(1 for e in entries if e.get('mode') == 'RF')
            erreurs_totales = sum(1 for e in entries if e.get('erreurs'))
            taux_reussite = ((total_fax - erreurs_totales) / total_fax * 100) if total_fax > 0 else 0.0
            pages_totales = sum(e.get('pages', 0) or 0 for e in entries if isinstance(e.get('pages'), (int, float)))
            pages_sf = sum(e.get('pages', 0) or 0 for e in entries if e.get('mode') == 'SF')
            pages_rf = sum(e.get('pages', 0) or 0 for e in entries if e.get('mode') == 'RF')
            
            logger.info(f"Import: {total_fax} FAX, SF={fax_envoyes} ({pages_sf} pages), RF={fax_recus} ({pages_rf} pages)")
            
            # Insérer le rapport
            cursor.execute("""
                INSERT INTO reports (
                    id, date_rapport, contract_id, date_debut, date_fin,
                    fichier_source, total_fax, fax_envoyes, fax_recus,
                    pages_totales, pages_envoyees, pages_recues,
                    erreurs_totales, taux_reussite, donnees_json
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                report_id,
                datetime.now(),
                'IMPORT',
                datetime.now().date(),
                datetime.now().date(),
                filename,
                total_fax,
                fax_envoyes, fax_recus, pages_totales, pages_sf, pages_rf,
                erreurs_totales, taux_reussite,
                json.dumps({'import': True, 'stats': {
                    'total': total_fax, 'sent': fax_envoyes, 'received': fax_recus,
                    'errors': erreurs_totales, 'success_rate': taux_reussite,
                    'pages_sf': pages_sf, 'pages_rf': pages_rf
                }})
            ))
            
            conn.commit()
            
            # Maintenant insérer les entrées FAX
            for entry in entries:
                try:
                    entry_id = str(uuid4())
                    
                    cursor.execute("""
                        INSERT INTO fax_entries (
                            id, report_id, fax_id, utilisateur, mode, date_heure,
                            numero_original, numero_normalise, pages, valide, erreurs
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        entry_id,
                        report_id,
                        entry.get('fax_id') or '-',
                        entry.get('utilisateur') or 'N/A',
                        entry.get('mode') or '-',
                        entry.get('date_heure'),
                        entry.get('numero_envoi') or '-',
                        entry.get('numero') or '-',
                        entry.get('pages') or 0,
                        1,  # valide
                        entry.get('erreurs', '')  # erreurs
                    ))
                    saved_count += 1
                except Exception as e:
                    logger.warning(f"Erreur sauvegarde entrée: {e}")
            
            conn.commit()
            
            # Ajouter une entrée dans analysis_history
            try:
                analysis_id = str(uuid4())
                timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")
                
                cursor.execute("""
                    INSERT INTO analysis_history (
                        id, report_id, analysis_name, fichier_source, date_analyse,
                        total_fax, fax_envoyes, fax_recus, erreurs_totales, taux_reussite,
                        statut, message
                    ) VALUES (%s, %s, %s, %s, NOW(), %s, %s, %s, %s, %s, %s, %s)
                """, (
                    analysis_id,
                    report_id,
                    f"{filename.split('.')[0]} - {timestamp}",
                    filename,
                    len(entries),
                    sum(1 for e in entries if e.get('mode') == 'SF'),  # fax_envoyes
                    sum(1 for e in entries if e.get('mode') == 'RF'),  # fax_recus
                    sum(1 for e in entries if e.get('valide', True) == False or e.get('erreurs')),  # erreurs
                    100.0 if saved_count > 0 else 0.0,  # taux_reussite
                    'completed',
                    f"Import: {saved_count} FAX importés"
                ))
                conn.commit()
            except Exception as e:
                logger.warning(f"Erreur insertion analysis_history: {e}")
            
            cursor.close()
            conn.close()
        except Exception as e:
            logger.error(f"Erreur sauvegarde base: {e}")
            import traceback
            traceback.print_exc()
        
        return jsonify({
            'success': True,
            'report_id': report_id,
            'imported': saved_count,
            'total': len(entries),
            'errors': result.get('errors', []),
            'message': f"{saved_count}/{len(entries)} enregistrements importés"
        })
    
    except Exception as e:
        logger.error(f"Erreur upload: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500




# ═══════════════════════════════════════════════════════════════════════════
# API ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

@app.route('/api/stats', methods=['GET'])
def api_stats():
    """Récupérer les statistiques globales"""
    try:
        db_conn = get_db()
        if db_conn is None:
            return jsonify({'total': 0, 'sent': 0, 'received': 0, 'errors': 0})
        stats = db_conn.get_stats()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Erreur stats: {e}")
        return jsonify({'total': 0, 'sent': 0, 'received': 0, 'errors': 0})


@app.route('/api/entries', methods=['GET'])
def api_entries():
    """Récupérer les entrées avec pagination"""
    try:
        db_conn = get_db()
        if db_conn is None:
            return jsonify({'entries': [], 'total': 0, 'page': 1, 'limit': 100})
        
        filter_type = request.args.get('filter', 'all')
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 100))
        
        offset = (page - 1) * limit
        entries = db_conn.get_entries(limit=limit, offset=offset, filter_type=filter_type)
        total = db_conn.count_entries(filter_type=filter_type)
        
        return jsonify({
            'entries': entries,
            'total': total,
            'page': page,
            'limit': limit,
            'pages': (total + limit - 1) // limit
        })
    except Exception as e:
        logger.error(f"Erreur entries: {e}")
        return jsonify({'entries': [], 'total': 0, 'error': str(e)})


@app.route('/api/latest-reports', methods=['GET'])
def api_latest_reports():
    """Récupérer les 5 derniers rapports"""
    try:
        db_conn = get_db()
        if db_conn is None:
            return jsonify({'reports': []})
        
        reports = db_conn.list_reports(limit=5, offset=0)
        return jsonify({'reports': reports})
    except Exception as e:
        logger.error(f"Erreur latest-reports: {e}")
        return jsonify({'reports': [], 'error': str(e)})


@app.route('/api/report/<report_id>/data', methods=['GET'])
def api_report_data(report_id):
    """Récupérer les données complètes d'un rapport"""
    try:
        db_conn = get_db()
        if db_conn is None:
            return jsonify({'error': 'Base de données indisponible'}), 503
            
        conn = db_conn.get_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Récupérer le rapport
        cursor.execute("""
            SELECT id, date_rapport, fichier_source, total_fax, fax_envoyes, 
                   fax_recus, erreurs_totales, taux_reussite
            FROM reports
            WHERE id = %s
        """, (report_id,))
        
        report = cursor.fetchone()
        if not report:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Rapport non trouvé'}), 404
        
        # Récupérer TOUTES les entrées FAX de ce rapport (pas de limite)
        cursor.execute("""
            SELECT id, fax_id, utilisateur, mode, date_heure, numero_original,
                   numero_normalise, pages, valide, erreurs
            FROM fax_entries
            WHERE report_id = %s
            ORDER BY date_heure DESC
        """, (report_id,))
        
        entries = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Utiliser les stats réelles du rapport
        total = report['total_fax']
        sent = report['fax_envoyes']
        received = report['fax_recus']
        errors = report['erreurs_totales']
        success_rate = report['taux_reussite']
        
        # Calculer les pages SF et RF
        pages_sf = sum(e['pages'] or 0 for e in entries if e['mode'] == 'SF')
        pages_rf = sum(e['pages'] or 0 for e in entries if e['mode'] == 'RF')
        
        logger.info(f"Rapport {report_id}: {len(entries)} entrées, SF={pages_sf}, RF={pages_rf}")
        
        return jsonify({
            'id': report['id'],
            'title': f"Rapport - {report['fichier_source']}",
            'date': report['date_rapport'].strftime('%d/%m/%Y') if hasattr(report['date_rapport'], 'strftime') else str(report['date_rapport']),
            'summary': f"Rapport d'analyse FAX - {total} FAX analysés",
            'total': total,
            'sent': sent,
            'received': received,
            'errors': errors,
            'success_rate': success_rate,
            'pages_sf': pages_sf,
            'pages_rf': pages_rf,
            'entries_count': len(entries),
            'entries': entries
        })
    except Exception as e:
        logger.error(f"Erreur report data: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/report/<report_id>/entries', methods=['GET'])
def api_report_entries_paginated(report_id):
    """Récupérer les entrées FAX d'un rapport avec PAGINATION côté serveur (optimisé)"""
    try:
        db_conn = get_db()
        if db_conn is None:
            return jsonify({'error': 'Base de données indisponible'}), 503
        
        # Paramètres de pagination
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        search = request.args.get('search', '').strip()
        filter_type = request.args.get('filter', 'all')  # all, SF, RF, error
        
        page = max(1, page)
        limit = max(1, min(100, limit))  # Max 100 par page
        offset = (page - 1) * limit
        
        conn = db_conn.get_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Construire la requête SQL optimisée
        where_clauses = ["report_id = %s"]
        params = [report_id]
        
        # Filtrer par type
        if filter_type == 'SF':
            where_clauses.append("mode = 'SF'")
        elif filter_type == 'RF':
            where_clauses.append("mode = 'RF'")
        elif filter_type == 'error':
            where_clauses.append("valide = 0")
        
        # Recherche multi-champs (utilise les index!)
        if search:
            search_clause = """(
                fax_id LIKE %s OR
                utilisateur LIKE %s OR
                numero_original LIKE %s OR
                numero_normalise LIKE %s
            )"""
            where_clauses.append(search_clause)
            search_param = f"%{search}%"
            params.extend([search_param, search_param, search_param, search_param])
        
        where_sql = " AND ".join(where_clauses)
        
        # Requête optimisée avec COUNT en même temps
        count_query = f"SELECT COUNT(*) as total FROM fax_entries WHERE {where_sql}"
        cursor.execute(count_query, params)
        total = cursor.fetchone()['total']
        
        # Requête pour les données avec pagination
        data_query = f"""
            SELECT id, fax_id, utilisateur, mode, date_heure, numero_original,
                   numero_normalise, pages, valide, erreurs
            FROM fax_entries
            WHERE {where_sql}
            ORDER BY date_heure DESC
            LIMIT %s OFFSET %s
        """
        cursor.execute(data_query, params + [limit, offset])
        entries = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Calculer les stats pour ce filtre
        stats = {}
        if entries:
            success = sum(1 for e in entries if e['valide'] == 1)
            errors = sum(1 for e in entries if e['valide'] == 0)
            stats = {
                'success': success,
                'errors': errors,
                'success_rate': round((success / len(entries)) * 100, 1) if entries else 0
            }
        
        return jsonify({
            'entries': entries,
            'total': total,
            'page': page,
            'limit': limit,
            'pages': (total + limit - 1) // limit,
            'stats': stats
        })
    except Exception as e:
        logger.error(f"Erreur entries paginated: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/report/<report_id>/qrcode', methods=['GET'])
def api_report_qrcode(report_id):
    """Générer le QR code d'un rapport"""
    try:
        import qrcode
        import io
        
        # Construire l'URL publique
        public_url = "http://localhost:5000"  # Par défaut local
        if Config.USE_NGROK:
            ngrok_url = NgrokHelper.get_public_url()
            if ngrok_url:
                public_url = ngrok_url
        
        # QR code pointe directement vers le PDF téléchargeable
        report_url = f"{public_url}/api/report/{report_id}/pdf"
        
        # Générer le QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(report_url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convertir en PNG
        img_io = io.BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        
        return send_file(
            img_io,
            mimetype='image/png',
            as_attachment=False
        )
    except Exception as e:
        logger.error(f"Erreur QR: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/report/<report_id>/pdf', methods=['GET'])
def api_report_pdf(report_id):
    """Générer et télécharger PDF du rapport"""
    try:
        # Récupérer les données du rapport directement
        db_conn = get_db()
        if db_conn is None:
            return jsonify({'error': 'Base de données indisponible'}), 503
        
        conn = db_conn.get_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Récupérer le rapport
        cursor.execute("""
            SELECT id, date_rapport, fichier_source, total_fax, fax_envoyes, 
                   fax_recus, erreurs_totales, taux_reussite
            FROM reports
            WHERE id = %s
        """, (report_id,))
        
        report = cursor.fetchone()
        if not report:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Rapport non trouvé'}), 404
        
        # Récupérer les entrées FAX
        cursor.execute("""
            SELECT id, fax_id, utilisateur, mode, date_heure, numero_original,
                   numero_normalise, pages, valide, erreurs
            FROM fax_entries
            WHERE report_id = %s
            ORDER BY date_heure DESC
        """, (report_id,))
        
        entries = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Préparer les données pour le PDF
        report_data = {
            'id': report['id'],
            'title': f"Rapport - {report['fichier_source']}",
            'date': str(report['date_rapport']),
            'total': report['total_fax'],
            'sent': report['fax_envoyes'],
            'received': report['fax_recus'],
            'errors': report['erreurs_totales'],
            'success_rate': report['taux_reussite'],
            'entries': entries
        }
        
        # Générer le PDF
        pdf_buffer = PDFReportGenerator.generate_pdf(report_data)
        if pdf_buffer is None:
            return jsonify({'error': 'Erreur lors de la génération du PDF'}), 500
        
        pdf_buffer.seek(0)  # Remettre le curseur au début
        
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"rapport_{report_id}.pdf"
        )
    except Exception as e:
        logger.error(f"Erreur PDF: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/clear', methods=['POST'])
def api_clear():
    """Effacer toutes les données"""
    try:
        db_conn = get_db()
        if db_conn is None:
            return jsonify({'success': False, 'error': 'Base de données indisponible'}), 503
        db_conn.clear_all()
        return jsonify({'success': True, 'message': 'Données effacées'})
    except Exception as e:
        logger.error(f"Erreur clear: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500



# ═══════════════════════════════════════════════════════════════════════════
# PAGES D'ERREUR
# ═══════════════════════════════════════════════════════════════════════════

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500


# ═══════════════════════════════════════════════════════════════════════════
# LANCEMENT
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    logger.info("Demarrage du serveur: http://127.0.0.1:5000")
    
    # Demarrer ngrok en arriere-plan (si activé)
    if Config.USE_NGROK:
        logger.info("Demarrage de ngrok en arriere-plan...")
        NgrokHelper.start_tunnel_subprocess()
    else:
        logger.info("ngrok désactivé (USE_NGROK=false)")
    
    # Lancer Flask
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=True,
        use_reloader=False
    )
