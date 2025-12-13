"""
Module pour générer des PDFs des rapports FAX
"""

import json
import logging
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

logger = logging.getLogger(__name__)


class PDFReportGenerator:
    """Génère un PDF à partir d'un rapport FAX"""
    
    @staticmethod
    def generate_pdf(report_data: dict) -> BytesIO:
        """
        Génère un PDF avec les infos du rapport
        
        Args:
            report_data: Dictionnaire contenant les données du rapport
        
        Returns:
            BytesIO contenant le PDF généré
        """
        try:
            # Créer un BytesIO pour stocker le PDF
            pdf_buffer = BytesIO()
            
            # Créer le document PDF
            doc = SimpleDocTemplate(
                pdf_buffer,
                pagesize=A4,
                rightMargin=0.5*inch,
                leftMargin=0.5*inch,
                topMargin=0.75*inch,
                bottomMargin=0.75*inch
            )
            
            # Éléments du document
            elements = []
            styles = getSampleStyleSheet()
            
            # Style personnalisé pour le titre
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1a3a52'),
                spaceAfter=30,
                alignment=TA_CENTER
            )
            
            # Style pour les sections
            section_style = ParagraphStyle(
                'SectionTitle',
                parent=styles['Heading2'],
                fontSize=14,
                textColor=colors.HexColor('#2d5a7b'),
                spaceAfter=12,
                spaceBefore=12,
                borderBottom=1,
                borderColor=colors.HexColor('#2d5a7b')
            )
            
            # Titre
            elements.append(Paragraph("RAPPORT D'ANALYSE FAX", title_style))
            elements.append(Spacer(1, 0.2*inch))
            
            # Info rapport
            report_id = report_data.get('id', 'N/A')
            analysis_name = report_data.get('analysis_name', 'Sans nom')
            date_analyse = report_data.get('date_analyse', 'N/A')
            
            info_data = [
                ['ID Rapport:', report_id],
                ['Nom de l\'analyse:', analysis_name],
                ['Date d\'analyse:', str(date_analyse)],
            ]
            
            info_table = Table(info_data, colWidths=[2*inch, 3.5*inch])
            info_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f0f5')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ]))
            
            elements.append(info_table)
            elements.append(Spacer(1, 0.3*inch))
            
            # Statistiques
            elements.append(Paragraph("STATISTIQUES GLOBALES", section_style))
            
            stats = report_data.get('stats', {})
            total_fax = stats.get('total_fax', 0)
            fax_envoyes = stats.get('fax_envoyes', 0)
            fax_recus = stats.get('fax_recus', 0)
            erreurs = stats.get('erreurs_totales', 0)
            taux_reussite = stats.get('taux_reussite', 0)
            
            stats_data = [
                ['Métrique', 'Valeur'],
                ['Total FAX', str(total_fax)],
                ['FAX Envoyés', str(fax_envoyes)],
                ['FAX Reçus', str(fax_recus)],
                ['Erreurs Totales', str(erreurs)],
                ['Taux de Réussite', f'{taux_reussite:.1f}%'],
            ]
            
            stats_table = Table(stats_data, colWidths=[2.5*inch, 2.5*inch])
            stats_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d5a7b')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('TOPPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0f5f9')),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
                ('TOPPADDING', (0, 1), (-1, -1), 6),
            ]))
            
            elements.append(stats_table)
            elements.append(Spacer(1, 0.3*inch))
            
            # Erreurs / FAX en erreur
            fax_data = report_data.get('fax_data', [])
            error_fax = [fax for fax in fax_data if fax.get('statut', '').lower() == 'erreur']
            
            if error_fax:
                elements.append(PageBreak())
                elements.append(Paragraph(f"FAX EN ERREUR (Total: {len(error_fax)})", section_style))
                
                # Tableau des erreurs
                error_table_data = [['Numéro', 'Pages', 'Détail Erreur', 'Date']]
                
                for fax in error_fax:
                    numero = fax.get('numero', 'N/A')
                    pages = str(fax.get('pages', 'N/A'))
                    detail = fax.get('detail_erreur', 'N/A')[:50]  # Limiter à 50 caractères
                    date_envoi = fax.get('date_envoi', 'N/A')
                    
                    error_table_data.append([
                        numero,
                        pages,
                        detail,
                        str(date_envoi)
                    ])
                
                error_table = Table(error_table_data, colWidths=[1.5*inch, 0.8*inch, 2*inch, 1.2*inch])
                error_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#d9534f')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                    ('TOPPADDING', (0, 0), (-1, 0), 6),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#fef5f5')),
                    ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                    ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
                    ('TOPPADDING', (0, 1), (-1, -1), 4),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ]))
                
                elements.append(error_table)
            
            # Footer
            elements.append(Spacer(1, 0.5*inch))
            footer_text = f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}"
            footer_style = ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=8,
                textColor=colors.grey,
                alignment=TA_CENTER
            )
            elements.append(Paragraph(footer_text, footer_style))
            
            # Construire le PDF
            doc.build(elements)
            
            # Retourner le buffer avec le pointeur au début
            pdf_buffer.seek(0)
            return pdf_buffer
        
        except Exception as e:
            logger.error(f"Erreur lors de la génération du PDF: {str(e)}", exc_info=True)
            return None
