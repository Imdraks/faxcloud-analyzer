"""
Application Flask pour FaxCloud Analyzer
Interface web pour consulter les rapports et gérer les imports
"""

import sys
import os
from pathlib import Path
from flask import Flask, render_template, jsonify, request, send_file
from flask_cors import CORS
import logging
import tempfile

# Ajouter src au chemin Python
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.config import Config
from core.db import Database
from core.reporter import ReportGenerator
from core.importer import FileImporter
from core.analyzer import FaxAnalyzer
from core.ngrok_helper import NgrokHelper
from core.pdf_generator import PDFReportGenerator

# Configuration du logging
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
# ROUTES - PAGE D'ACCUEIL
# ═══════════════════════════════════════════════════════════════════════════

@app.route('/')
def index():
    """Page d'accueil"""
    return render_template('index.html')

@app.route('/reports')
def reports_page():
    """Page de liste des rapports"""
    return render_template('reports.html')

@app.route('/report/<report_id>')
def report_detail(report_id):
    """Page de détail d'un rapport"""
    return render_template('report.html', report_id=report_id)

@app.route('/qrcode/<report_id>')
def get_qrcode(report_id):
    """Retourne le QR code d'un rapport"""
    from flask import send_file
    try:
        qr_path = Config.REPORTS_QR_DIR / f"{report_id}.png"
        if qr_path.exists():
            return send_file(str(qr_path), mimetype='image/png')
        else:
            return jsonify({'error': 'QR code not found'}), 404
    except Exception as e:
        logger.error(f"Erreur chargement QR code: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/report/<report_id>/pdf')
def get_report_pdf(report_id):
    """Génère et retourne un PDF du rapport"""
    try:
        # Récupérer les données du rapport
        report_json = db.get_report_data(report_id)
        if not report_json:
            return jsonify({'error': 'Report not found'}), 404
        
        # Parser le JSON
        import json
        report_data = json.loads(report_json) if isinstance(report_json, str) else report_json
        
        # Récupérer les FAX entries
        fax_entries = db.get_fax_entries(report_id)
        
        # Préparer les données pour le PDF
        pdf_data = {
            'id': report_id,
            'analysis_name': report_data.get('analysis_name', 'Sans nom'),
            'date_analyse': report_data.get('date_analyse', 'N/A'),
            'stats': {
                'total_fax': len(fax_entries),
                'fax_envoyes': len([f for f in fax_entries if f.get('statut', '').lower() == 'envoyé']),
                'fax_recus': len([f for f in fax_entries if f.get('statut', '').lower() == 'reçu']),
                'erreurs_totales': len([f for f in fax_entries if f.get('statut', '').lower() == 'erreur']),
                'taux_reussite': report_data.get('taux_reussite', 0)
            },
            'fax_data': fax_entries
        }
        
        # Générer le PDF
        pdf_buffer = PDFReportGenerator.generate_pdf(pdf_data)
        
        if not pdf_buffer:
            return jsonify({'error': 'Failed to generate PDF'}), 500
        
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'rapport_{report_id}.pdf'
        )
    
    except Exception as e:
        logger.error(f"Erreur génération PDF: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

# ═══════════════════════════════════════════════════════════════════════════
# API - GESTION FICHIERS (ENDPOINT PRINCIPAL)
# ═══════════════════════════════════════════════════════════════════════════

@app.route('/api/import', methods=['POST'])
def api_import_file():
    """
    API: Importer et analyser un fichier CSV/XLSX
    Endpoint simplifié sans paramètres - prend juste le fichier
    """
    try:
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
        
        # Valider l'extension
        allowed_extensions = {'.csv', '.xlsx', '.xls'}
        file_ext = Path(file.filename).suffix.lower()
        
        if file_ext not in allowed_extensions:
            return jsonify({
                'success': False,
                'error': f'Format non supporté. Fichiers acceptés: CSV, XLSX'
            }), 400
        
        # Sauvegarder temporairement
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
            file.save(tmp.name)
            temp_path = tmp.name
        
        try:
            logger.info(f"Importation du fichier: {file.filename}")
            
            # Importer le fichier
            import_result = importer.import_file(temp_path)
            
            if not import_result.get('success'):
                logger.error(f"Erreur import: {import_result.get('errors')}")
                return jsonify({
                    'success': False,
                    'error': f'Erreur lors de l\'import du fichier'
                }), 400
            
            rows = import_result.get('data', [])
            logger.info(f"Fichier charge: {len(rows)} lignes")
            
            # Analyser les données avec paramètres par défaut
            analysis = analyzer.analyze_data(
                rows,
                contract_id='AUTO_IMPORT',
                date_debut='2024-01-01',
                date_fin='2024-12-31'
            )
            analysis['fichier_source'] = file.filename
            
            # Générer le rapport
            report_result = reporter.generate_report(analysis)
            
            if report_result['success']:
                logger.info(f"Rapport genere: {report_result['rapport_id']}")
                
                stats = analysis.get('statistics', {})
                
                return jsonify({
                    'success': True,
                    'message': 'Fichier importé et analysé avec succès',
                    'rapport_id': report_result['rapport_id'],
                    'report_url': f"/report/{report_result['rapport_id']}",
                    'stats': {
                        'total_fax': stats.get('total_fax', 0),
                        'fax_envoyes': stats.get('fax_envoyes', 0),
                        'fax_recus': stats.get('fax_recus', 0),
                        'pages_totales': stats.get('pages_totales', 0),
                        'erreurs_totales': stats.get('erreurs_totales', 0),
                        'taux_reussite': stats.get('taux_reussite', 0)
                    }
                }), 200
            else:
                logger.error(f"Erreur rapport: {report_result.get('message')}")
                return jsonify({
                    'success': False,
                    'error': report_result.get('message', 'Erreur lors de la génération du rapport')
                }), 500
        
        except Exception as e:
            logger.error(f"Erreur lors du traitement: {str(e)}", exc_info=True)
            return jsonify({
                'success': False,
                'error': f'Erreur lors de l\'analyse: {str(e)}'
            }), 500
        
        finally:
            # Nettoyer le fichier temporaire
            try:
                os.remove(temp_path)
            except:
                pass
    
    except Exception as e:
        logger.error(f"Erreur API import: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ═══════════════════════════════════════════════════════════════════════════
# API - CONSULTATION RAPPORTS
# ═══════════════════════════════════════════════════════════════════════════

@app.route('/api/reports', methods=['GET'])
def api_list_reports():
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
                'limit': limit
            }
        }), 200
    
    except Exception as e:
        logger.error(f"Erreur API reports: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/report/<report_id>', methods=['GET'])
def api_get_report(report_id):
    """API: Récupérer les détails d'un rapport"""
    try:
        report_data = reporter.load_report_json(report_id)
        
        if not report_data:
            return jsonify({
                'success': False,
                'error': 'Rapport non trouvé'
            }), 404
        
        # Récupérer les entrées
        entries = db.get_fax_entries(report_id)
        
        return jsonify({
            'success': True,
            'report': report_data,
            'entries': entries
        }), 200
    
    except Exception as e:
        logger.error(f"Erreur API report detail: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/report/<report_id>/entries', methods=['GET'])
def api_get_report_entries(report_id):
    """API: Récupérer les entrées (lignes FAX) d'un rapport"""
    try:
        only_errors = request.args.get('errors_only', False, type=bool)
        entries = db.get_fax_entries(report_id, only_errors=only_errors)
        
        return jsonify({
            'success': True,
            'entries': entries,
            'count': len(entries)
        }), 200
    
    except Exception as e:
        logger.error(f"Erreur API report entries: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/report/<report_id>/errors', methods=['GET'])
def api_get_report_errors(report_id):
    """API: Récupérer uniquement les erreurs d'un rapport"""
    try:
        entries = db.get_fax_entries(report_id, only_errors=True)
        
        return jsonify({
            'success': True,
            'errors': entries,
            'error_count': len(entries)
        }), 200
    
    except Exception as e:
        logger.error(f"Erreur API report errors: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/analysis_history', methods=['GET'])
def api_get_analysis_history():
    """API: Récupérer l'historique des analyses"""
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        offset = (page - 1) * limit
        
        analyses = db.get_analysis_history(limit=limit, offset=offset)
        
        return jsonify({
            'success': True,
            'analyses': analyses,
            'pagination': {
                'page': page,
                'limit': limit
            }
        }), 200
    
    except Exception as e:
        logger.error(f"Erreur API analysis_history: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ═══════════════════════════════════════════════════════════════════════════
# API - PARTAGE DE RAPPORTS
# ═══════════════════════════════════════════════════════════════════════════

@app.route('/api/report/<report_id>/share', methods=['POST'])
def api_create_share_link(report_id):
    """API: Créer un lien de partage pour un rapport"""
    try:
        days = request.json.get('days', 7) if request.json else 7
        utilisateur = request.json.get('utilisateur') if request.json else None
        
        token = db.create_share_token(report_id, days=days, utilisateur=utilisateur)
        
        share_url = f"{request.host_url.rstrip('/')}/share/{token}"
        
        return jsonify({
            'success': True,
            'token': token,
            'share_url': share_url,
            'expires_in_days': days,
            'message': 'Lien de partage créé avec succès'
        }), 200
    
    except Exception as e:
        logger.error(f"Erreur API create_share_link: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/share/<token>')
def share_report(token):
    """Page publique pour accéder à un rapport partagé"""
    try:
        report_data = db.get_report_by_share_token(token)
        
        if not report_data:
            return render_template('404.html'), 404
        
        return render_template('report.html', report_id=report_data['rapport_id'])
    
    except Exception as e:
        logger.error(f"Erreur share_report: {str(e)}", exc_info=True)
        return render_template('500.html'), 500

@app.route('/api/share/<token>/report', methods=['GET'])
def api_get_shared_report(token):
    """API: Récupérer un rapport partagé"""
    try:
        report_data = db.get_report_by_share_token(token)
        
        if not report_data:
            return jsonify({
                'success': False,
                'error': 'Lien expiré ou invalide'
            }), 403
        
        entries = db.get_fax_entries(report_data['rapport_id'])
        
        return jsonify({
            'success': True,
            'report': report_data,
            'entries': entries
        }), 200
    
    except Exception as e:
        logger.error(f"Erreur API get_shared_report: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 403

# ═══════════════════════════════════════════════════════════════════════════
# GESTION DES ERREURS
# ═══════════════════════════════════════════════════════════════════════════

@app.errorhandler(404)
def not_found(error):
    """Erreur 404"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Erreur 500"""
    logger.error(f"Erreur 500: {error}")
    return render_template('500.html'), 500

# ═══════════════════════════════════════════════════════════════════════════
# DÉMARRAGE
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    try:
        # Initialiser la base de données
        db.initialize()
        logger.info("Base de donnees initialisee")
        
        # Démarrer l'app
        host = Config.FLASK_CONFIG.get('HOST', '127.0.0.1')
        port = Config.FLASK_CONFIG.get('PORT', 5000)
        
        # Vérifier si on veut ngrok (env var ou en local)
        use_ngrok = os.environ.get('USE_NGROK', 'true').lower() == 'true'
        
        logger.info(f"Demarrage du serveur: http://{host}:{port}")
        
        # Si ngrok est activé, le démarrer dans un thread
        if use_ngrok:
            try:
                import threading
                from time import sleep
                
                def start_ngrok():
                    sleep(3)  # Attendre que Flask démarre
                    NgrokHelper.start_tunnel_subprocess(port)
                
                ngrok_thread = threading.Thread(target=start_ngrok, daemon=True)
                ngrok_thread.start()
                logger.info("Démarrage de ngrok en arrière-plan...")
            except Exception as e:
                logger.warning(f"Erreur ngrok: {e}")
        else:
            logger.info("ngrok désactivé (USE_NGROK=false)")
        
        app.run(
            host=host,
            port=port,
            debug=Config.FLASK_CONFIG.get('DEBUG', False),
            use_reloader=False
        )
    
    except Exception as e:
        logger.error(f"Erreur lors du demarrage: {str(e)}", exc_info=True)
        sys.exit(1)
