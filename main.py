"""
Point d'entrée principal - FaxCloud Analyzer
Orchestration du workflow complet
"""

import logging
import argparse
import sys
from pathlib import Path
from typing import Dict, Optional

# Ajouter src au chemin Python
sys.path.insert(0, str(Path(__file__).parent / "src" / "core"))

# Importer les modules
import config
import db
import importer
import analyzer
import reporter

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION LOGGING
# ═══════════════════════════════════════════════════════════════════════════

config.ensure_directories()
config.setup_logging()
logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════
# ORCHESTRATION
# ═══════════════════════════════════════════════════════════════════════════

def process_export(
    file_path: str,
    contract_id: str,
    date_debut: str,
    date_fin: str
) -> Dict:
    """
    Traite un export FaxCloud complet
    Importe → Analyse → Rapporte
    
    Args:
        file_path: Chemin du fichier à importer
        contract_id: ID du contrat
        date_debut: Date de début (YYYY-MM-DD)
        date_fin: Date de fin (YYYY-MM-DD)
    
    Returns:
        Résultat du traitement (success, rapport_id, etc.)
    """
    logger.info("=" * 70)
    logger.info(f"TRAITEMENT EXPORT: {contract_id} ({date_debut} à {date_fin})")
    logger.info("=" * 70)
    
    # Étape 1: Importer
    logger.info("\n📥 ÉTAPE 1: IMPORTATION")
    logger.info("-" * 70)
    
    import_result = importer.import_faxcloud_export(file_path)
    
    if not import_result["success"]:
        logger.error(f"✗ Erreur importation: {import_result['message']}")
        return {
            "success": False,
            "message": import_result["message"],
            "step": "import"
        }
    
    logger.info(f"✓ {import_result['message']}")
    
    # Étape 2: Analyser
    logger.info("\n📊 ÉTAPE 2: ANALYSE")
    logger.info("-" * 70)
    
    analysis = analyzer.analyze_data(
        import_result["rows"],
        contract_id,
        date_debut,
        date_fin
    )
    
    stats = analysis["statistics"]
    logger.info(f"✓ Analyse complète:")
    logger.info(f"  • Total FAX: {stats['total_fax']}")
    logger.info(f"  • Envoyés: {stats['fax_envoyes']}, Reçus: {stats['fax_recus']}")
    logger.info(f"  • Pages: {stats['pages_totales']}")
    logger.info(f"  • Erreurs: {stats['erreurs_totales']} ({100-stats['taux_reussite']:.2f}%)")
    logger.info(f"  • Taux réussite: {stats['taux_reussite']:.2f}%")
    
    # Étape 3: Rapporter
    logger.info("\n📝 ÉTAPE 3: RAPPORT ET QR CODE")
    logger.info("-" * 70)
    
    report = reporter.generate_report(analysis)
    
    if not report["success"]:
        logger.error(f"✗ Erreur génération rapport: {report['message']}")
        return {
            "success": False,
            "message": report["message"],
            "step": "reporter"
        }
    
    logger.info(f"✓ {report['message']}")
    logger.info(f"  • ID: {report['report_id']}")
    logger.info(f"  • URL: {report['report_url']}")
    if report['qr_path']:
        logger.info(f"  • QR Code: {report['qr_path']}")
    
    # Étape 4: Afficher le résumé
    logger.info("\n📋 RÉSUMÉ")
    logger.info("-" * 70)
    
    report_json = reporter.load_report_json(report['report_id'])
    if report_json:
        summary = reporter.generate_summary(report_json)
        logger.info(summary)
    
    logger.info("=" * 70)
    logger.info("✅ TRAITEMENT RÉUSSI")
    logger.info("=" * 70)
    
    return {
        "success": True,
        "message": "Traitement réussi",
        "report_id": report['report_id'],
        "report_url": report['report_url'],
        "qr_path": report['qr_path']
    }


# ═══════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════

def main():
    """Point d'entrée principal"""
    
    parser = argparse.ArgumentParser(
        description="FaxCloud Analyzer - Analyse automatique des exports FaxCloud"
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
        logger.info("🔧 Initialisation du projet...")
        config.ensure_directories()
        db.init_database()
        logger.info("✅ Projet initialisé avec succès")
        return
    
    # ─────────────────────────────────────────────────────────────────────
    # COMMANDE: import
    # ─────────────────────────────────────────────────────────────────────
    
    elif args.command == "import":
        if not args.file:
            logger.error("❌ --file requis pour la commande 'import'")
            return
        
        result = process_export(
            args.file,
            args.contract,
            args.start,
            args.end
        )
        
        if result["success"]:
            logger.info(f"\n✅ Rapport généré: {result['report_id']}")
        else:
            logger.error(f"\n❌ Erreur: {result['message']}")
        
        return result
    
    # ─────────────────────────────────────────────────────────────────────
    # COMMANDE: list
    # ─────────────────────────────────────────────────────────────────────
    
    elif args.command == "list":
        logger.info("📋 Liste des rapports")
        logger.info("-" * 70)
        
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
            return
        
        logger.info(f"📖 Affichage rapport: {args.report_id}")
        logger.info("-" * 70)
        
        report_json = reporter.load_report_json(args.report_id)
        
        if not report_json:
            logger.error(f"Rapport non trouvé: {args.report_id}")
            return
        
        summary = reporter.generate_summary(report_json)
        logger.info(summary)
        
        # Afficher aussi les entrées avec erreurs
        errors = [e for e in report_json['entries'] if not e['valide']]
        if errors:
            logger.info("\n⚠️  ENTRÉES AVEC ERREURS:\n")
            for entry in errors:
                logger.info(f"  • {entry['fax_id']} ({entry['utilisateur']})")
                logger.info(f"    Numéro: {entry['numero_original']}")
                logger.info(f"    Erreurs: {', '.join(entry['erreurs'])}\n")


# ═══════════════════════════════════════════════════════════════════════════
# EXPORTS POUR UTILISATION PROGRAMMÉE
# ═══════════════════════════════════════════════════════════════════════════

__all__ = [
    'process_export',
    'config',
    'db',
    'importer',
    'analyzer',
    'reporter'
]


# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    main()
