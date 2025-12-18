from __future__ import annotations

import argparse
import csv
import io
import json
import logging
import threading
import time
import uuid
from pathlib import Path
import hashlib

from werkzeug.utils import secure_filename

from flask import Flask, Response, abort, jsonify, render_template, request, send_file

from src.core import (
    analyze_data,
    generate_report,
    get_all_reports,
    import_faxcloud_export,
    init_database,
    insert_report_to_db,
    settings,
)
from src.core.config import configure_logging, ensure_directories
from src.core.db import (
    delete_report,
    get_report_by_id,
    get_report_entries,
    get_report_summary_by_id,
    insert_audit_event,
)

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

    # In-memory upload progress (best-effort) for "real-time" UX.
    # Note: in multi-process deployments, each process has its own memory.
    _upload_jobs: dict[str, dict] = {}
    _upload_jobs_lock = threading.Lock()

    def _set_job(upload_id: str, **updates) -> None:
        with _upload_jobs_lock:
            job = _upload_jobs.get(upload_id)
            if not job:
                return
            job.update(updates)

    def _get_job(upload_id: str) -> dict | None:
        with _upload_jobs_lock:
            job = _upload_jobs.get(upload_id)
            return dict(job) if job else None

    def _prune_jobs() -> None:
        now = time.time()
        with _upload_jobs_lock:
            expired = [k for k, v in _upload_jobs.items() if v.get("expires_at", 0) < now]
            for k in expired:
                _upload_jobs.pop(k, None)

    def _current_user() -> str:
        # Auth retirée: on garde un champ user pour l'audit (valeur par défaut).
        return "local"

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
        include_entries = request.args.get("include_entries") in {"1", "true", "yes"}
        if include_entries:
            report = _ensure_report_derived_fields(get_report_by_id(report_id))
        else:
            report = _ensure_report_derived_fields(get_report_summary_by_id(report_id))
        if not report:
            return {"error": "Rapport non trouvé"}, 404
        return jsonify(report)

    @app.route("/api/report/<report_id>/entries", methods=["GET"])
    def api_report_entries(report_id: str):
        offset = request.args.get("offset", 0)
        limit = request.args.get("limit", 200)
        entry_type = request.args.get("type") or None
        valide = request.args.get("valide")
        q = request.args.get("q") or None
        date_from = request.args.get("date_from") or None
        date_to = request.args.get("date_to") or None
        pages_min = request.args.get("pages_min")
        pages_max = request.args.get("pages_max")
        order = request.args.get("order") or "asc"
        try:
            offset_i = int(offset)
        except Exception:
            offset_i = 0
        try:
            limit_i = int(limit)
        except Exception:
            limit_i = 200

        valide_i = None
        if valide is not None and str(valide).strip() != "":
            try:
                valide_i = int(valide)
            except Exception:
                valide_i = None

        pages_min_i = None
        if pages_min is not None and str(pages_min).strip() != "":
            try:
                pages_min_i = int(pages_min)
            except Exception:
                pages_min_i = None

        pages_max_i = None
        if pages_max is not None and str(pages_max).strip() != "":
            try:
                pages_max_i = int(pages_max)
            except Exception:
                pages_max_i = None

        rows, total = get_report_entries(
            report_id,
            offset=offset_i,
            limit=limit_i,
            entry_type=entry_type,
            valide=valide_i,
            q=q,
            date_from=date_from,
            date_to=date_to,
            pages_min=pages_min_i,
            pages_max=pages_max_i,
            order=order,
        )
        return jsonify({
            "report_id": report_id,
            "offset": offset_i,
            "limit": limit_i,
            "total": total,
            "filters": {
                "type": entry_type,
                "valide": valide_i,
                "q": q,
                "date_from": date_from,
                "date_to": date_to,
                "pages_min": pages_min_i,
                "pages_max": pages_max_i,
                "order": order,
            },
            "entries": rows,
        })

    @app.route("/api/report/<report_id>/export.json", methods=["GET"])
    def api_report_export_json(report_id: str):
        # Par défaut: summary + stats dérivées (léger). `include_entries=1` pour complet.
        include_entries = request.args.get("include_entries") in {"1", "true", "yes"}
        if include_entries:
            report = _ensure_report_derived_fields(get_report_by_id(report_id))
        else:
            report = _ensure_report_derived_fields(get_report_summary_by_id(report_id))

        if not report:
            return {"error": "Rapport non trouvé"}, 404

        insert_audit_event(
            action="export_json",
            user=_current_user(),
            report_id=report_id,
            ip=request.remote_addr,
            user_agent=request.headers.get("User-Agent"),
            meta={"include_entries": bool(include_entries)},
        )
        return jsonify(report)

    @app.route("/api/report/<report_id>/export.csv", methods=["GET"])
    def api_report_export_csv(report_id: str):
        # Export CSV streaming des entrées
        report = get_report_summary_by_id(report_id)
        if not report:
            return {"error": "Rapport non trouvé"}, 404

        # Optional filters for export (same as /entries)
        entry_type = request.args.get("type") or None
        valide = request.args.get("valide")
        q = request.args.get("q") or None
        date_from = request.args.get("date_from") or None
        date_to = request.args.get("date_to") or None
        pages_min = request.args.get("pages_min")
        pages_max = request.args.get("pages_max")
        order = request.args.get("order") or "asc"

        valide_i = None
        if valide is not None and str(valide).strip() != "":
            try:
                valide_i = int(valide)
            except Exception:
                valide_i = None

        pages_min_i = None
        if pages_min is not None and str(pages_min).strip() != "":
            try:
                pages_min_i = int(pages_min)
            except Exception:
                pages_min_i = None

        pages_max_i = None
        if pages_max is not None and str(pages_max).strip() != "":
            try:
                pages_max_i = int(pages_max)
            except Exception:
                pages_max_i = None

        insert_audit_event(
            action="export_csv",
            user=_current_user(),
            report_id=report_id,
            ip=request.remote_addr,
            user_agent=request.headers.get("User-Agent"),
            meta={
                "type": entry_type,
                "valide": valide_i,
                "q": q,
                "date_from": date_from,
                "date_to": date_to,
                "pages_min": pages_min_i,
                "pages_max": pages_max_i,
                "order": order,
            },
        )

        def generate():
            buffer = io.StringIO()
            writer = csv.writer(buffer, delimiter=";")
            writer.writerow([
                "id",
                "fax_id",
                "utilisateur",
                "type",
                "numero_original",
                "numero_normalise",
                "valide",
                "pages",
                "datetime",
                "erreurs",
            ])
            yield buffer.getvalue()
            buffer.seek(0)
            buffer.truncate(0)

            offset = 0
            page_size = 2000
            while True:
                rows, total = get_report_entries(
                    report_id,
                    offset=offset,
                    limit=page_size,
                    entry_type=entry_type,
                    valide=valide_i,
                    q=q,
                    date_from=date_from,
                    date_to=date_to,
                    pages_min=pages_min_i,
                    pages_max=pages_max_i,
                    order=order,
                )
                if not rows:
                    break
                for r in rows:
                    writer.writerow([
                        r.get("id"),
                        r.get("fax_id"),
                        r.get("utilisateur"),
                        r.get("type"),
                        r.get("numero_original"),
                        r.get("numero_normalise"),
                        r.get("valide"),
                        r.get("pages"),
                        r.get("datetime"),
                        r.get("erreurs"),
                    ])
                    yield buffer.getvalue()
                    buffer.seek(0)
                    buffer.truncate(0)
                offset += len(rows)
                if offset >= total:
                    break

        filename = f"faxcloud_report_{report_id}.csv"
        headers = {
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Type": "text/csv; charset=utf-8",
        }
        return Response(generate(), headers=headers)

    @app.route("/api/report/<report_id>/export.entries.json", methods=["GET"])
    def api_report_export_entries_json(report_id: str):
        # Streaming JSON array export for entries (optionally filtered)
        report = get_report_summary_by_id(report_id)
        if not report:
            return {"error": "Rapport non trouvé"}, 404

        entry_type = request.args.get("type") or None
        valide = request.args.get("valide")
        q = request.args.get("q") or None
        date_from = request.args.get("date_from") or None
        date_to = request.args.get("date_to") or None
        pages_min = request.args.get("pages_min")
        pages_max = request.args.get("pages_max")
        order = request.args.get("order") or "asc"

        valide_i = None
        if valide is not None and str(valide).strip() != "":
            try:
                valide_i = int(valide)
            except Exception:
                valide_i = None

        pages_min_i = None
        if pages_min is not None and str(pages_min).strip() != "":
            try:
                pages_min_i = int(pages_min)
            except Exception:
                pages_min_i = None

        pages_max_i = None
        if pages_max is not None and str(pages_max).strip() != "":
            try:
                pages_max_i = int(pages_max)
            except Exception:
                pages_max_i = None

        insert_audit_event(
            action="export_entries_json",
            user=_current_user(),
            report_id=report_id,
            ip=request.remote_addr,
            user_agent=request.headers.get("User-Agent"),
            meta={
                "type": entry_type,
                "valide": valide_i,
                "q": q,
                "date_from": date_from,
                "date_to": date_to,
                "pages_min": pages_min_i,
                "pages_max": pages_max_i,
                "order": order,
            },
        )

        def generate():
            yield "["
            first = True
            offset = 0
            page_size = 2000
            while True:
                rows, total = get_report_entries(
                    report_id,
                    offset=offset,
                    limit=page_size,
                    entry_type=entry_type,
                    valide=valide_i,
                    q=q,
                    date_from=date_from,
                    date_to=date_to,
                    pages_min=pages_min_i,
                    pages_max=pages_max_i,
                    order=order,
                )
                if not rows:
                    break
                for r in rows:
                    if first:
                        first = False
                    else:
                        yield ","
                    yield jsonify(r).get_data(as_text=True)
                offset += len(rows)
                if offset >= total:
                    break
            yield "]"

        filename = f"faxcloud_report_{report_id}_entries.json"
        headers = {
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Type": "application/json; charset=utf-8",
        }
        return Response(generate(), headers=headers)

    @app.route("/api/report/<report_id>", methods=["DELETE"])
    def api_report_delete(report_id: str):
        insert_audit_event(
            action="delete_report",
            user=_current_user(),
            report_id=report_id,
            ip=request.remote_addr,
            user_agent=request.headers.get("User-Agent"),
            meta=None,
        )
        delete_report(report_id)
        return {"success": True, "deleted": report_id}, 200

    @app.route("/api/report/<report_id>/qr", methods=["GET"])
    def api_report_qr(report_id: str):
        report = get_report_by_id(report_id)
        if not report or not report.get("qr_path"):
            return {"error": "QR code non trouvé"}, 404

        qr_path = Path(report["qr_path"])
        if not qr_path.exists():
            return {"error": "Fichier QR introuvable"}, 404

        return send_file(str(qr_path), mimetype="image/png")

    @app.route("/api/upload/<upload_id>/events", methods=["GET"])
    def api_upload_events(upload_id: str):
        def generate():
            last_payload = None
            last_ping = 0.0
            while True:
                job = _get_job(upload_id)
                if not job:
                    payload = {"success": False, "done": True, "error": "Upload inconnu"}
                    yield f"event: error\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"
                    break

                payload = {
                    "success": True,
                    "upload_id": upload_id,
                    "percent": int(job.get("percent", 0)),
                    "stage": job.get("stage") or "processing",
                    "message": job.get("message") or "",
                    "done": bool(job.get("done")),
                    "report_id": job.get("report_id"),
                    "error": job.get("error"),
                }

                if payload != last_payload:
                    yield f"event: progress\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"
                    last_payload = payload

                now = time.time()
                if now - last_ping > 10:
                    yield ": ping\n\n"
                    last_ping = now

                if payload["done"]:
                    _set_job(upload_id, expires_at=time.time() + 60)
                    break

                time.sleep(0.35)

            _prune_jobs()

        headers = {
            "Cache-Control": "no-cache",
            "Content-Type": "text/event-stream",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        }
        return Response(generate(), headers=headers)

    @app.route("/api/upload_async", methods=["POST"])
    def api_upload_async():
        if "file" not in request.files:
            return {"success": False, "error": "Pas de fichier"}, 400

        f = request.files["file"]
        if not f.filename:
            return {"success": False, "error": "Fichier vide"}, 400

        contract_id = request.form.get("contract") or None
        date_debut = request.form.get("start") or None
        date_fin = request.form.get("end") or None
        ip = request.remote_addr
        user_agent = request.headers.get("User-Agent")

        upload_id = str(uuid.uuid4())
        _prune_jobs()
        with _upload_jobs_lock:
            _upload_jobs[upload_id] = {
                "created_at": time.time(),
                "expires_at": time.time() + 3600,
                "percent": 0,
                "stage": "upload",
                "message": "Réception du fichier…",
                "done": False,
                "report_id": None,
                "error": None,
            }

        filename = secure_filename(f.filename)
        unique_name = f"{upload_id}_{filename}" if filename else upload_id
        filepath = Path(app.config["UPLOAD_FOLDER"]) / unique_name
        try:
            f.save(str(filepath))
        except Exception as e:
            _set_job(upload_id, done=True, error=str(e), stage="error", percent=100)
            return {"success": False, "error": "Échec sauvegarde fichier"}, 500

        def run_job():
            try:
                _set_job(upload_id, stage="hash", message="Vérification du fichier…", percent=5)

                try:
                    size = filepath.stat().st_size
                except Exception:
                    size = None

                sha256 = None
                try:
                    h = hashlib.sha256()
                    with open(filepath, "rb") as fp:
                        for chunk in iter(lambda: fp.read(1024 * 1024), b""):
                            h.update(chunk)
                    sha256 = h.hexdigest()
                except Exception:
                    sha256 = None

                _set_job(upload_id, stage="import", message="Import des données…", percent=15)
                rows = import_faxcloud_export(str(filepath))

                _set_job(upload_id, stage="analyze", message="Analyse…", percent=55)
                analysis = analyze_data(rows, contract_id, date_debut, date_fin)

                _set_job(upload_id, stage="report", message="Génération du rapport…", percent=75)
                report_data = generate_report(analysis)

                _set_job(upload_id, stage="save", message="Sauvegarde…", percent=90)
                insert_report_to_db(
                    report_data["report_id"],
                    report_data,
                    report_data.get("qr_path"),
                    source_filename=filename,
                    source_filesize=size,
                    source_sha256=sha256,
                )

                insert_audit_event(
                    action="upload",
                    user=_current_user(),
                    report_id=report_data["report_id"],
                    ip=ip,
                    user_agent=user_agent,
                    meta={
                        "filename": filename,
                        "filesize": size,
                        "sha256": sha256,
                        "contract": contract_id,
                        "start": date_debut,
                        "end": date_fin,
                        "async": True,
                    },
                )

                _set_job(
                    upload_id,
                    stage="done",
                    message="Terminé",
                    percent=100,
                    done=True,
                    report_id=report_data["report_id"],
                    error=None,
                )
            except Exception as e:
                _set_job(upload_id, stage="error", message="Erreur", percent=100, done=True, error=str(e))
            finally:
                try:
                    filepath.unlink(missing_ok=True)
                except Exception:
                    pass

        threading.Thread(target=run_job, daemon=True).start()
        return {"success": True, "upload_id": upload_id}, 200

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

        # Traçabilité fichier (utile pour un produit vendable)
        try:
            size = filepath.stat().st_size
        except Exception:
            size = None
        sha256 = None
        try:
            h = hashlib.sha256()
            with open(filepath, "rb") as fp:
                for chunk in iter(lambda: fp.read(1024 * 1024), b""):
                    h.update(chunk)
            sha256 = h.hexdigest()
        except Exception:
            sha256 = None

        contract_id = request.form.get("contract") or None
        date_debut = request.form.get("start") or None
        date_fin = request.form.get("end") or None

        rows = import_faxcloud_export(str(filepath))
        analysis = analyze_data(rows, contract_id, date_debut, date_fin)
        report_data = generate_report(analysis)
        insert_report_to_db(
            report_data["report_id"],
            report_data,
            report_data.get("qr_path"),
            source_filename=filename,
            source_filesize=size,
            source_sha256=sha256,
        )

        insert_audit_event(
            action="upload",
            user=_current_user(),
            report_id=report_data["report_id"],
            ip=request.remote_addr,
            user_agent=request.headers.get("User-Agent"),
            meta={
                "filename": filename,
                "filesize": size,
                "sha256": sha256,
                "contract": contract_id,
                "start": date_debut,
                "end": date_fin,
            },
        )

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
