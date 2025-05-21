#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module de génération de mots de passe pour GhostCrack
"""

import itertools
import re
import logging
import random
from typing import List, Dict, Any, Optional, Callable, Generator, Set, Tuple
from datetime import datetime

def generate_combinations(base: str, patterns: Optional[List[str]] = None) -> List[str]:
    """
    Génère des combinaisons de mots de passe basées sur un mot de base
    
    Args:
        base: Mot de base
        patterns: Liste de suffixes (par défaut: ["123", "!", "2025"])
        
    Returns:
        List[str]: Liste des combinaisons générées
    """
    logger = logging.getLogger(__name__)
    
    # Patterns par défaut
    if patterns is None:
        patterns = ["123", "!", "2025"]
    
    # Liste pour stocker les combinaisons
    combos = []
    
    # Ajout des suffixes
    for suffix in patterns:
        combos.append(base + suffix)
        combos.append(base.capitalize() + suffix)
    
    # Ajout des préfixes
    for prefix in patterns:
        combos.append(prefix + base)
        combos.append(prefix + base.capitalize())
    
    # Substitutions courantes (leet speak)
    leet_map = {
        'a': ['4', '@'],
        'e': ['3'],
        'i': ['1', '!'],
        'o': ['0'],
        's': ['5', '$'],
        't': ['7', '+']
    }
    
    # Application des substitutions leet
    leet_combos = []
    for combo in combos:
        # On limite le nombre de substitutions possibles
        for char, replacements in leet_map.items():
            if char in combo.lower():
                for replacement in replacements:
                    leet_combos.append(combo.lower().replace(char, replacement))
    
    # Ajout des combinaisons leet
    combos.extend(leet_combos)
    
    # Inversion et ajout d'années
    current_year = datetime.now().year
    years = [str(y) for y in range(current_year - 5, current_year + 2)]
    
    year_combos = []
    for year in years:
        year_combos.append(base + year)
        year_combos.append(year + base)
    
    # Ajout des combinaisons avec années
    combos.extend(year_combos)
    
    # Suppression des doublons
    combos = list(dict.fromkeys(combos))
    
    logger.debug(f"Généré {len(combos)} combinaisons à partir de '{base}'")
    return combos

def generate_mutations(base: str) -> List[str]:
    """
    Génère des mutations basées sur un mot de base
    
    Args:
        base: Mot de base
        
    Returns:
        List[str]: Liste des mutations générées
    """
    logger = logging.getLogger(__name__)
    mutations = []
    
    # Conversions de casse
    mutations.append(base.lower())
    mutations.append(base.upper())
    mutations.append(base.capitalize())
    mutations.append(base.title())
    
    # Inversion
    mutations.append(base[::-1])
    
    # Double
    mutations.append(base + base)
    
    # Substitutions courantes
    substitutions = {
        'a': ['4', '@'],
        'e': ['3'],
        'i': ['1', '!'],
        'o': ['0'],
        's': ['5', '$'],
        't': ['7', '+'],
        'b': ['8'],
        'g': ['9'],
        'l': ['1', '|'],
        'z': ['2']
    }
    
    # Génération de toutes les combinaisons de substitutions
    chars = []
    options = []
    
    # Pour chaque caractère dans le mot de base
    for char in base.lower():
        if char in substitutions:
            # Options pour ce caractère: lui-même et ses substitutions
            char_options = [char] + substitutions[char]
            options.append(char_options)
        else:
            # Juste le caractère original
            options.append([char])
    
    # Génération des combinaisons
    # Limitée à max 100 combinaisons pour éviter l'explosion combinatoire
    max_combinations = 100
    combinations = list(itertools.product(*options))[:max_combinations]
    
    # Conversion des tuples en chaînes
    for combo in combinations:
        mutations.append(''.join(combo))
    
    # Suppression des doublons
    mutations = list(dict.fromkeys(mutations))
    
    logger.debug(f"Généré {len(mutations)} mutations à partir de '{base}'")
    return mutations

def generate_common_patterns(company: Optional[str] = None, username: Optional[str] = None) -> List[str]:
    """
    Génère des mots de passe basés sur des modèles courants
    
    Args:
        company: Nom de l'entreprise (optionnel)
        username: Nom d'utilisateur (optionnel)
        
    Returns:
        List[str]: Liste des mots de passe générés
    """
    logger = logging.getLogger(__name__)
    passwords = []
    
    # Années courantes
    current_year = datetime.now().year
    years = [str(y) for y in range(current_year - 10, current_year + 2)]
    
    # Motifs courants
    patterns = [
        "password", "pass", "welcome", "admin", "user", "login",
        "changeme", "secret", "secure", "security", "letmein",
        "qwerty", "123456", "abc123"
    ]
    
    # Saisons et mois
    seasons = ["spring", "summer", "autumn", "fall", "winter"]
    months = ["january", "february", "march", "april", "may", "june",
              "july", "august", "september", "october", "november", "december"]
    
    # Ajout des patterns de base
    passwords.extend(patterns)
    
    # Ajout des combinaisons avec années et saisons
    for pattern in patterns:
        for year in years:
            passwords.append(f"{pattern}{year}")
            passwords.append(f"{year}{pattern}")
    
    for season in seasons:
        for year in years:
            passwords.append(f"{season}{year}")
    
    for month in months:
        for year in years[-3:]:  # Juste les 3 dernières années
            passwords.append(f"{month}{year}")
    
    # Si le nom de l'entreprise est fourni
    if company:
        company = company.lower()
        passwords.append(company)
        passwords.append(company.capitalize())
        
        # Combinaisons entreprise + année
        for year in years[-5:]:  # Juste les 5 dernières années
            passwords.append(f"{company}{year}")
            passwords.append(f"{company.capitalize()}{year}")
        
        # Combinaisons avec "welcome"
        passwords.append(f"welcome{company}")
        passwords.append(f"welcome{company.capitalize()}")
        passwords.append(f"Welcome{company}")
        passwords.append(f"Welcome{company.capitalize()}")
        
        # Combinaisons avec "admin"
        passwords.append(f"admin{company}")
        passwords.append(f"{company}admin")
    
    # Si le nom d'utilisateur est fourni
    if username:
        username = username.lower()
        passwords.append(username)
        passwords.append(username.capitalize())
        
        # Combinaisons nom d'utilisateur + année
        for year in years[-3:]:  # Juste les 3 dernières années
            passwords.append(f"{username}{year}")
            passwords.append(f"{username.capitalize()}{year}")
        
        # Si le nom d'utilisateur contient un point (prénom.nom)
        if '.' in username:
            parts = username.split('.')
            if len(parts) == 2:
                # Initiales
                initials = parts[0][0] + parts[1][0]
                passwords.append(initials)
                passwords.append(initials.upper())
                
                # Combinaisons initiales + année
                for year in years[-5:]:
                    passwords.append(f"{initials}{year}")
                    passwords.append(f"{initials.upper()}{year}")
    
    # Suppression des doublons et des mots de passe trop courts
    passwords = [p for p in list(dict.fromkeys(passwords)) if len(p) >= 4]
    
    logger.debug(f"Généré {len(passwords)} mots de passe communs")
    return passwords

def enhance_wordlist(passwords: List[str], max_size: int = 10000) -> List[str]:
    """
    Améliore une wordlist en y ajoutant des variantes
    
    Args:
        passwords: Liste de mots de passe de base
        max_size: Taille maximale de la wordlist
        
    Returns:
        List[str]: Liste des mots de passe améliorée
    """
    logger = logging.getLogger(__name__)
    enhanced = set(passwords)
    
    # Limitation pour éviter une explosion de la taille
    sample_size = min(len(passwords), 100)
    sample = random.sample(passwords, sample_size)
    
    # Ajout de quelques combinaisons
    for password in sample:
        enhanced.update(generate_combinations(password))
        
        # Si la liste est déjà assez grande, on s'arrête
        if len(enhanced) >= max_size:
            break
    
    # Conversion en liste et limitation de la taille
    result = list(enhanced)[:max_size]
    
    logger.debug(f"Wordlist améliorée: {len(passwords)} -> {len(result)} mots de passe")
    return result