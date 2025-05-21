#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module de logging pour GhostCrack
"""

import logging
import sys
import os
from datetime import datetime
from typing import Optional

def setup_logger(level: int = logging.INFO, log_file: Optional[str] = None) -> logging.Logger:
    """
    Configure le logger avec un formattage coloré en console et dans un fichier
    
    Args:
        level: Niveau de log
        log_file: Chemin vers le fichier de log (None pour désactiver)
        
    Returns:
        logging.Logger: Logger configuré
    """
    # Création du logger
    logger = logging.getLogger("ghostcrack")
    logger.setLevel(level)
    
    # Suppression des handlers existants
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Configuration du formatteur console avec couleurs
    class ColoredFormatter(logging.Formatter):
        grey = "\x1b[38;20m"
        yellow = "\x1b[33;20m"
        red = "\x1b[31;20m"
        bold_red = "\x1b[31;1m"
        green = "\x1b[32;20m"
        blue = "\x1b[34;20m"
        purple = "\x1b[35;20m"
        cyan = "\x1b[36;20m"
        reset = "\x1b[0m"
        
        format_str = "%(asctime)s [%(levelname)s] %(message)s"
        
        FORMATS = {
            logging.DEBUG: grey + format_str + reset,
            logging.INFO: blue + format_str + reset,
            logging.WARNING: yellow + format_str + reset,
            logging.ERROR: red + format_str + reset,
            logging.CRITICAL: bold_red + format_str + reset
        }
        
        def format(self, record):
            log_fmt = self.FORMATS.get(record.levelno)
            formatter = logging.Formatter(log_fmt, datefmt="%H:%M:%S")
            return formatter.format(record)
    
    # Handler console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(ColoredFormatter())
    logger.addHandler(console_handler)
    
    # Handler fichier si demandé
    if log_file:
        # Création du répertoire du fichier de log si nécessaire
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        file_handler = logging.FileHandler(log_file)
        file_formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger

def get_auto_log_file() -> str:
    """
    Génère un nom de fichier de log automatique basé sur la date
    
    Returns:
        str: Chemin vers le fichier de log
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_dir = "logs"
    
    # Création du répertoire logs si nécessaire
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    return os.path.join(log_dir, f"ghostcrack_{timestamp}.log")

def enable_debug_logging() -> logging.Logger:
    """
    Active le mode debug pour tous les logs
    
    Returns:
        logging.Logger: Logger configuré en mode debug
    """
    return setup_logger(logging.DEBUG, get_auto_log_file())