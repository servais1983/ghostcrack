#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module de prédiction de mots de passe pour GhostCrack basé sur l'IA
"""

import logging
import re
import os
import pickle
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import warnings

try:
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.pipeline import Pipeline
    from sklearn.model_selection import train_test_split
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

class PasswordPredictor:
    """
    Classe de prédiction de mots de passe basée sur l'IA
    
    Cette classe utilise un modèle de Naive Bayes multinomial pour prédire
    la probabilité qu'un mot de passe soit correct.
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialise le prédicteur de mots de passe
        
        Args:
            model_path: Chemin vers un modèle pré-entraîné (optionnel)
        """
        self.logger = logging.getLogger(__name__)
        
        # Vérification de la disponibilité de scikit-learn
        if not SKLEARN_AVAILABLE:
            self.logger.warning("scikit-learn n'est pas installé. La prédiction IA ne sera pas disponible.")
            self.sklearn_available = False
            return
        else:
            self.sklearn_available = True
        
        # Suppression des avertissements non pertinents
        warnings.filterwarnings("ignore", category=UserWarning)
        
        # Initialisation du modèle
        self.vectorizer = CountVectorizer(analyzer='char', ngram_range=(2, 3))
        self.classifier = MultinomialNB()
        self.pipeline = Pipeline([
            ('vectorizer', self.vectorizer),
            ('classifier', self.classifier)
        ])
        
        # Chargement du modèle pré-entraîné si disponible
        self.model_loaded = False
        if model_path and os.path.exists(model_path):
            try:
                with open(model_path, 'rb') as f:
                    self.pipeline = pickle.load(f)
                self.model_loaded = True
                self.logger.info(f"Modèle chargé depuis: {model_path}")
            except Exception as e:
                self.logger.error(f"Erreur lors du chargement du modèle: {e}")
    
    def train(self, passwords: List[str], labels: List[int], 
             test_size: float = 0.2) -> Dict[str, float]:
        """
        Entraîne le modèle de prédiction
        
        Args:
            passwords: Liste des mots de passe
            labels: Liste des étiquettes (1 pour correct, 0 pour incorrect)
            test_size: Proportion des données à utiliser pour les tests
            
        Returns:
            Dict[str, float]: Métriques d'évaluation
        """
        if not self.sklearn_available:
            self.logger.error("scikit-learn est requis pour l'entraînement du modèle")
            return {}
        
        if len(passwords) != len(labels):
            self.logger.error("Le nombre de mots de passe et d'étiquettes doit être identique")
            return {}
        
        # Séparation des données d'entraînement et de test
        X_train, X_test, y_train, y_test = train_test_split(
            passwords, labels, test_size=test_size, random_state=42)
        
        # Entraînement du modèle
        self.pipeline.fit(X_train, y_train)
        
        # Évaluation du modèle
        accuracy = self.pipeline.score(X_test, y_test)
        
        # Calcul des prédictions
        y_pred = self.pipeline.predict(X_test)
        
        # Calcul des métriques
        metrics = {
            'accuracy': accuracy,
        }
        
        self.model_loaded = True
        self.logger.info(f"Modèle entraîné avec une précision de {accuracy:.2f}")
        
        return metrics
    
    def save_model(self, path: str) -> bool:
        """
        Sauvegarde le modèle entraîné
        
        Args:
            path: Chemin vers le fichier de sortie
            
        Returns:
            bool: True si la sauvegarde a réussi, False sinon
        """
        if not self.sklearn_available or not self.model_loaded:
            self.logger.error("Aucun modèle entraîné à sauvegarder")
            return False
        
        # Création du répertoire si nécessaire
        output_dir = os.path.dirname(path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        try:
            with open(path, 'wb') as f:
                pickle.dump(self.pipeline, f)
            self.logger.info(f"Modèle sauvegardé dans: {path}")
            return True
        except Exception as e:
            self.logger.error(f"Erreur lors de la sauvegarde du modèle: {e}")
            return False
    
    def predict_score(self, password: str) -> float:
        """
        Prédit le score d'un mot de passe
        
        Args:
            password: Mot de passe à évaluer
            
        Returns:
            float: Score de probabilité (entre 0 et 1)
        """
        if not self.sklearn_available or not self.model_loaded:
            # Retourne un score basé sur des heuristiques simples si le modèle n'est pas disponible
            return self._heuristic_score(password)
        
        try:
            # Prédiction de la probabilité
            prob = self.pipeline.predict_proba([password])[0][1]
            return prob
        except Exception as e:
            self.logger.error(f"Erreur lors de la prédiction: {e}")
            return self._heuristic_score(password)
    
    def _heuristic_score(self, password: str) -> float:
        """
        Calcule un score heuristique pour un mot de passe
        
        Cette méthode est utilisée comme fallback si le modèle n'est pas disponible
        
        Args:
            password: Mot de passe à évaluer
            
        Returns:
            float: Score heuristique (entre 0 et 1)
        """
        # Longueur (40%)
        length_score = min(1.0, len(password) / 12) * 0.4
        
        # Complexité (60%)
        has_upper = bool(re.search(r'[A-Z]', password)) * 0.15
        has_lower = bool(re.search(r'[a-z]', password)) * 0.15
        has_digit = bool(re.search(r'\d', password)) * 0.15
        has_special = bool(re.search(r'[^A-Za-z0-9]', password)) * 0.15
        
        return length_score + has_upper + has_lower + has_digit + has_special
    
    def rank_passwords(self, passwords: List[str]) -> List[Tuple[str, float]]:
        """
        Classe une liste de mots de passe par probabilité décroissante
        
        Args:
            passwords: Liste des mots de passe à classer
            
        Returns:
            List[Tuple[str, float]]: Liste de tuples (mot de passe, score) triée
        """
        if not passwords:
            return []
        
        # Calcul des scores
        scores = []
        for password in passwords:
            score = self.predict_score(password)
            scores.append((password, score))
        
        # Tri par score décroissant
        scores.sort(key=lambda x: x[1], reverse=True)
        
        return scores