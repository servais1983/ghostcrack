#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module d'export des résultats pour GhostCrack
"""

import json
import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional

def export_json(data: Dict[str, Any], path: Optional[str] = None) -> str:
    """
    Exporte les données au format JSON
    
    Args:
        data: Données à exporter
        path: Chemin du fichier de sortie (généré automatiquement si None)
        
    Returns:
        str: Chemin du fichier exporté
    """
    logger = logging.getLogger(__name__)
    
    # Génération du chemin si non spécifié
    if path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = f"ghostcrack_results_{timestamp}.json"
    
    # Création du répertoire si nécessaire
    output_dir = os.path.dirname(path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Ajout d'informations supplémentaires
    export_data = data.copy()
    export_data['timestamp'] = datetime.now().isoformat()
    export_data['tool'] = 'GhostCrack'
    
    # Export au format JSON
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        logger.info(f"Résultats exportés au format JSON: {path}")
        return path
    except Exception as e:
        logger.error(f"Erreur lors de l'export JSON: {e}")
        return ""

def export_pdf(data: Dict[str, Any], path: Optional[str] = None) -> str:
    """
    Exporte les données au format PDF
    
    Args:
        data: Données à exporter
        path: Chemin du fichier de sortie (généré automatiquement si None)
        
    Returns:
        str: Chemin du fichier exporté
    """
    logger = logging.getLogger(__name__)
    
    # Génération du chemin si non spécifié
    if path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = f"ghostcrack_results_{timestamp}.pdf"
    
    # Création du répertoire si nécessaire
    output_dir = os.path.dirname(path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    try:
        # Import de ReportLab (optionnel)
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.units import cm
            from reportlab.lib import colors
        except ImportError:
            logger.error("ReportLab n'est pas installé. Impossible de générer un PDF.")
            return ""
        
        # Création du PDF
        c = canvas.Canvas(path, pagesize=A4)
        width, height = A4
        
        # En-tête
        c.setFont("Helvetica-Bold", 16)
        c.drawString(2*cm, height - 2*cm, "GhostCrack - Rapport d'attaque")
        
        c.setFont("Helvetica", 12)
        c.drawString(2*cm, height - 3*cm, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Informations sur la cible
        c.setFont("Helvetica-Bold", 14)
        c.drawString(2*cm, height - 4*cm, "Informations sur la cible")
        
        c.setFont("Helvetica", 12)
        y = height - 4.5*cm
        
        # Cible
        c.drawString(2*cm, y, f"Cible: {data.get('target', 'N/A')}")
        y -= 0.5*cm
        
        # Protocole
        c.drawString(2*cm, y, f"Protocole: {data.get('protocol', 'N/A')}")
        y -= 0.5*cm
        
        # Nom d'utilisateur
        c.drawString(2*cm, y, f"Nom d'utilisateur: {data.get('username', 'N/A')}")
        y -= 0.5*cm
        
        # Résultat
        success = data.get('success', False)
        if success:
            c.setFillColor(colors.green)
            c.drawString(2*cm, y, f"Résultat: Succès - Mot de passe trouvé: {data.get('password', 'N/A')}")
        else:
            c.setFillColor(colors.red)
            c.drawString(2*cm, y, "Résultat: Échec - Aucun mot de passe trouvé")
        y -= 0.5*cm
        
        # Réinitialisation de la couleur
        c.setFillColor(colors.black)
        
        # Statistiques
        c.setFont("Helvetica-Bold", 14)
        c.drawString(2*cm, y - 0.5*cm, "Statistiques")
        
        c.setFont("Helvetica", 12)
        y -= 1.5*cm
        
        # Tentatives
        c.drawString(2*cm, y, f"Tentatives: {data.get('attempts', 0)}")
        y -= 0.5*cm
        
        # Temps écoulé
        elapsed_time = data.get('elapsed_time', 0)
        c.drawString(2*cm, y, f"Temps écoulé: {elapsed_time:.2f} secondes")
        y -= 0.5*cm
        
        # Si blocage détecté
        if data.get('blocked', False):
            c.setFillColor(colors.red)
            c.drawString(2*cm, y, "ATTENTION: Blocage détecté pendant l'attaque!")
            y -= 0.5*cm
            c.setFillColor(colors.black)
        
        # Erreurs
        errors = data.get('errors', [])
        if errors:
            c.setFont("Helvetica-Bold", 14)
            c.drawString(2*cm, y - 0.5*cm, "Erreurs")
            
            c.setFont("Helvetica", 10)
            y -= 1.5*cm
            
            for error in errors[:10]:  # Limite à 10 erreurs
                c.drawString(2*cm, y, f"- {error}")
                y -= 0.4*cm
                
            if len(errors) > 10:
                c.drawString(2*cm, y, f"... et {len(errors) - 10} autres erreurs")
        
        # Pied de page
        c.setFont("Helvetica-Oblique", 8)
        c.drawString(2*cm, 1*cm, "Ce rapport a été généré automatiquement par GhostCrack.")
        c.drawString(2*cm, 0.7*cm, "Utilisation éthique uniquement.")
        
        # Sauvegarde du PDF
        c.showPage()
        c.save()
        
        logger.info(f"Résultats exportés au format PDF: {path}")
        return path
        
    except Exception as e:
        logger.error(f"Erreur lors de l'export PDF: {e}")
        return ""