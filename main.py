from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

from src.core import (
    analyze_data,
    generate_report,
    get_all_reports,
    get_report_by_id,
    import_faxcloud_export,
    init_database,
    insert_report_to_db,
    list_report_files,
)
from src.core.config import configure_logging, ensure_directories
from src.server import create_app


def cmd_init(args: argparse.Namespace) -> None:
    ensure_directories()
    init_database()
    print("✓ Répertoires et base de données initialisés")


def cmd_import(args: argparse.Namespace) -> None:
    ensure_directories()
    init_database()
    rows = import_faxcloud_export(args.file)
    analysis = analyze_data(rows, args.contract, args.start, args.end)
    report = generate_report(analysis, include_qr=not args.no_qr)
    insert_report_to_db(report["report_id"], report, report.get("qr_path"))
    print(f"✓ Rapport généré: {report['report_id']}")


def cmd_list(args: argparse.Namespace) -> None:
    init_database()
    reports = get_all_reports()
    if not reports:
        print("Aucun rapport en base.")
        return
    for rpt in reports:
        print(
            f"{rpt['id']} | contrat={rpt['contract_id']} "
            f"période={rpt['date_debut']}->{rpt['date_fin']} "
            f"fax={rpt['total_fax']} erreurs={rpt['erreurs_totales']} "
            f"taux={rpt['taux_reussite']}%"
        )


def cmd_view(args: argparse.Namespace) -> None:
    report_id = args.report_id
    path = Path(report_id)
    if path.exists():
        print(path.read_text(encoding="utf-8"))
        return

    data = get_report_by_id(report_id)
    if not data:
        print(f"Rapport introuvable: {report_id}")
        return
    print(json.dumps(data, indent=2, ensure_ascii=False))


def cmd_reports_dir(args: argparse.Namespace) -> None:
    for path in list_report_files():
        print(path)


def cmd_serve(args: argparse.Namespace) -> None:
    app = create_app()
    host = args.host
    port = args.port
    app.run(host=host, port=port)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="FaxCloud Analyzer CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="Initialiser la base et les répertoires")
    p_init.set_defaults(func=cmd_init)

    p_import = sub.add_parser("import", help="Importer un fichier CSV/XLSX")
    p_import.add_argument("--file", required=True, help="Chemin du fichier à importer")
    p_import.add_argument("--contract", default=None, help="Identifiant contrat")
    p_import.add_argument("--start", dest="start", default=None, help="Date début (YYYY-MM-DD)")
    p_import.add_argument("--end", dest="end", default=None, help="Date fin (YYYY-MM-DD)")
    p_import.add_argument("--no-qr", action="store_true", help="Ne pas générer de QR code")
    p_import.set_defaults(func=cmd_import)

    p_list = sub.add_parser("list", help="Lister les rapports en base")
    p_list.set_defaults(func=cmd_list)

    p_view = sub.add_parser("view", help="Afficher un rapport (fichier ou base)")
    p_view.add_argument("--report-id", required=True, help="UUID de rapport ou chemin JSON")
    p_view.set_defaults(func=cmd_view)

    p_reports_dir = sub.add_parser("reports-dir", help="Lister les fichiers rapport JSON")
    p_reports_dir.set_defaults(func=cmd_reports_dir)

    p_serve = sub.add_parser("serve", help="Lancer le serveur web (Flask) pour consulter les rapports")
    p_serve.add_argument("--host", default="0.0.0.0", help="Adresse d'écoute (défaut: 0.0.0.0)")
    p_serve.add_argument("--port", type=int, default=5000, help="Port HTTP (défaut: 5000)")
    p_serve.set_defaults(func=cmd_serve)

    return parser


def main() -> None:
    configure_logging(logging.INFO)
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
