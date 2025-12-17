#!/usr/bin/env python3
"""
FaxCloud Analyzer - Web API
Serveur web Flask connecté à la CLI backend
"""

import json
import logging
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import sys

# Ajouter src au chemin
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.config import settings, ensure_directories, configure_logging
from core import (
    import_faxcloud_export,
    analyze_data,
    generate_report,
    insert_report_to_db,
    get_all_reports,
    get_report_by_id,
)

# ═══════════════════════════════════════════════════════════════════════════
# CONFIG FLASK
# ═══════════════════════════════════════════════════════════════════════════

app = Flask(__name__, 
    template_folder='templates',
    static_folder='static',
    static_url_path='/static')

app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB
app.config['UPLOAD_FOLDER'] = str(settings.imports_dir)

logger = logging.getLogger(__name__)

# Setup
ensure_directories()
configure_logging()


def _sanitize_none(value):
    if value is None:
        return None
    if isinstance(value, str) and value.strip().lower() in {"none", "null", ""}:
        return None
    return value


def _ensure_report_derived_fields(report_data: dict) -> dict:
    """Assure la présence des champs SF/RF et pages réelles pour le rendu HTML/JSON."""
    if not report_data:
        return report_data

    report_data["contract_id"] = _sanitize_none(report_data.get("contract_id"))
    report_data["date_debut"] = _sanitize_none(report_data.get("date_debut"))
    report_data["date_fin"] = _sanitize_none(report_data.get("date_fin"))

    entries = report_data.get("entries") or report_data.get("fax_entries") or []

    pages_sf = 0
    pages_rf = 0
    fax_sf = 0
    fax_rf = 0
    for e in entries:
        t = (e.get("type") or "").lower()
        pages = e.get("pages") or 0
        try:
            pages = int(pages)
        except Exception:
            pages = 0

        if t == "send":
            fax_sf += 1
            pages_sf += pages
        elif t == "receive":
            fax_rf += 1
            pages_rf += pages

    # Toujours exposer ces clés pour le template
    report_data.setdefault("fax_sf", fax_sf)
    report_data.setdefault("fax_rf", fax_rf)
    report_data.setdefault("pages_reelles_sf", pages_sf)
    report_data.setdefault("pages_reelles_rf", pages_rf)
    report_data.setdefault("pages_reelles_totales", pages_sf + pages_rf)
    report_data.setdefault("pages_envoyees", pages_sf)
    report_data.setdefault("pages_recues", pages_rf)

    # Fallbacks si la DB n'a pas ces colonnes (ou valeurs vides)
    if report_data.get("fax_envoyes") in (None, ""):
        report_data["fax_envoyes"] = fax_sf
    if report_data.get("fax_recus") in (None, ""):
        report_data["fax_recus"] = fax_rf
    if report_data.get("pages_totales") in (None, ""):
        report_data["pages_totales"] = pages_sf + pages_rf

    # Compat: exposer aussi `fax_entries` si uniquement `entries` existe
    if "fax_entries" not in report_data and "entries" in report_data:
        report_data["fax_entries"] = report_data["entries"]
    if "entries" not in report_data and "fax_entries" in report_data:
        report_data["entries"] = report_data["fax_entries"]

    return report_data

# ═══════════════════════════════════════════════════════════════════════════
# ROUTES
# ═══════════════════════════════════════════════════════════════════════════

@app.route('/', methods=['GET'])
def index():
    """Page d'accueil"""
    try:
        reports = get_all_reports()
        return render_template('index.html', reports_count=len(reports) if reports else 0)
    except Exception as e:
        print(f"Erreur: {e}")
        return render_template('index.html', reports_count=0)


@app.route('/reports', methods=['GET'])
def reports():
    """Liste des rapports"""
    try:
        reports_list = get_all_reports() or []
        return render_template('reports.html', reports=reports_list)
    except Exception as e:
        print(f"Erreur: {e}")
        return render_template('reports.html', reports=[])


@app.route('/report/<report_id>', methods=['GET'])
def report(report_id):
    """Détail d'un rapport"""
    try:
        report_data = _ensure_report_derived_fields(get_report_by_id(report_id))
        if not report_data:
            return render_template('404.html'), 404
        return render_template('report.html', report=report_data)
    except Exception as e:
        print(f"Erreur: {e}")
        return render_template('404.html'), 404


# ═══════════════════════════════════════════════════════════════════════════
# API ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

@app.route('/api/upload', methods=['POST'])
def api_upload():
    """Upload et import CSV"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'Pas de fichier'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'Fichier vide'}), 400
        
        # Sauvegarder
        filename = secure_filename(file.filename)
        filepath = Path(app.config['UPLOAD_FOLDER']) / filename
        file.save(str(filepath))

        contract_id = request.form.get("contract") or None
        date_debut = request.form.get("start") or None
        date_fin = request.form.get("end") or None
        
        # Importer via CLI backend
        rows = import_faxcloud_export(str(filepath))
        analysis = analyze_data(rows, contract_id, date_debut, date_fin)
        report_data = generate_report(analysis)
        insert_report_to_db(report_data["report_id"], report_data, report_data.get("qr_path"))

        stats = report_data.get("statistics", {})
        
        return jsonify({
            'success': True,
            'report_id': report_data["report_id"],
            'total_fax': stats.get('total_fax', 0),
            'errors': stats.get('erreurs_totales', 0)
        })
    
    except Exception as e:
        logger.exception("Erreur upload")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/reports', methods=['GET'])
def api_reports():
    """Liste des rapports (JSON)"""
    try:
        reports = get_all_reports() or []
        return jsonify({'reports': reports, 'count': len(reports)})
    except Exception as e:
        print(f"Erreur: {e}")
        return jsonify({'reports': [], 'count': 0})


@app.route('/api/report/<report_id>', methods=['GET'])
def api_report(report_id):
    """Détail rapport (JSON)"""
    try:
        report_data = _ensure_report_derived_fields(get_report_by_id(report_id))
        if not report_data:
            return jsonify({'error': 'Rapport non trouvé'}), 404
        return jsonify(report_data)
    except Exception as e:
        print(f"Erreur: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/report/<report_id>/qr', methods=['GET'])
def api_report_qr(report_id):
    """Télécharger QR code"""
    try:
        report_data = get_report_by_id(report_id)
        if not report_data or not report_data.get('qr_path'):
            return jsonify({'error': 'QR code non trouvé'}), 404
        
        qr_path = Path(report_data['qr_path'])
        if not qr_path.exists():
            return jsonify({'error': 'Fichier QR introuvable'}), 404
        
        return send_file(str(qr_path), mimetype='image/png')
    except Exception as e:
        print(f"Erreur QR: {e}")
        return jsonify({'error': str(e)}), 500


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
    print("Demarrage du serveur FaxCloud Analyzer")
    print("http://127.0.0.1:5000")
    print("CTRL+C pour arreter")
    app.run(host='127.0.0.1', port=5000, debug=False)
