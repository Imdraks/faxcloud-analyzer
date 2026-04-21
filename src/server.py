from __future__ import annotations

import argparse
import csv
import io
import json
import logging
import os
import threading
import time
import uuid
from collections import defaultdict
from datetime import datetime, timezone
from functools import wraps
from pathlib import Path
import hashlib

from werkzeug.utils import secure_filename

from flask import Flask, Response, abort, jsonify, render_template, request, send_file

# ─────────────────────────────────────────────────────────────
# Application metadata
# ─────────────────────────────────────────────────────────────
__version__ = "1.2.0"
__app_name__ = "FaxCloud Analyzer"
__description__ = "Analyseur intelligent pour exports FaxCloud"

# Rate limiting configuration (requests per minute per IP)
RATE_LIMIT_REQUESTS = int(os.environ.get("RATE_LIMIT_REQUESTS", 120))
RATE_LIMIT_WINDOW = int(os.environ.get("RATE_LIMIT_WINDOW", 60))  # seconds

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
    get_dashboard_stats,
    get_report_by_id,
    get_report_entries,
    get_report_summary_by_id,
    insert_audit_event,
)
from src.core.asterisk import (
    init_asterisk_tables,
    get_sda_ranges,
    add_sda_range,
    update_sda_range,
    delete_sda_range,
    get_ami_config,
    save_ami_config,
    get_engine as get_asterisk_engine,
    reload_engine as reload_asterisk_engine,
    NUMBER_TYPE_LABELS,
    get_all_cached_tones,
    clear_tone_cache,
    get_dialplan_snippet,
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
    init_asterisk_tables()

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
    app.config["JSON_AS_ASCII"] = False
    app.config["JSON_SORT_KEYS"] = False

    # ─────────────────────────────────────────────────────────────
    # Simple in-memory rate limiter
    # ─────────────────────────────────────────────────────────────
    _rate_limit_store: dict[str, list[float]] = defaultdict(list)
    _rate_limit_lock = threading.Lock()

    def _check_rate_limit(ip: str) -> bool:
        """Returns True if request is allowed, False if rate limited."""
        now = time.time()
        window_start = now - RATE_LIMIT_WINDOW
        
        with _rate_limit_lock:
            # Clean old entries
            _rate_limit_store[ip] = [t for t in _rate_limit_store[ip] if t > window_start]
            
            if len(_rate_limit_store[ip]) >= RATE_LIMIT_REQUESTS:
                return False
            
            _rate_limit_store[ip].append(now)
            return True

    @app.before_request
    def rate_limit_check():
        """Apply rate limiting to API endpoints."""
        if request.path.startswith("/api/") and not request.path.startswith("/api/health"):
            ip = request.remote_addr or "unknown"
            if not _check_rate_limit(ip):
                logger.warning("Rate limit exceeded for IP: %s", ip)
                return {"error": "Trop de requêtes. Réessayez dans quelques secondes."}, 429

    # ─────────────────────────────────────────────────────────────
    # Error handlers
    # ─────────────────────────────────────────────────────────────
    @app.errorhandler(404)
    def not_found_error(error):
        if request.path.startswith("/api/"):
            return {"error": "Ressource non trouvée"}, 404
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.exception("Internal server error: %s", error)
        if request.path.startswith("/api/"):
            return {"error": "Erreur interne du serveur"}, 500
        return render_template("500.html"), 500

    @app.errorhandler(413)
    def file_too_large(error):
        return {"error": "Fichier trop volumineux (max 100MB)"}, 413

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

    @app.route("/api/health")
    def api_health() -> tuple[dict, int]:
        """Health check endpoint pour Docker/Kubernetes/monitoring."""
        import platform
        try:
            db_ok = True
            init_database()
        except Exception:
            db_ok = False
        
        return {
            "status": "healthy" if db_ok else "degraded",
            "version": __version__,
            "app": __app_name__,
            "database": "ok" if db_ok else "error",
            "platform": platform.machine(),
            "python": platform.python_version(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }, 200 if db_ok else 503

    @app.route("/api/info")
    def api_info() -> tuple[dict, int]:
        """Information about the API."""
        return {
            "name": __app_name__,
            "version": __version__,
            "description": __description__,
            "endpoints": {
                "health": "/api/health",
                "reports": "/api/reports",
                "report": "/api/report/<id>",
                "entries": "/api/report/<id>/entries",
                "upload": "/api/upload",
                "upload_async": "/api/upload_async",
                "asterisk_config": "/api/asterisk/config",
                "asterisk_sda": "/api/asterisk/sda",
                "asterisk_classify": "/api/asterisk/classify",
                "asterisk_types": "/api/asterisk/types",
                "asterisk_stats": "/api/asterisk/stats/<id>",
                "asterisk_detect": "/api/asterisk/detect",
                "asterisk_detect_single": "/api/asterisk/detect/<numero>",
                "asterisk_cache": "/api/asterisk/cache",
                "asterisk_dialplan": "/api/asterisk/dialplan",
            },
        }, 200

    # ─────────────────────────────────────────────────────────────
    # Pages (SSR)
    # ─────────────────────────────────────────────────────────────

    @app.route("/", methods=["GET"])
    def index():
        dashboard = get_dashboard_stats()
        return render_template(
            "index.html",
            reports_count=dashboard.get("reports_count", 0),
            dashboard=dashboard,
        )

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
                "numero_type",
                "numero_type_label",
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
                        r.get("numero_type", ""),
                        r.get("numero_type_label", ""),
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

    # ─────────────────────────────────────────────────────────────
    # API Asterisk / SDA
    # ─────────────────────────────────────────────────────────────

    @app.route("/api/asterisk/config", methods=["GET"])
    def api_asterisk_config():
        """Retourne la configuration AMI Asterisk."""
        config = get_ami_config()
        # Ne pas exposer le secret en clair
        if config.get("ami_secret"):
            config["ami_secret"] = "********"
        return jsonify(config)

    @app.route("/api/asterisk/config", methods=["PUT"])
    def api_asterisk_config_update():
        """Met à jour la configuration AMI Asterisk."""
        data = request.get_json(silent=True) or {}
        host = data.get("ami_host", "127.0.0.1")
        port = int(data.get("ami_port", 5038))
        username = data.get("ami_username", "admin")
        secret = data.get("ami_secret", "")
        enabled = bool(data.get("ami_enabled", False))

        # Si le secret est masqué, garder l'ancien
        if secret == "********":
            old_config = get_ami_config()
            secret = old_config.get("ami_secret", "")

        # Nouveaux paramètres de détection
        context = data.get("ami_context", "faxcloud-detect")
        caller_id = data.get("ami_caller_id", "FaxCloudTest")
        call_timeout = int(data.get("ami_call_timeout", 15))
        detect_timeout = int(data.get("ami_detect_timeout", 10))
        trunk = data.get("ami_trunk", "")
        cache_ttl_hours = int(data.get("cache_ttl_hours", 168))
        simulation = bool(data.get("ami_simulation", False))

        save_ami_config(host, port, username, secret, enabled,
                        context, caller_id, call_timeout, detect_timeout,
                        trunk, cache_ttl_hours, simulation)
        reload_asterisk_engine()

        insert_audit_event(
            action="asterisk_config_update",
            user=_current_user(),
            ip=request.remote_addr,
            user_agent=request.headers.get("User-Agent"),
        )
        return {"success": True, "message": "Configuration AMI mise à jour"}, 200

    @app.route("/api/asterisk/sda", methods=["GET"])
    def api_sda_ranges():
        """Liste toutes les plages SDA configurées."""
        ranges = get_sda_ranges()
        return jsonify({"ranges": ranges, "count": len(ranges)})

    @app.route("/api/asterisk/sda", methods=["POST"])
    def api_sda_range_add():
        """Ajoute une plage SDA."""
        data = request.get_json(silent=True) or {}
        label = data.get("label", "").strip()
        prefix = data.get("prefix", "").strip()

        if not label or not prefix:
            return {"error": "label et prefix sont requis"}, 400

        result = add_sda_range(
            label=label,
            prefix=prefix,
            range_start=data.get("range_start", ""),
            range_end=data.get("range_end", ""),
            site=data.get("site", ""),
            description=data.get("description", ""),
        )
        reload_asterisk_engine()

        insert_audit_event(
            action="sda_range_add",
            user=_current_user(),
            ip=request.remote_addr,
            user_agent=request.headers.get("User-Agent"),
            meta={"label": label, "prefix": prefix},
        )
        return jsonify({"success": True, "range": result}), 201

    @app.route("/api/asterisk/sda/<int:range_id>", methods=["PUT"])
    def api_sda_range_update(range_id: int):
        """Met à jour une plage SDA."""
        data = request.get_json(silent=True) or {}
        updated = update_sda_range(range_id, **data)
        if updated:
            reload_asterisk_engine()
        return {"success": updated}, 200 if updated else 404

    @app.route("/api/asterisk/sda/<int:range_id>", methods=["DELETE"])
    def api_sda_range_delete(range_id: int):
        """Supprime une plage SDA."""
        deleted = delete_sda_range(range_id)
        if deleted:
            reload_asterisk_engine()
            insert_audit_event(
                action="sda_range_delete",
                user=_current_user(),
                ip=request.remote_addr,
                user_agent=request.headers.get("User-Agent"),
                meta={"range_id": range_id},
            )
        return {"success": deleted}, 200 if deleted else 404

    @app.route("/api/asterisk/classify", methods=["POST"])
    def api_asterisk_classify():
        """Classifie un ou plusieurs numéros."""
        data = request.get_json(silent=True) or {}
        numeros = data.get("numeros", [])
        if isinstance(numeros, str):
            numeros = [numeros]
        if not numeros:
            numero = data.get("numero", "")
            if numero:
                numeros = [numero]

        if not numeros:
            return {"error": "Fournir 'numero' ou 'numeros'"}, 400

        engine = get_asterisk_engine()
        from src.core.analyzer import normalize_number
        results = []
        for n in numeros:
            normalise = normalize_number(n)
            num_type, num_label = engine.classify_number(normalise)
            results.append({
                "numero_original": n,
                "numero_normalise": normalise,
                "type": num_type,
                "label": num_label,
            })
        return jsonify({"results": results})

    @app.route("/api/asterisk/types", methods=["GET"])
    def api_asterisk_types():
        """Retourne les types de numéros disponibles."""
        return jsonify(NUMBER_TYPE_LABELS)

    @app.route("/api/asterisk/stats/<report_id>", methods=["GET"])
    def api_asterisk_report_stats(report_id: str):
        """Calcule les stats SDA/Téléphone pour un rapport existant."""
        report = get_report_by_id(report_id)
        if not report:
            return {"error": "Rapport non trouvé"}, 404

        entries = report.get("fax_entries", report.get("entries", []))
        engine = get_asterisk_engine()
        entries = engine.classify_entries(entries)
        stats = engine.get_stats(entries)
        return jsonify({"report_id": report_id, "asterisk_stats": stats})

    # ──────────────────────────────────────────
    # API Détection de tonalité fax
    # ──────────────────────────────────────────

    @app.route("/api/asterisk/detect", methods=["POST"])
    def api_asterisk_detect():
        """
        Appelle un ou plusieurs numéros pour détecter la tonalité fax.
        Body: { "numero": "0493095562" } ou { "numeros": ["049...", "049..."] }
        Param: ?force=1 pour ignorer le cache
        """
        data = request.get_json(silent=True) or {}
        force = request.args.get("force", "0") == "1"

        numeros = data.get("numeros", [])
        if isinstance(numeros, str):
            numeros = [numeros]
        if not numeros:
            numero = data.get("numero", "")
            if numero:
                numeros = [numero]
        if not numeros:
            return {"error": "Fournir 'numero' ou 'numeros'"}, 400

        engine = get_asterisk_engine()
        from src.core.analyzer import normalize_number

        if len(numeros) == 1:
            normalise = normalize_number(numeros[0])
            result = engine.detect_tone(normalise, force=force)
            result["numero_original"] = numeros[0]
            return jsonify(result)

        # Batch : limiter à 50 numéros par requête
        if len(numeros) > 50:
            return {"error": "Maximum 50 numéros par requête"}, 400

        normalises = [normalize_number(n) for n in numeros]
        results = engine.detect_tones_batch(normalises, force=force)
        for i, r in enumerate(results):
            r["numero_original"] = numeros[i] if i < len(numeros) else ""
        return jsonify({"results": results, "count": len(results)})

    @app.route("/api/asterisk/detect/<numero>", methods=["GET"])
    def api_asterisk_detect_single(numero: str):
        """Détecte la tonalité fax pour un numéro donné (GET)."""
        force = request.args.get("force", "0") == "1"
        engine = get_asterisk_engine()
        from src.core.analyzer import normalize_number
        normalise = normalize_number(numero)
        result = engine.detect_tone(normalise, force=force)
        result["numero_original"] = numero
        return jsonify(result)

    @app.route("/api/asterisk/cache", methods=["GET"])
    def api_asterisk_cache():
        """Liste tous les résultats de détection en cache."""
        results = get_all_cached_tones()
        return jsonify({"cache": results, "count": len(results)})

    @app.route("/api/asterisk/cache", methods=["DELETE"])
    def api_asterisk_cache_clear():
        """Vide le cache de détection (un numéro ou tout)."""
        numero = request.args.get("numero")
        count = clear_tone_cache(numero)
        return {"success": True, "cleared": count}

    @app.route("/api/asterisk/dialplan", methods=["GET"])
    def api_asterisk_dialplan():
        """Retourne le snippet de dialplan Asterisk à configurer."""
        return Response(get_dialplan_snippet(), mimetype="text/plain")

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

    @app.route("/api/upload/<upload_id>", methods=["GET"])
    def api_upload_status(upload_id: str):
        job = _get_job(upload_id)
        if not job:
            return {"success": False, "done": True, "error": "Upload inconnu"}, 404

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

        if payload["done"]:
            _set_job(upload_id, expires_at=time.time() + 60)
            _prune_jobs()

        return jsonify(payload)

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
        enable_detection = request.form.get("enable_detection", "false").lower() == "true"
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
                analysis = analyze_data(rows, contract_id, date_debut, date_fin, enable_asterisk_detection=enable_detection)

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
        enable_detection = request.form.get("enable_detection", "false").lower() == "true"

        rows = import_faxcloud_export(str(filepath))
        analysis = analyze_data(rows, contract_id, date_debut, date_fin, enable_asterisk_detection=enable_detection)
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
