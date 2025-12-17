from __future__ import annotations

import argparse
import logging
from pathlib import Path

from werkzeug.utils import secure_filename

from flask import Flask, abort, jsonify, render_template, request, send_file, send_from_directory

from src.core import (
    analyze_data,
    generate_report,
    get_all_reports,
    get_report_by_id,
    import_faxcloud_export,
    init_database,
    insert_report_to_db,
    settings,
)
from src.core.config import configure_logging, ensure_directories

logger = logging.getLogger(__name__)


def _sanitize_none(value):
    if value is None:
        return None
    if isinstance(value, str) and value.strip().lower() in {"none", "null", ""}:
        return None
    return value


def _ensure_report_derived_fields(report_data: dict) -> dict:
    """Assure la présence des champs SF/RF et pages réelles (compat anciens rapports)."""
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

    report_data.setdefault("fax_sf", fax_sf)
    report_data.setdefault("fax_rf", fax_rf)
    report_data.setdefault("pages_reelles_sf", pages_sf)
    report_data.setdefault("pages_reelles_rf", pages_rf)
    report_data.setdefault("pages_reelles_totales", pages_sf + pages_rf)
    report_data.setdefault("pages_envoyees", pages_sf)
    report_data.setdefault("pages_recues", pages_rf)

    if report_data.get("fax_envoyes") in (None, ""):
        report_data["fax_envoyes"] = fax_sf
    if report_data.get("fax_recus") in (None, ""):
        report_data["fax_recus"] = fax_rf
    if report_data.get("pages_totales") in (None, ""):
        report_data["pages_totales"] = pages_sf + pages_rf

    if "fax_entries" not in report_data and "entries" in report_data:
        report_data["fax_entries"] = report_data["entries"]
    if "entries" not in report_data and "fax_entries" in report_data:
        report_data["entries"] = report_data["fax_entries"]

    return report_data


def create_app() -> Flask:
    ensure_directories()
    init_database()

    configure_logging()

    web_dir = settings.base_dir / "web"
    templates_dir = web_dir / "templates"
    static_dir = web_dir / "static"
    app = Flask(
        __name__,
        template_folder=str(templates_dir),
        static_folder=str(static_dir),
        static_url_path="/static",
    )

    app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024  # 100MB
    app.config["UPLOAD_FOLDER"] = str(settings.imports_dir)

    @app.route("/health")
    def health() -> tuple[dict, int]:
        return {"status": "ok"}, 200

    # ─────────────────────────────────────────────────────────────
    # Pages (SSR)
    # ─────────────────────────────────────────────────────────────

    @app.route("/", methods=["GET"])
    def index():
        reports = get_all_reports() or []
        return render_template("index.html", reports_count=len(reports))

    @app.route("/reports", methods=["GET"])
    def reports_page():
        reports = get_all_reports() or []
        return render_template("reports.html", reports=reports)

    @app.route("/report/<report_id>", methods=["GET"])
    def report_page(report_id: str):
        report = _ensure_report_derived_fields(get_report_by_id(report_id))
        if not report:
            return render_template("404.html"), 404
        return render_template("report.html", report=report)

    # ─────────────────────────────────────────────────────────────
    # API
    # ─────────────────────────────────────────────────────────────

    @app.route("/api/reports", methods=["GET"])
    def api_reports() -> tuple[dict, int]:
        reports = get_all_reports() or []
        return {"reports": reports, "count": len(reports)}, 200

    @app.route("/api/report/<report_id>", methods=["GET"])
    def api_report(report_id: str):
        report = _ensure_report_derived_fields(get_report_by_id(report_id))
        if not report:
            return {"error": "Rapport non trouvé"}, 404
        return jsonify(report)

    @app.route("/api/report/<report_id>/qr", methods=["GET"])
    def api_report_qr(report_id: str):
        report = get_report_by_id(report_id)
        if not report or not report.get("qr_path"):
            return {"error": "QR code non trouvé"}, 404

        qr_path = Path(report["qr_path"])
        if not qr_path.exists():
            return {"error": "Fichier QR introuvable"}, 404

        return send_file(str(qr_path), mimetype="image/png")

    @app.route("/api/upload", methods=["POST"])
    def api_upload():
        if "file" not in request.files:
            return {"success": False, "error": "Pas de fichier"}, 400

        f = request.files["file"]
        if not f.filename:
            return {"success": False, "error": "Fichier vide"}, 400

        filename = secure_filename(f.filename)
        filepath = Path(app.config["UPLOAD_FOLDER"]) / filename
        f.save(str(filepath))

        contract_id = request.form.get("contract") or None
        date_debut = request.form.get("start") or None
        date_fin = request.form.get("end") or None

        rows = import_faxcloud_export(str(filepath))
        analysis = analyze_data(rows, contract_id, date_debut, date_fin)
        report_data = generate_report(analysis)
        insert_report_to_db(report_data["report_id"], report_data, report_data.get("qr_path"))

        stats = report_data.get("statistics", {})
        return {
            "success": True,
            "report_id": report_data["report_id"],
            "total_fax": stats.get("total_fax", 0),
            "errors": stats.get("erreurs_totales", 0),
        }, 200

    return app


def main() -> None:
    parser = argparse.ArgumentParser(description="FaxCloud Analyzer - serveur web")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    app = create_app()
    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
