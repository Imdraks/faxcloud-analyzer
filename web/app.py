"""
Application Flask pour FaxCloud Analyzer
Interface web responsive pour consulter les rapports et gérer les imports
"""

import sys
from pathlib import Path
from flask import Flask, render_template, jsonify, request, send_file
from flask_cors import CORS

# Ajouter src au chemin Python
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.config import Config
from core.db import Database
from core.reporter import ReportGenerator
from core.importer import FileImporter
from core.analyzer import FaxAnalyzer
import logging

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

Config.setup_logging()
logger = Config.get_logger(__name__)

# Créer l'app Flask
app = Flask(__name__, template_folder='templates', static_folder='static')
app.config.update(Config.FLASK_CONFIG)

# CORS
CORS(app)

# Initialiser les modules
db = Database()
reporter = ReportGenerator(db=db)
importer = FileImporter()
analyzer = FaxAnalyzer()

# ═══════════════════════════════════════════════════════════════════════════
# ROUTES
# ═══════════════════════════════════════════════════════════════════════════

@app.route('/')
def index():
    """Page d'accueil"""
    return render_template('index.html')

@app.route('/api/reports', methods=['GET'])
def get_reports():
    """API: Lister tous les rapports"""
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        offset = (page - 1) * limit
        
        reports = db.list_reports(limit=limit, offset=offset)
        stats = db.get_statistics()
        
        return jsonify({
            'success': True,
            'reports': reports,
            'stats': stats,
            'pagination': {
                'page': page,
                'limit': limit,
                'offset': offset
            }
        }), 200
    
    except Exception as e:
        logger.error(f"Erreur API reports: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/report/<report_id>', methods=['GET'])
def get_report(report_id):
    """API: Récupérer un rapport spécifique"""
    try:
        report_data = reporter.load_report_json(report_id)
        
        if not report_data:
            return jsonify({
                'success': False,
                'error': 'Rapport non trouvé'
            }), 404
        
        # Récupérer les entrées FAX de la DB
        entries = db.get_fax_entries(report_id)
        
        return jsonify({
            'success': True,
            'report': report_data,
            'entries': entries
        }), 200
    
    except Exception as e:
        logger.error(f"Erreur API report: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/report/<report_id>/errors', methods=['GET'])
def get_report_errors(report_id):
    """API: Récupérer uniquement les erreurs d'un rapport"""
    try:
        entries = db.get_fax_entries(report_id, only_errors=True)
        
        return jsonify({
            'success': True,
            'errors': entries,
            'error_count': len(entries)
        }), 200
    
    except Exception as e:
        logger.error(f"Erreur API errors: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """API: Uploader et traiter un fichier"""
    try:
        # Récupérer les paramètres
        contract_id = request.form.get('contract_id', 'CONTRACT_001')
        date_debut = request.form.get('date_debut', '2024-01-01')
        date_fin = request.form.get('date_fin', '2024-12-31')
        
        # Vérifier le fichier
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'Aucun fichier fourni'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'Nom de fichier vide'
            }), 400
        
        # Sauvegarder le fichier temporaire
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
            file.save(tmp.name)
            temp_path = tmp.name
        
        try:
            # Importer et analyser
            rows, import_info = importer.import_file(temp_path)
            analysis = analyzer.analyze_data(rows, contract_id, date_debut, date_fin)
            analysis['fichier_source'] = file.filename
            
            # Générer le rapport
            report = reporter.generate_report(analysis)
            
            if report['success']:
                return jsonify({
                    'success': True,
                    'message': report['message'],
                    'rapport_id': report['rapport_id'],
                    'report_url': report['report_url'],
                    'qr_path': report['qr_path']
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'error': report['message']
                }), 400
        
        finally:
            # Nettoyer le fichier temporaire
            import os
            try:
                os.remove(temp_path)
            except:
                pass
    
    except Exception as e:
        logger.error(f"Erreur API upload: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/config', methods=['GET'])
def get_config():
    """API: Récupérer la configuration"""
    try:
        return jsonify({
            'success': True,
            'config': Config.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"Erreur API config: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ═══════════════════════════════════════════════════════════════════════════
# PAGES WEB
# ═══════════════════════════════════════════════════════════════════════════

@app.route('/report/<report_id>')
def view_report(report_id):
    """Page de visualisation d'un rapport"""
    report_data = reporter.load_report_json(report_id)
    
    if not report_data:
        return render_template('404.html'), 404
    
    return render_template('report.html', report=report_data)

@app.route('/reports')
def list_all_reports():
    """Page de liste de tous les rapports"""
    return render_template('reports.html')

# ═══════════════════════════════════════════════════════════════════════════
# GESTION DES ERREURS
# ═══════════════════════════════════════════════════════════════════════════

@app.errorhandler(404)
def not_found(error):
    """Page 404"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Page 500"""
    logger.error(f"Erreur 500: {error}")
    return render_template('500.html'), 500

# ═══════════════════════════════════════════════════════════════════════════
# DÉMARRAGE
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    try:
        # Initialiser la base de données
        db.initialize()
        logger.info("Base de données initialisée")
        
        # Démarrer l'app
        logger.info(f"Démarrage du serveur: http://{Config.FLASK_CONFIG['HOST']}:{Config.FLASK_CONFIG['PORT']}")
        
        app.run(
            host=Config.FLASK_CONFIG['HOST'],
            port=Config.FLASK_CONFIG['PORT'],
            debug=Config.FLASK_CONFIG['DEBUG']
        )
    
    except Exception as e:
        logger.error(f"Erreur lors du démarrage: {e}")
        sys.exit(1)
