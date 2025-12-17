from __future__ import annotations

import logging
from pathlib import Path

from flask import Flask, abort, jsonify, send_from_directory

from src.core import get_all_reports, get_report_by_id, init_database, settings
from src.core.config import ensure_directories

logger = logging.getLogger(__name__)


def create_app() -> Flask:
    ensure_directories()
    init_database()

    static_dir = settings.base_dir / "web"
    app = Flask(
        __name__,
        static_folder=str(static_dir),
        static_url_path="",
    )

    @app.route("/health")
    def health() -> tuple[dict, int]:
        return {"status": "ok"}, 200

    @app.route("/reports")
    def list_reports() -> tuple[list[dict], int]:
        reports = get_all_reports()
        return reports, 200

    @app.route("/reports/<report_id>")
    def get_report(report_id: str):
        report = get_report_by_id(report_id)
        if not report:
            abort(404, description="Report not found")
        return jsonify(report)

    @app.route("/")
    def index():
        return send_from_directory(static_dir, "index.html")

    @app.route("/<path:path>")
    def static_files(path: str):
        target = static_dir / path
        if target.exists():
            return send_from_directory(static_dir, path)
        abort(404)

    return app
