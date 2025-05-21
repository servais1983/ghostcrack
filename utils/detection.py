#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module de détection de blocage et de protection pour GhostCrack
"""

import logging
import re
from typing import Dict, Any, List, Optional

def detect_blocking(response: Dict[str, Any]) -> bool:
    """
    Détecte si l'authentification est bloquée
    
    Args:
        response: Réponse du serveur
        
    Returns:
        bool: True si un blocage est détecté, False sinon
    """
    logger = logging.getLogger(__name__)
    
    # Si la réponse est vide, pas de blocage détectable
    if not response:
        return False
    
    # Si la réponse contient une erreur, analyse du message d'erreur
    error = response.get('error')
    if error:
        # Liste des motifs de blocage dans les messages d'erreur
        block_patterns = [
            'banned', 'blocked', 'lockout', 'denied', 'rejected',
            'too many', 'brute force', 'throttled', 'rate limit',
            'captcha', 'recaptcha', 'temporary block', 'suspicious',
            'abuse', 'anomalous', 'unusual', 'security', 'firewall'
        ]
        
        # Message d'erreur
        message = str(response.get('message', '')).lower()
        
        # Vérification des motifs de blocage dans le message
        for pattern in block_patterns:
            if pattern in message:
                logger.warning(f"Détection de blocage: {pattern} trouvé dans le message d'erreur")
                return True
    
    # Si la réponse contient un code HTTP
    status_code = response.get('status_code')
    if status_code:
        # Codes HTTP indiquant un blocage
        if status_code in [403, 429, 503]:
            logger.warning(f"Détection de blocage: code HTTP {status_code}")
            return True
    
    # Si la réponse contient des en-têtes
    headers = response.get('headers', {})
    if headers:
        # En-têtes liés à la limitation de débit
        for header in ['X-RateLimit-Remaining', 'Retry-After', 'X-Retry-After']:
            if header in headers and int(headers.get(header, '1') or 1) <= 0:
                logger.warning(f"Détection de blocage: en-tête {header} indique une limitation de débit")
                return True
    
    # Si WAF détecté
    if detect_waf(response):
        logger.warning("Détection de blocage: WAF détecté")
        return True
    
    # Si MFA détectée
    if detect_mfa(response):
        logger.warning("Authentification à deux facteurs détectée")
        return True
    
    return False

def detect_waf(response: Dict[str, Any]) -> bool:
    """
    Détecte la présence d'un WAF (Web Application Firewall)
    
    Args:
        response: Réponse du serveur
        
    Returns:
        bool: True si un WAF est détecté, False sinon
    """
    # Si la réponse ne contient pas d'en-têtes, pas de WAF détectable
    headers = response.get('headers', {})
    if not headers:
        return False
    
    # En-têtes liés aux WAF courants
    waf_headers = [
        'X-WAF', 'X-XSS-Protection', 'X-Content-Security-Policy',
        'X-WebKit-CSP', 'X-Content-Type-Options', 'X-Frame-Options',
        'Strict-Transport-Security', 'Content-Security-Policy',
        'X-Sucuri-ID', 'Server-Timing', 'X-Powered-By'
    ]
    
    # Vérification des en-têtes de WAF
    for header in waf_headers:
        if header in headers:
            return True
    
    # Vérification des valeurs d'en-têtes pour les signatures de WAF
    for _, value in headers.items():
        value = str(value).lower()
        if any(x in value for x in ['cloudflare', 'waf', 'firewall', 'wordfence', 'sucuri', 'akamai']):
            return True
    
    return False

def detect_mfa(response: Dict[str, Any]) -> bool:
    """
    Détecte la présence d'une authentification à deux facteurs (MFA)
    
    Args:
        response: Réponse du serveur
        
    Returns:
        bool: True si MFA est détectée, False sinon
    """
    # Si la réponse est vide, pas de MFA détectable
    if not response:
        return False
    
    # Vérification du contenu de la réponse pour les signatures de MFA
    if 'body' in response:
        body = str(response.get('body', '')).lower()
        
        # Motifs liés à la MFA
        mfa_patterns = [
            'two-factor', 'two factor', '2fa', 'second factor',
            'verification code', 'security code', 'authenticator',
            'google authenticator', 'authy', 'totp', 'hotp',
            'one-time', 'one time', 'code', 'token'
        ]
        
        for pattern in mfa_patterns:
            if pattern in body:
                return True
    
    # Si le statut indique une authentification partielle
    if response.get('status_code') == 202:  # Accepted mais incomplet
        return True
    
    return False

def detect_honeypot(response: Dict[str, Any]) -> bool:
    """
    Détecte la présence d'un pot de miel (honeypot)
    
    Args:
        response: Réponse du serveur
        
    Returns:
        bool: True si un honeypot est détecté, False sinon
    """
    # Signatures de honeypot
    if 'honeypot' in str(response).lower():
        return True
    
    # Trop facile - réponse suspecte
    if response.get('success') and response.get('status_code') == 200:
        # Vérification du temps de réponse (trop rapide = suspect)
        if response.get('response_time', 1.0) < 0.01:
            return True
    
    return False

def get_rate_limit_info(response: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Extrait les informations de limitation de débit de la réponse
    
    Args:
        response: Réponse du serveur
        
    Returns:
        Optional[Dict[str, Any]]: Informations de limitation de débit, ou None si aucune
    """
    # Si la réponse ne contient pas d'en-têtes, pas d'infos de limitation
    headers = response.get('headers', {})
    if not headers:
        return None
    
    # En-têtes liés à la limitation de débit
    rate_limit_headers = {
        'remaining': ['X-RateLimit-Remaining', 'RateLimit-Remaining'],
        'limit': ['X-RateLimit-Limit', 'RateLimit-Limit'],
        'reset': ['X-RateLimit-Reset', 'RateLimit-Reset', 'Retry-After', 'X-Retry-After']
    }
    
    result = {}
    
    # Extraction des valeurs d'en-têtes
    for key, header_list in rate_limit_headers.items():
        for header in header_list:
            if header in headers:
                result[key] = headers[header]
                break
    
    return result if result else None