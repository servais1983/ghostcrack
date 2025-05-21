#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module HTTP pour GhostCrack - Gère les authentifications HTTP Basic
"""

import logging
import requests
from typing import Optional, Dict, Any
from requests.auth import HTTPBasicAuth
from urllib3.exceptions import InsecureRequestWarning

# Désactivation des warnings pour les certificats auto-signés
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

class HTTPClient:
    """Client HTTP pour brute force d'authentification Basic"""
    
    def __init__(self, host: str, username: str, password: str, 
                port: Optional[int] = None, timeout: int = 10, 
                proxy: Optional[str] = None, verify_ssl: bool = False):
        """
        Initialise un client HTTP
        
        Args:
            host: Hôte cible (URL)
            username: Nom d'utilisateur
            password: Mot de passe à tester
            port: Port HTTP/HTTPS (80/443 par défaut selon le protocole)
            timeout: Timeout en secondes
            proxy: Proxy à utiliser (format: socks5://127.0.0.1:9050)
            verify_ssl: Vérifier les certificats SSL
        """
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.timeout = timeout
        self.proxy = proxy
        self.verify_ssl = verify_ssl
        self.logger = logging.getLogger(__name__)
        self.last_response = {}
        
        # Préparation de l'URL
        self.url = self._prepare_url()
    
    def _prepare_url(self) -> str:
        """
        Prépare l'URL complète
        
        Returns:
            str: URL complète
        """
        # Vérification du protocole dans l'URL
        if not self.host.startswith(('http://', 'https://')):
            # Par défaut, on utilise HTTPS
            self.host = 'https://' + self.host
        
        # Ajout du port si spécifié
        if self.port:
            # On extrait le protocole
            proto, rest = self.host.split('://', 1)
            
            # On supprime tout port existant
            if ':' in rest.split('/', 1)[0]:
                host = rest.split(':', 1)[0]
                rest = rest.split('/', 1)[1] if '/' in rest else ''
                self.host = f"{proto}://{host}:{self.port}"
                if rest:
                    self.host += f"/{rest}"
            else:
                # On ajoute simplement le port
                if '/' in rest:
                    host, path = rest.split('/', 1)
                    self.host = f"{proto}://{host}:{self.port}/{path}"
                else:
                    self.host = f"{proto}://{rest}:{self.port}"
        
        return self.host
    
    def authenticate(self) -> bool:
        """
        Tente une authentification HTTP Basic
        
        Returns:
            bool: True si l'authentification réussit, False sinon
        """
        # Configuration des proxies si nécessaire
        proxies = None
        if self.proxy:
            if self.proxy.startswith('http'):
                proxies = {'http': self.proxy, 'https': self.proxy}
            elif self.proxy.startswith('socks'):
                proxies = {'http': self.proxy, 'https': self.proxy}
        
        # Configuration de l'authentification
        auth = HTTPBasicAuth(self.username, self.password)
        
        # Headers personnalisés pour éviter la détection
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'close'
        }
        
        try:
            # Tentative d'authentification
            response = requests.get(
                self.url,
                auth=auth,
                headers=headers,
                proxies=proxies,
                timeout=self.timeout,
                verify=self.verify_ssl,
                allow_redirects=True
            )
            
            # Analyse de la réponse
            status_code = response.status_code
            self.last_response = {
                'status_code': status_code,
                'headers': dict(response.headers),
                'content_length': len(response.content),
                'response_time': response.elapsed.total_seconds(),
                'redirects': [str(r.url) for r in response.history],
                'success': False,
                'error': None
            }
            
            # Vérification du succès
            if status_code < 400:
                # Authentification réussie
                self.last_response['success'] = True
                return True
            
            # Codes d'erreur spécifiques
            if status_code == 401:
                self.last_response['error'] = 'authentication_failed'
            elif status_code == 403:
                self.last_response['error'] = 'access_denied'
            elif status_code == 429:
                self.last_response['error'] = 'rate_limited'
            elif status_code == 503:
                self.last_response['error'] = 'service_unavailable'
            else:
                self.last_response['error'] = f'http_error_{status_code}'
            
            return False
            
        except requests.exceptions.Timeout:
            self.last_response = {
                'success': False,
                'error': 'timeout',
                'message': 'Connection timeout'
            }
            return False
            
        except requests.exceptions.ConnectionError as e:
            self.last_response = {
                'success': False,
                'error': 'connection_error',
                'message': str(e)
            }
            return False
            
        except requests.exceptions.TooManyRedirects:
            self.last_response = {
                'success': False,
                'error': 'too_many_redirects',
                'message': 'Too many redirects'
            }
            return False
            
        except Exception as e:
            self.last_response = {
                'success': False,
                'error': 'unknown_error',
                'message': str(e)
            }
            return False
    
    def get_last_response(self) -> Dict[str, Any]:
        """
        Récupère la dernière réponse
        
        Returns:
            dict: La dernière réponse
        """
        return self.last_response