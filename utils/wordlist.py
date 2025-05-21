#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module de gestion des wordlists pour GhostCrack
"""

import os
import logging
from typing import List, Optional

def load_wordlist(path: str, encoding: str = 'utf-8', 
                 skip_comments: bool = True, limit: Optional[int] = None) -> List[str]:
    """
    Charge une wordlist depuis un fichier
    
    Args:
        path: Chemin vers le fichier wordlist
        encoding: Encodage du fichier
        skip_comments: Ignorer les lignes commençant par # ou //
        limit: Limite le nombre de mots de passe à charger
        
    Returns:
        List[str]: Liste des mots de passe
    """
    logger = logging.getLogger(__name__)
    passwords = []
    
    # Vérification que le fichier existe
    if not os.path.exists(path):
        logger.error(f"Fichier wordlist introuvable: {path}")
        return []
    
    # Détection de l'extension pour déterminer si le fichier est compressé
    if path.endswith(('.gz', '.gzip')):
        import gzip
        open_func = gzip.open
    elif path.endswith('.bz2'):
        import bz2
        open_func = bz2.open
    elif path.endswith('.xz'):
        import lzma
        open_func = lzma.open
    else:
        open_func = open
    
    # Chargement des mots de passe
    try:
        with open_func(path, 'rt', encoding=encoding, errors='ignore') as f:
            for line in f:
                # Nettoyage de la ligne
                line = line.strip()
                
                # Ignorer les lignes vides
                if not line:
                    continue
                
                # Ignorer les commentaires si demandé
                if skip_comments and (line.startswith('#') or line.startswith('//')):
                    continue
                
                # Ajout du mot de passe
                passwords.append(line)
                
                # Arrêt si la limite est atteinte
                if limit and len(passwords) >= limit:
                    logger.info(f"Limite de {limit} mots de passe atteinte")
                    break
    
    except Exception as e:
        logger.error(f"Erreur lors du chargement de la wordlist: {e}")
        return []
    
    logger.info(f"Wordlist chargée: {len(passwords)} mots de passe")
    return passwords

def save_wordlist(passwords: List[str], path: str, encoding: str = 'utf-8') -> bool:
    """
    Sauvegarde une wordlist dans un fichier
    
    Args:
        passwords: Liste des mots de passe
        path: Chemin vers le fichier wordlist
        encoding: Encodage du fichier
        
    Returns:
        bool: True si la sauvegarde a réussi, False sinon
    """
    logger = logging.getLogger(__name__)
    
    # Détection de l'extension pour déterminer si le fichier doit être compressé
    if path.endswith(('.gz', '.gzip')):
        import gzip
        open_func = gzip.open
    elif path.endswith('.bz2'):
        import bz2
        open_func = bz2.open
    elif path.endswith('.xz'):
        import lzma
        open_func = lzma.open
    else:
        open_func = open
    
    # Sauvegarde des mots de passe
    try:
        with open_func(path, 'wt', encoding=encoding) as f:
            for password in passwords:
                f.write(f"{password}\n")
        
        logger.info(f"Wordlist sauvegardée: {len(passwords)} mots de passe")
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde de la wordlist: {e}")
        return False

def merge_wordlists(paths: List[str], output_path: str, 
                   remove_duplicates: bool = True, sort: bool = False) -> bool:
    """
    Fusionne plusieurs wordlists en une seule
    
    Args:
        paths: Liste des chemins vers les fichiers wordlist
        output_path: Chemin vers le fichier wordlist de sortie
        remove_duplicates: Supprimer les doublons
        sort: Trier les mots de passe
        
    Returns:
        bool: True si la fusion a réussi, False sinon
    """
    logger = logging.getLogger(__name__)
    all_passwords = []
    
    # Chargement de toutes les wordlists
    for path in paths:
        passwords = load_wordlist(path)
        all_passwords.extend(passwords)
    
    # Suppression des doublons si demandé
    if remove_duplicates:
        all_passwords = list(dict.fromkeys(all_passwords))
    
    # Tri si demandé
    if sort:
        all_passwords.sort()
    
    # Sauvegarde de la wordlist
    return save_wordlist(all_passwords, output_path)