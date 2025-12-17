#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FaxCloud Analyzer - Point d'entrée principal
Orchestration du workflow complet: Import → Analyse → Rapport
"""

import sys
import logging
import argparse
from pathlib import Path

# Ajouter src au chemin Python
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.config import Config
from core.importer import FileImporter
from core.analyzer import FaxAnalyzer
from core.reporter import ReportGenerator
from core.db import Database

# ═══════════════════════════════════════════════════════════════════════════
# INITIALISATION
# ═══════════════════════════════════════════════════════════════════════════

Config.ensure_directories()
Config.setup_logging()
logger = Config.get_logger(__name__)

# ═══════════════════════════════════════════════════════════════════════════
# FONCTIONS PRINCIPALES
# ═══════════════════════════════════════════════════════════════════════════

def process_export(
    file_path: str,
    contract_id: str = None,
    date_debut: str = None,
    date_fin: str = None
) -> dict:
    """
    Traite un export FaxCloud complet
    PHASE 1: Import → PHASE 2: Analyse → PHASE 3: Rapport
    
    Args:
        file_path: Chemin du fichier CSV/XLSX
        contract_id: ID du contrat (optionnel)
        date_debut: Date de début YYYY-MM-DD (optionnel)
        date_fin: Date de fin YYYY-MM-DD (optionnel)
    
    Returns:
        dict: {success, report_id, message, ...}
    """
    try:
        logger.info("=" * 70)
        logger.info(f"TRAITEMENT EXPORT: {contract_id} ({date_debut} à {date_fin})")
        logger.info("=" * 70)
        
        # ─────────────────────────────────────────────────────────────────
        # ÉTAPE 1: IMPORTATION
        # ─────────────────────────────────────────────────────────────────
        
        logger.info("\n📥 ÉTAPE 1: IMPORTATION")
        logger.info("-" * 70)

        importer = FileImporter()
        import_result = importer.import_file(file_path)

        if not import_result.get("success"):
            message = ", ".join(import_result.get("errors", [])) or "Importation impossible"
            logger.error(f"✗ Erreur d'import: {message}")
            return {
                "success": False,
                "message": message,
                "step": "import"
            }

        rows = import_result.get("data", [])
        metadata = import_result.get("metadata", {})
        file_size_kb = Path(file_path).stat().st_size / 1024 if Path(file_path).exists() else 0

        logger.info(f"✓ Fichier importé: {metadata.get('file', Path(file_path).name)}")
        logger.info(f"  • Format: {metadata.get('format', 'inconnu')}")
        logger.info(f"  • Lignes: {metadata.get('rows', len(rows))}")
        logger.info(f"  • Taille: {file_size_kb:.2f} KB")
        
        # ─────────────────────────────────────────────────────────────────
        # ÉTAPE 2: ANALYSE
        # ─────────────────────────────────────────────────────────────────
        
        logger.info("\n📊 ÉTAPE 2: ANALYSE")
        logger.info("-" * 70)
        
        analyzer = FaxAnalyzer()
        analysis = analyzer.analyze_data(
            rows,
            contract_id,
            date_debut,
            date_fin
        )
        analysis["fichier_source"] = metadata.get("file", Path(file_path).name)
        analysis["metadata"] = metadata

        stats = analysis['statistics']
        logger.info(f"✓ Analyse complète:")
        logger.info(f"  • Total FAX: {stats['total_fax']}")
        logger.info(f"  • Envoyés: {stats['fax_envoyes']}, Reçus: {stats['fax_recus']}")
        logger.info(f"  • Pages: {stats['pages_totales']}")
        logger.info(f"  • Erreurs: {stats['erreurs_totales']}")
        logger.info(f"  • Taux réussite: {stats['taux_reussite']:.2f}%")
        
        # ─────────────────────────────────────────────────────────────────
        # ÉTAPE 3: RAPPORT ET QR CODE
        # ─────────────────────────────────────────────────────────────────
        
        logger.info("\n📝 ÉTAPE 3: RAPPORT ET QR CODE")
        logger.info("-" * 70)
        
        db = Database()
        reporter = ReportGenerator(db=db)
        
        report = reporter.generate_report(analysis)
        
        if not report['success']:
            logger.error(f"✗ Erreur génération rapport: {report['message']}")
            return {
                "success": False,
                "message": report['message'],
                "step": "reporter"
            }
        
        logger.info(f"✓ {report['message']}")
        logger.info(f"  • ID: {report['rapport_id']}")
        logger.info(f"  • URL: {report['report_url']}")
        if report['qr_path']:
            logger.info(f"  • QR Code: {report['qr_path']}")
        
        # ─────────────────────────────────────────────────────────────────
        # ÉTAPE 4: AFFICHER LE RÉSUMÉ
        # ─────────────────────────────────────────────────────────────────
        
        logger.info("\n📋 RÉSUMÉ")
        logger.info("-" * 70)
        
        report_json = reporter.load_report_json(report['rapport_id'])
        if report_json:
            summary = reporter.generate_summary(report_json)
            logger.info(summary)
        
        logger.info("=" * 70)
        logger.info("✅ TRAITEMENT RÉUSSI")
        logger.info("=" * 70)
        
        return {
            "success": True,
            "message": "Traitement réussi",
            "rapport_id": report['rapport_id'],
            "report_url": report['report_url'],
            "qr_path": report['qr_path']
        }
    
    except Exception as e:
        logger.error(f"❌ Erreur lors du traitement: {e}", exc_info=True)
        return {
            "success": False,
            "message": str(e),
            "error": str(e)
        }

# ═══════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════

def main():
    """Point d'entrée principal"""
    
    parser = argparse.ArgumentParser(
        description="FaxCloud Analyzer - Analyse automatique des exports FaxCloud",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  python main.py init
  python main.py import --file data.csv --contract "CLIENT_001" --start 2024-01-01 --end 2024-12-31
  python main.py list
  python main.py view --report-id <uuid>
        """
    )
    
    parser.add_argument(
        "command",
        choices=["import", "list", "view", "init"],
        help="Commande à exécuter"
    )
    
    parser.add_argument(
        "--file",
        help="Chemin du fichier à importer",
        default=None
    )
    
    parser.add_argument(
        "--contract",
        help="ID du contrat",
        default="CONTRACT_001"
    )
    
    parser.add_argument(
        "--start",
        help="Date de début (YYYY-MM-DD)",
        default="2024-01-01"
    )
    
    parser.add_argument(
        "--end",
        help="Date de fin (YYYY-MM-DD)",
        default="2024-12-31"
    )
    
    parser.add_argument(
        "--report-id",
        help="ID du rapport à consulter",
        default=None
    )
    
    args = parser.parse_args()
    
    # ─────────────────────────────────────────────────────────────────────
    # COMMANDE: init
    # ─────────────────────────────────────────────────────────────────────
    
    if args.command == "init":
        logger.info("Initialisation du projet...")
        try:
            Config.ensure_directories()
            db = Database()
            db.initialize()
            logger.info("✅ Projet initialisé avec succès")
            logger.info(f"   Base de données: {Config.DATABASE_CONFIG['path']}")
        except Exception as e:
            logger.error(f"❌ Erreur initialisation: {e}")
            sys.exit(1)
        return
    
    # ─────────────────────────────────────────────────────────────────────
    # COMMANDE: import
    # ─────────────────────────────────────────────────────────────────────
    
    elif args.command == "import":
        if not args.file:
            logger.error("❌ --file requis pour la commande 'import'")
            sys.exit(1)
        
        result = process_export(
            args.file,
            args.contract,
            args.start,
            args.end
        )
        
        if result["success"]:
            logger.info(f"\n✅ Rapport généré: {result['rapport_id']}")
            sys.exit(0)
        else:
            logger.error(f"\n❌ Erreur: {result['message']}")
            sys.exit(1)
    
    # ─────────────────────────────────────────────────────────────────────
    # COMMANDE: list
    # ─────────────────────────────────────────────────────────────────────
    
    elif args.command == "list":
        logger.info("📋 Liste des rapports")
        logger.info("-" * 70)
        
        reporter = ReportGenerator()
        reports = reporter.list_reports()
        
        if not reports:
            logger.info("Aucun rapport trouvé")
        else:
            logger.info(f"Total: {len(reports)} rapport(s)\n")
            
            for idx, report in enumerate(reports, 1):
                logger.info(f"{idx}. {report['id']}")
                logger.info(f"   Contrat: {report['contract_id']}")
                logger.info(f"   Généré: {report['timestamp']}")
                logger.info(f"   FAX: {report['total_fax']} "
                           f"(Erreurs: {report['erreurs']}, "
                           f"Réussite: {report['taux_reussite']:.1f}%)")
                logger.info("")
    
    # ─────────────────────────────────────────────────────────────────────
    # COMMANDE: view
    # ─────────────────────────────────────────────────────────────────────
    
    elif args.command == "view":
        if not args.report_id:
            logger.error("❌ --report-id requis pour la commande 'view'")
            sys.exit(1)
        
        logger.info(f"📖 Affichage rapport: {args.report_id}")
        logger.info("-" * 70)
        
        reporter = ReportGenerator()
        report_json = reporter.load_report_json(args.report_id)
        
        if not report_json:
            logger.error(f"Rapport non trouvé: {args.report_id}")
            sys.exit(1)
        
        summary = reporter.generate_summary(report_json)
        logger.info(summary)
        
        # Afficher aussi les entrées avec erreurs
        errors = [e for e in report_json['entries'] if not e['valide']]
        if errors:
            logger.info("\n⚠️  ENTRÉES AVEC ERREURS:\n")
            for entry in errors[:20]:  # Limiter à 20 pour la lisibilité
                logger.info(f"  • {entry['fax_id']} ({entry['utilisateur']})")
                logger.info(f"    Numéro: {entry['numero_original']}")
                logger.info(f"    Erreurs: {', '.join(entry['erreurs'])}\n")
            
            if len(errors) > 20:
                logger.info(f"  ... et {len(errors) - 20} autres erreurs")

# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    main()
