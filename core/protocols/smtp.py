#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module SMTP pour GhostCrack - Gère les connexions SMTP
"""

import smtplib
import socket
import logging
import base64
from typing import Optional, Dict, Any

class SMTPClient:
    """Client SMTP pour brute force"""
    
    def __init__(self, host: str, username: str, password: str, 
                port: Optional[int] = None, timeout: int = 10, 
                proxy: Optional[str] = None, use_ssl: bool = False):
        """
        Initialise un client SMTP
        
        Args:
            host: Hôte cible
            username: Nom d'utilisateur
            password: Mot de passe à tester
            port: Port SMTP (25 par défaut, 587 pour TLS, 465 pour SSL)
            timeout: Timeout en secondes
            proxy: Proxy à utiliser (format: socks5://127.0.0.1:9050)
            use_ssl: Utiliser SSL/TLS
        """
        self.host = host
        self.username = username
        self.password = password
        self.use_ssl = use_ssl
        
        # Détermination du port par défaut
        if port is None:
            if use_ssl:
                self.port = 465  # SSL
            else:
                self.port = 587  # STARTTLS
        else:
            self.port = port
            
        self.timeout = timeout
        self.proxy = proxy
        self.logger = logging.getLogger(__name__)
        self.last_response = {}
    
    def authenticate(self) -> bool:
        """
        Tente une authentification SMTP
        
        Returns:
            bool: True si l'authentification réussit, False sinon
        """
        # Configuration du proxy si nécessaire
        sock = None
        if self.proxy:
            import socks
            proxy_type, proxy_addr = self._parse_proxy(self.proxy)
            if proxy_type and proxy_addr:
                self.logger.debug(f"Utilisation du proxy: {self.proxy}")
                
                # Création du socket proxy
                proxy_host, proxy_port = proxy_addr.split(':')
                sock = socks.socksocket()
                
                if proxy_type == 'socks5':
                    sock.set_proxy(socks.SOCKS5, proxy_host, int(proxy_port))
                elif proxy_type == 'socks4':
                    sock.set_proxy(socks.SOCKS4, proxy_host, int(proxy_port))
                elif proxy_type == 'http':
                    sock.set_proxy(socks.HTTP, proxy_host, int(proxy_port))
                
                sock.settimeout(self.timeout)
                sock.connect((self.host, self.port))
        
        # Initialisation du client SMTP
        server = None
        try:
            # Sélection du type de connexion
            if self.use_ssl:
                server = smtplib.SMTP_SSL(
                    host=self.host,
                    port=self.port,
                    timeout=self.timeout,
                    source_address=None
                )
            else:
                server = smtplib.SMTP(
                    host=self.host,
                    port=self.port,
                    timeout=self.timeout,
                    source_address=None
                )
                
                # Activation du mode TLS si port standard TLS
                if self.port == 587:
                    server.starttls()
            
            # Récupération de la bannière
            banner = server.ehlo()[1].decode()
            
            # Tentative d'authentification
            server.login(self.username, self.password)
            
            # Si on arrive ici, l'authentification a réussi
            self.last_response = {
                'success': True,
                'banner': banner,
                'auth_method': 'LOGIN',
                'error': None
            }
            
            # Déconnexion
            server.quit()
            
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            # Erreur d'authentification (identifiants incorrects)
            self.last_response = {
                'success': False,
                'error': 'authentication_failed',
                'message': str(e)
            }
            return False
            
        except smtplib.SMTPException as e:
            # Autres erreurs SMTP
            error_msg = str(e)
            self.last_response = {
                'success': False,
                'error': 'smtp_error',
                'message': error_msg
            }
            
            # Détection de bannissement
            if any(x in error_msg.lower() for x in ["ban", "block", "deny", "too many"]):
                self.last_response['error'] = 'banned'
                
            return False
            
        except (socket.timeout, socket.error) as e:
            # Erreurs de socket
            self.last_response = {
                'success': False,
                'error': 'connection_error',
                'message': str(e)
            }
            return False
            
        except Exception as e:
            # Erreurs inconnues
            self.last_response = {
                'success': False,
                'error': 'unknown_error',
                'message': str(e)
            }
            return False
            
        finally:
            # Nettoyage
            if server:
                try:
                    server.close()
                except:
                    pass
    
    def _parse_proxy(self, proxy_str: str) -> tuple:
        """
        Parse une chaîne de proxy
        
        Args:
            proxy_str: Chaîne de proxy (ex: socks5://127.0.0.1:9050)
            
        Returns:
            tuple: (type, adresse) ou (None, None) si invalide
        """
        if not proxy_str or '://' not in proxy_str:
            return None, None
        
        try:
            proxy_type, proxy_addr = proxy_str.split('://')
            return proxy_type, proxy_addr
        except ValueError:
            return None, None
    
    def get_last_response(self) -> Dict[str, Any]:
        """
        Récupère la dernière réponse
        
        Returns:
            dict: La dernière réponse
        """
        return self.last_response