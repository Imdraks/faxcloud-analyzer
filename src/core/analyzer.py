"""
Module d'analyse et validation des données FAX
Applique les règles métier et détecte les erreurs
"""

import logging
import re
from typing import Dict, List, Tuple, Any
from datetime import datetime
import pandas as pd

from .config import Config

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════
# CLASSE FAX ANALYZER
# ═══════════════════════════════════════════════════════════════════════════

class FaxAnalyzer:
    """Analyseur de données FAX avec validation complète"""
    
    def __init__(self):
        """Initialise l'analyseur"""
        self.validation_rules = Config.NUMBER_VALIDATION_RULES
        self.valid_modes = Config.VALID_FAX_MODES
        self.error_types = Config.ERROR_TYPES
    
    # ═════════════════════════════════════════════════════════════════════
    # VALIDATION DES NUMÉROS
    # ═════════════════════════════════════════════════════════════════════
    
    @staticmethod
    def normalize_number(raw_number: str) -> str:
        """
        Normalise un numéro téléphonique
        - Supprime tous les caractères non numériques
        - Convertit 0033XXXXXXXXX → 33XXXXXXXXX
        - Convertit 0XXXXXXXXXX → 33XXXXXXXXXX
        """
        # Supprimer tous les caractères non-numériques
        cleaned = re.sub(r'\D', '', raw_number)
        
        if not cleaned:
            return ''
        
        # Convertir 0033XXXXXXXXX → 33XXXXXXXXX
        if cleaned.startswith('0033'):
            cleaned = cleaned[2:]
        
        # Convertir 0XXXXXXXXXX → 33XXXXXXXXXX
        elif cleaned.startswith('0'):
            cleaned = '33' + cleaned[1:]
        
        return cleaned
    
    def validate_number(self, raw_number: str) -> Tuple[bool, str, List[str]]:
        """
        Valide un numéro selon les règles métier
        Retourne: (est_valide, numéro_normalisé, liste_erreurs)
        """
        errors = []
        
        # Règle 1: Vérifier que le numéro n'est pas vide
        if not raw_number or not str(raw_number).strip():
            errors.append('ERR_001')  # Numéro vide
            return False, '', errors
        
        # Normaliser le numéro
        normalized = self.normalize_number(raw_number)
        
        # Règle 2: Vérifier que après normalisation, c'est bien numérique
        if not normalized.isdigit():
            errors.append('ERR_002')  # Format illisible
            return False, '', errors
        
        # Règle 3: Vérifier la longueur exacte (11 chiffres)
        min_len = self.validation_rules['min_length']
        max_len = self.validation_rules['max_length']
        
        if len(normalized) != min_len:
            errors.append('ERR_003')  # Nombre de chiffres incorrect
            return False, normalized, errors
        
        # Règle 4: Vérifier l'indicatif (doit commencer par 33)
        required_prefix = self.validation_rules['required_prefix']
        if not normalized.startswith(required_prefix):
            errors.append('ERR_004')  # Indicatif incorrect
            return False, normalized, errors
        
        # ✅ Numéro valide
        return True, normalized, errors
    
    # ═════════════════════════════════════════════════════════════════════
    # VALIDATION DES AUTRES CHAMPS
    # ═════════════════════════════════════════════════════════════════════
    
    def validate_mode(self, mode: str) -> Tuple[bool, List[str]]:
        """Valide le mode de fax (SF ou RF)"""
        errors = []
        
        if not mode or mode not in self.valid_modes:
            errors.append('ERR_006')  # Mode invalide
            return False, errors
        
        return True, errors
    
    def validate_pages(self, pages_str: str) -> Tuple[bool, int, List[str]]:
        """Valide le nombre de pages"""
        errors = []
        pages = 0
        
        try:
            pages = int(pages_str)
            
            if pages < 1:
                errors.append('ERR_005')  # Nombre de pages invalide
                return False, pages, errors
            
            return True, pages, errors
        
        except (ValueError, TypeError):
            errors.append('ERR_005')  # Nombre de pages invalide
            return False, 0, errors
    
    def validate_date(self, date_str: str) -> Tuple[bool, str, List[str]]:
        """Valide une date/heure"""
        errors = []
        
        if not date_str or not str(date_str).strip():
            errors.append('ERR_007')  # Date manquante
            return False, '', errors
        
        # Essayer plusieurs formats courants
        formats = [
            '%d/%m/%Y %H:%M:%S',
            '%d/%m/%Y %H:%M',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d %H:%M',
            '%d/%m/%Y',
            '%Y-%m-%d'
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(str(date_str).strip(), fmt)
                return True, dt.isoformat(), errors
            except ValueError:
                continue
        
        # Si aucun format ne marche
        errors.append('ERR_007')  # Date invalide
        return False, '', errors
    
    def validate_utilisateur(self, utilisateur: str) -> Tuple[bool, List[str]]:
        """Valide que l'utilisateur est renseigné"""
        errors = []
        
        if not utilisateur or not str(utilisateur).strip():
            errors.append('ERR_008')  # Utilisateur non renseigné
            return False, errors
        
        return True, errors
    
    # ═════════════════════════════════════════════════════════════════════
    # ANALYSE COMPLÈTE D'UNE ENTRÉE
    # ═════════════════════════════════════════════════════════════════════
    
    def analyze_entry(self, entry: Dict[str, str]) -> Dict[str, Any]:
        """
        Analyse une entrée complète
        Retourne un dictionnaire avec tous les détails
        """
        errors = []
        
        # Extraire les données (convertir en string d'abord)
        fax_id = str(entry.get('fax_id', '')).strip()
        utilisateur = str(entry.get('utilisateur', '')).strip()
        mode = str(entry.get('mode', '')).strip()
        date_heure = str(entry.get('date_heure', '')).strip()
        numero_raw = str(entry.get('numero', '')).strip()
        pages_str = str(entry.get('pages', '')).strip()
        
        # Valider utilisateur
        user_valid, user_errors = self.validate_utilisateur(utilisateur)
        errors.extend(user_errors)
        
        # Valider mode
        mode_valid, mode_errors = self.validate_mode(mode)
        errors.extend(mode_errors)
        
        # Valider date
        date_valid, date_iso, date_errors = self.validate_date(date_heure)
        errors.extend(date_errors)
        
        # Valider numéro
        num_valid, num_normalized, num_errors = self.validate_number(numero_raw)
        errors.extend(num_errors)
        
        # Valider pages
        pages_valid, pages_int, pages_errors = self.validate_pages(pages_str)
        errors.extend(pages_errors)
        
        # Déterminer si l'entrée est valide
        is_valid = all([
            user_valid,
            mode_valid,
            date_valid,
            num_valid,
            pages_valid
        ])
        
        # Construire le résultat
        result = {
            'fax_id': fax_id,
            'utilisateur': utilisateur,
            'mode': mode,
            'date_heure': date_iso if date_valid else date_heure,
            'numero_original': numero_raw,
            'numero_normalise': num_normalized,
            'pages': pages_int if pages_valid else 0,
            'valide': is_valid,
            'erreurs': [Config.ERROR_TYPES.get(e, e) for e in errors]
        }
        
        return result
    
    # ═════════════════════════════════════════════════════════════════════
    # ANALYSE GLOBALE
    # ═════════════════════════════════════════════════════════════════════
    
    def analyze_data(
        self,
        entries: List[Dict[str, str]],
        contract_id: str,
        date_debut: str,
        date_fin: str
    ) -> Dict[str, Any]:
        """
        Analyse l'ensemble des données
        Retourne un rapport complet avec statistiques
        """
        analyzed_entries = []
        stats = {
            'total_fax': 0,
            'fax_envoyes': 0,
            'fax_recus': 0,
            'pages_totales': 0,
            'pages_envoyees': 0,
            'pages_recues': 0,
            'erreurs_totales': 0,
            'taux_reussite': 0.0
        }
        
        utilisateurs_stats = {}  # Statistiques par utilisateur
        
        # Analyser chaque entrée
        for entry in entries:
            analyzed = self.analyze_entry(entry)
            analyzed_entries.append(analyzed)
            
            # Mettre à jour les statistiques
            stats['total_fax'] += 1
            
            if analyzed['valide']:
                # Compter par mode
                if analyzed['mode'] == 'SF':
                    stats['fax_envoyes'] += 1
                    stats['pages_envoyees'] += analyzed['pages']
                elif analyzed['mode'] == 'RF':
                    stats['fax_recus'] += 1
                    stats['pages_recues'] += analyzed['pages']
                
                stats['pages_totales'] += analyzed['pages']
            else:
                stats['erreurs_totales'] += len(analyzed['erreurs'])
            
            # Statistiques par utilisateur
            user = analyzed['utilisateur']
            if user not in utilisateurs_stats:
                utilisateurs_stats[user] = {
                    'total': 0,
                    'valides': 0,
                    'erreurs': 0
                }
            utilisateurs_stats[user]['total'] += 1
            if analyzed['valide']:
                utilisateurs_stats[user]['valides'] += 1
            else:
                utilisateurs_stats[user]['erreurs'] += len(analyzed['erreurs'])
        
        # Calculer le taux de réussite
        if stats['total_fax'] > 0:
            stats['taux_reussite'] = (
                (stats['total_fax'] - (stats['erreurs_totales'] / max(1, stats['total_fax']))) / stats['total_fax'] * 100
            )
            # Meilleure formule: nombre d'entrées sans erreur
            valides = sum(1 for e in analyzed_entries if e['valide'])
            stats['taux_reussite'] = (valides / stats['total_fax'] * 100) if stats['total_fax'] > 0 else 0
        
        # Construire le rapport
        rapport = {
            'contract_id': contract_id,
            'date_debut': date_debut,
            'date_fin': date_fin,
            'statistics': stats,
            'entries': analyzed_entries,
            'utilisateurs_stats': utilisateurs_stats,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(
            f"Analyse complète: {stats['total_fax']} FAX, "
            f"{stats['fax_envoyes']} envoyés, {stats['fax_recus']} reçus, "
            f"{stats['erreurs_totales']} erreurs, "
            f"{stats['taux_reussite']:.2f}% réussite"
        )
        
        return rapport
