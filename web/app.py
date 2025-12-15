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
from werkzeug.utils import secure_filename

# Ajouter src au chemin Python
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.config import Config
from core.importer import FileImporter
from core.analyzer import FaxAnalyzer
from core.reporter import ReportGenerator
from core.db_mysql import DatabaseMySQL
from core.ngrok_helper import NgrokHelper

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION FLASK
# ═══════════════════════════════════════════════════════════════════════════

app = Flask(__name__, 
    template_folder='templates',
    static_folder='static',
    static_url_path='/static')

app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB
app.config['UPLOAD_FOLDER'] = Config.IMPORTS_DIR

# Setup logging
Config.ensure_directories()
Config.setup_logging()
logger = Config.get_logger(__name__)

# Initialiser la base de données
try:
    db = DatabaseMySQL()
    db.initialize()
    logger.info("Base de donnees initialisee")
except Exception as e:
    logger.error(f"Erreur BD: {e}")

# ═══════════════════════════════════════════════════════════════════════════
# ROUTES PRINCIPALES
# ═══════════════════════════════════════════════════════════════════════════

@app.route('/', methods=['GET'])
def index():
    """Page d'accueil - Import CSV"""
    try:
        stats = db.get_stats()
        return render_template('index.html', stats=stats)
    except Exception as e:
        logger.error(f"Erreur index: {e}")
        return render_template('index.html', stats={})


@app.route('/reports', methods=['GET'])
def reports():
    """Page liste des rapports"""
    try:
        reports_list = db.get_reports_list()
        return render_template('reports.html', reports=reports_list)
    except Exception as e:
        logger.error(f"Erreur reports: {e}")
        return render_template('reports.html', reports=[])


@app.route('/report/<report_id>', methods=['GET'])
def report(report_id):
    """Page détail d'un rapport"""
    try:
        report_data = db.get_report(report_id)
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
            conn = db.get_connection()
            cursor = conn.cursor()
            from uuid import uuid4
            
            for entry in entries:
                try:
                    # Créer un ID unique pour l'entrée
                    entry_id = str(uuid4())
                    
                    # Insérer directement dans la BDD
                    cursor.execute("""
                        INSERT INTO fax_entries (
                            id, report_id, fax_id, utilisateur, mode, date_heure,
                            numero_original, numero_normalise, pages, valide, erreurs
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        entry_id,
                        'import_' + entry_id[:8],  # report_id temporaire
                        entry.get('fax_id'),
                        entry.get('utilisateur'),
                        entry.get('mode'),
                        entry.get('datetime'),
                        entry.get('numero_envoi'),
                        entry.get('numero_appele'),
                        entry.get('pages_reelles'),
                        1,  # valide
                        ''  # pas d'erreurs
                    ))
                    saved_count += 1
                except Exception as e:
                    logger.warning(f"Erreur sauvegarde entrée: {e}")
            
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as e:
            logger.error(f"Erreur sauvegarde base: {e}")
            saved_count = 0
        
        return jsonify({
            'success': True,
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


@app.route('/api/stats', methods=['GET'])
def api_stats():
    """Récupérer les statistiques"""
    try:
        stats = db.get_stats()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Erreur stats: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/entries', methods=['GET'])
def api_entries():
    """Récupérer les entrées avec filtres"""
    try:
        filter_type = request.args.get('filter', 'all')
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        
        offset = (page - 1) * limit
        entries = db.get_entries(limit=limit, offset=offset, filter_type=filter_type)
        total = db.count_entries(filter_type=filter_type)
        
        return jsonify({
            'entries': entries,
            'total': total,
            'page': page,
            'pages': (total + limit - 1) // limit
        })
    except Exception as e:
        logger.error(f"Erreur entries: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/report/<report_id>/data', methods=['GET'])
def api_report_data(report_id):
    """Récupérer les données d'un rapport"""
    try:
        report_data = db.get_report(report_id)
        if not report_data:
            return jsonify({'error': 'Rapport non trouvé'}), 404
        return jsonify(report_data)
    except Exception as e:
        logger.error(f"Erreur report data: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/report/<report_id>/pdf', methods=['GET'])
def api_report_pdf(report_id):
    """Générer et télécharger PDF du rapport"""
    try:
        report_data = db.get_report(report_id)
        if not report_data:
            return jsonify({'error': 'Rapport non trouvé'}), 404
        
        # Récupérer l'URL publique ngrok si disponible
        public_url = NgrokHelper.get_public_url() or "http://localhost:5000"
        
        # Générer le PDF avec QR code
        generator = ReportGenerator(db, public_url=public_url)
        pdf_bytes = generator.generate_pdf_report(report_data)
        
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"rapport_{report_id}.pdf"
        )
    except Exception as e:
        logger.error(f"Erreur PDF: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/report/<report_id>/qrcode', methods=['GET'])
def api_report_qrcode(report_id):
    """Générer le QR code d'un rapport"""
    try:
        from core.pdf_generator import QRCodeGenerator
        
        # Récupérer l'URL publique
        public_url = NgrokHelper.get_public_url() or "http://localhost:5000"
        report_url = f"{public_url}/report/{report_id}"
        
        # Générer le QR code
        qr_gen = QRCodeGenerator()
        qr_image = qr_gen.generate(report_url)
        
        return send_file(
            io.BytesIO(qr_image),
            mimetype='image/png'
        )
    except Exception as e:
        logger.error(f"Erreur QR: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/clear', methods=['POST'])
def api_clear():
    """Effacer toutes les données"""
    try:
        db.clear_all()
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
    
    # Demarrer ngrok en arriere-plan
    logger.info("Demarrage de ngrok en arriere-plan...")
    NgrokHelper.start_tunnel_subprocess()
    
    # Lancer Flask
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=False,
        use_reloader=False
    )
