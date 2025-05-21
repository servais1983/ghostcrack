#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module FTP pour GhostCrack - Gère les connexions FTP
"""

import ftplib
import socket
import logging
from typing import Optional, Dict, Any

class FTPClient:
    """Client FTP pour brute force"""
    
    def __init__(self, host: str, username: str, password: str, 
                port: Optional[int] = None, timeout: int = 10, 
                proxy: Optional[str] = None):
        """
        Initialise un client FTP
        
        Args:
            host: Hôte cible
            username: Nom d'utilisateur
            password: Mot de passe à tester
            port: Port FTP (21 par défaut)
            timeout: Timeout en secondes
            proxy: Proxy à utiliser (format: socks5://127.0.0.1:9050)
        """
        self.host = host
        self.username = username
        self.password = password
        self.port = port or 21
        self.timeout = timeout
        self.proxy = proxy
        self.logger = logging.getLogger(__name__)
        self.last_response = {}
    
    def authenticate(self) -> bool:
        """
        Tente une authentification FTP
        
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
        
        ftp = None
        try:
            # Initialisation du client FTP
            ftp = ftplib.FTP(timeout=self.timeout)
            
            # Connexion via socket proxy ou directe
            if sock:
                sock.connect((self.host, self.port))
                ftp.sock = sock
                ftp.connect(host=self.host, port=self.port, timeout=self.timeout)
            else:
                ftp.connect(host=self.host, port=self.port, timeout=self.timeout)
            
            # Tentative de login
            welcome_msg = ftp.getwelcome()
            ftp.login(user=self.username, passwd=self.password)
            
            # Récupération d'informations supplémentaires
            system_info = ftp.sendcmd("SYST")
            current_dir = ftp.pwd()
            
            # On stocke les informations dans last_response
            self.last_response = {
                'success': True,
                'welcome_message': welcome_msg,
                'system_info': system_info,
                'current_dir': current_dir,
                'error': None
            }
            
            # Déconnexion propre
            try:
                ftp.quit()
            except:
                ftp.close()
            
            return True
            
        except ftplib.error_perm as e:
            # Erreur de permission (mauvais identifiants)
            error_msg = str(e)
            self.last_response = {
                'success': False,
                'error': 'authentication_failed',
                'message': error_msg
            }
            
            # Détection de bannissement
            if "530" in error_msg and any(x in error_msg.lower() for x in ["banned", "blocked", "deny", "exceeded"]):
                self.last_response['error'] = 'banned'
            
            return False
            
        except ftplib.all_errors as e:
            # Autres erreurs FTP
            self.last_response = {
                'success': False,
                'error': 'ftp_error',
                'message': str(e)
            }
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
            if ftp:
                try:
                    ftp.close()
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