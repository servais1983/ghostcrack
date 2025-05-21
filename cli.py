#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GhostCrack CLI - Un outil modulaire pour les attaques par force brute éthiques
"""

import argparse
import os
import sys
import logging
from core.engine import BruteForceEngine
from utils.export import export_json, export_pdf
from utils.logger import setup_logger
from utils.wordlist import load_wordlist

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="GhostCrack - Outil de brute-force éthique",
        epilog="Utilisation éthique uniquement. Pour les pentests autorisés."
    )
    
    parser.add_argument("--target", required=True, help="Cible (IP ou nom d'hôte)")
    parser.add_argument("--protocol", required=True, choices=["ssh", "http", "ftp", "smtp", "rdp"], 
                        help="Protocole à attaquer")
    parser.add_argument("--port", type=int, help="Port du service (utilise le port par défaut si non spécifié)")
    parser.add_argument("--user", required=True, help="Nom d'utilisateur à tester")
    parser.add_argument("--wordlist", required=True, help="Chemin vers le fichier wordlist")
    parser.add_argument("--threads", type=int, default=5, help="Nombre de threads (défaut: 5)")
    parser.add_argument("--timeout", type=int, default=10, help="Timeout en secondes (défaut: 10)")
    parser.add_argument("--proxy", help="Proxy à utiliser (format: socks5://127.0.0.1:9050)")
    parser.add_argument("--export", help="Chemin pour exporter les résultats (format déterminé par l'extension)")
    parser.add_argument("--verbose", "-v", action="count", default=0, help="Niveau de verbosité")
    parser.add_argument("--ai-predict", action="store_true", help="Utiliser l'IA pour prédire les mots de passe probables")
    parser.add_argument("--generate", action="store_true", help="Générer des variations de mots de passe")
    
    return parser.parse_args()

def main():
    args = parse_arguments()
    
    # Configuration du logger
    log_level = logging.INFO
    if args.verbose >= 1:
        log_level = logging.DEBUG
        
    logger = setup_logger(log_level)
    logger.info("GhostCrack CLI démarré")
    
    # Vérification du fichier wordlist
    if not os.path.exists(args.wordlist):
        logger.error(f"Fichier wordlist non trouvé: {args.wordlist}")
        sys.exit(1)
    
    # Chargement de la wordlist
    passwords = load_wordlist(args.wordlist)
    logger.info(f"Wordlist chargée: {len(passwords)} mots de passe")
    
    # Configuration du moteur de brute-force
    engine = BruteForceEngine(
        target=args.target,
        protocol=args.protocol,
        port=args.port,
        username=args.user,
        passwords=passwords,
        threads=args.threads,
        timeout=args.timeout,
        proxy=args.proxy,
        use_ai=args.ai_predict,
        generate=args.generate,
        logger=logger
    )
    
    # Exécution de l'attaque
    logger.info(f"Démarrage de l'attaque sur {args.target} ({args.protocol})")
    results = engine.run()
    
    # Affichage des résultats
    if results.success:
        logger.info(f"SUCCÈS! Mot de passe trouvé: {results.password}")
    else:
        logger.info("Échec: Aucun mot de passe trouvé")
    
    # Export des résultats si demandé
    if args.export:
        if args.export.endswith('.json'):
            export_json(results, args.export)
            logger.info(f"Résultats exportés en JSON: {args.export}")
        elif args.export.endswith('.pdf'):
            export_pdf(results, args.export)
            logger.info(f"Résultats exportés en PDF: {args.export}")
        else:
            logger.warning(f"Format d'export non reconnu: {args.export}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())