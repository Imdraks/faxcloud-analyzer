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
            from uuid import uuid4
            import json
            
            # Créer un rapport d'import
            report_id = 'import_' + str(uuid4())[:12]
            conn = db.get_connection()
            cursor = conn.cursor()
            
            # Calculer les stats avant d'insérer
            total_fax = len(entries)
            fax_envoyes = sum(1 for e in entries if e.get('mode') == 'SF')
            fax_recus = sum(1 for e in entries if e.get('mode') == 'RF')
            erreurs_totales = sum(1 for e in entries if e.get('erreurs'))
            taux_reussite = ((total_fax - erreurs_totales) / total_fax * 100) if total_fax > 0 else 0.0
            pages_totales = sum(e.get('pages_reelles', 0) for e in entries if isinstance(e.get('pages_reelles'), (int, float)))
            
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
                fax_envoyes, fax_recus, pages_totales, 0, 0,
                erreurs_totales, taux_reussite,
                json.dumps({'import': True, 'stats': {
                    'total': total_fax, 'sent': fax_envoyes, 'received': fax_recus,
                    'errors': erreurs_totales, 'success_rate': taux_reussite
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
    """Récupérer les données d'un rapport avec ses statistiques"""
    try:
        conn = db.get_connection()
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
        
        # Récupérer les entrées FAX de ce rapport
        cursor.execute("""
            SELECT id, fax_id, utilisateur, mode, date_heure, numero_original,
                   numero_normalise, pages, valide, erreurs
            FROM fax_entries
            WHERE report_id = %s
            ORDER BY date_heure DESC
            LIMIT 50
        """, (report_id,))
        
        entries = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Calculer les stats
        total = len(entries)
        sent = sum(1 for e in entries if e['mode'] == 'SF')
        received = sum(1 for e in entries if e['mode'] == 'RF')
        errors = sum(1 for e in entries if e['valide'] == 0)
        
        return jsonify({
            'id': report['id'],
            'title': f"Rapport - {report['fichier_source']}",
            'date': report['date_rapport'].strftime('%d/%m/%Y') if hasattr(report['date_rapport'], 'strftime') else str(report['date_rapport']),
            'summary': f"Rapport d'analyse FAX - {total} entrées",
            'total': total,
            'sent': sent,
            'received': received,
            'errors': errors,
            'entries': entries
        })
    except Exception as e:
        logger.error(f"Erreur report data: {e}")
        import traceback
        traceback.print_exc()
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
        debug=False,
        use_reloader=False
    )
