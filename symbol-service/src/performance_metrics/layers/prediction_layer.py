"""
Layer 2: Multi-Model Prediction Engine

Coordinates multiple machine learning models for ensemble predictions.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
import logging

from ..models.xgboost_model import XGBoostClassifier
from ..models.random_forest_model import RandomForestModel
from ..models.neural_network_model import NeuralNetworkModel
from ..models.svm_model import SVMModel
from ..models.lightgbm_model import LightGBMModel
from ..models.kmap_engine import KMapRuleEngine

logger = logging.getLogger(__name__)


class MultiModelPredictionLayer:
    """
    Coordinates multiple ML models for ensemble prediction.

    Models:
    - XGBoost: Gradient boosting with hyperparameter optimization
    - Random Forest: Bootstrap aggregating with diverse trees
    - Neural Network: Multi-layer perceptron with adaptive sizing
    - SVM: Support vector machine with kernel strategies
    - LightGBM: Memory-efficient gradient boosting
    - K-Map: Rule-based engine for binary patterns
    """

    def __init__(self, grade: Optional[int] = None):
        """
        Initialize prediction layer with all models.

        Args:
            grade: Specific grade for grade-aware modeling
        """
        self.grade = grade

        # Initialize models
        self.xgboost = XGBoostClassifier(grade=grade)
        self.random_forest = RandomForestModel()
        self.neural_network = NeuralNetworkModel()
        self.svm = SVMModel()
        self.lightgbm = LightGBMModel()
        self.kmap = KMapRuleEngine()

        self.models = {
            'xgboost': self.xgboost,
            'random_forest': self.random_forest,
            'neural_network': self.neural_network,
            'svm': self.svm,
            'lightgbm': self.lightgbm,
            'kmap': self.kmap
        }

        self.is_trained = False
        logger.info("MultiModelPredictionLayer initialized")

    def train_all_models(self, X: np.ndarray, y: np.ndarray,
                        binary_patterns: Optional[List[str]] = None,
                        **kwargs):
        """
        Train all models in the ensemble.

        Args:
            X: Training feature matrix
            y: Training labels
            binary_patterns: Binary patterns for K-Map training
            **kwargs: Additional training parameters
        """
        logger.info(f"Training all models with {X.shape[0]} samples")

        # Train ML models
        try:
            self.xgboost.train(X, y, **kwargs)
            logger.info("XGBoost trained successfully")
        except Exception as e:
            logger.error(f"XGBoost training failed: {e}")

        try:
            self.random_forest.train(X, y)
            logger.info("Random Forest trained successfully")
        except Exception as e:
            logger.error(f"Random Forest training failed: {e}")

        try:
            self.neural_network.train(X, y)
            logger.info("Neural Network trained successfully")
        except Exception as e:
            logger.error(f"Neural Network training failed: {e}")

        try:
            self.svm.train(X, y)
            logger.info("SVM trained successfully")
        except Exception as e:
            logger.error(f"SVM training failed: {e}")

        try:
            self.lightgbm.train(X, y, **kwargs)
            logger.info("LightGBM trained successfully")
        except Exception as e:
            logger.error(f"LightGBM training failed: {e}")

        # Train K-Map if binary patterns provided
        if binary_patterns:
            try:
                self.kmap.train(X, y, binary_patterns)
                logger.info("K-Map Engine trained successfully")
            except Exception as e:
                logger.error(f"K-Map training failed: {e}")

        self.is_trained = True
        logger.info("All models trained successfully")

    def predict_ensemble(self, X: np.ndarray,
                        binary_pattern: Optional[str] = None) -> Dict[str, np.ndarray]:
        """
        Get predictions from all models.

        Args:
            X: Feature matrix for prediction
            binary_pattern: Binary pattern for K-Map prediction

        Returns:
            Dictionary mapping model names to prediction probabilities
        """
        if not self.is_trained:
            raise RuntimeError("Models are not trained yet")

        predictions = {}

        # Get predictions from ML models
        for model_name in ['xgboost', 'random_forest', 'neural_network', 'svm', 'lightgbm']:
            try:
                model = self.models[model_name]
                if model.is_trained:
                    predictions[model_name] = model.predict_proba(X)
            except Exception as e:
                logger.warning(f"{model_name} prediction failed: {e}")

        # Get K-Map prediction
        if binary_pattern and self.kmap.is_trained:
            try:
                num_classes = 3  # Default: levels 1, 2, 3
                predictions['kmap'] = self.kmap.predict_proba([binary_pattern], num_classes)
            except Exception as e:
                logger.warning(f"K-Map prediction failed: {e}")

        return predictions

    def get_model_weights(self, confidence_scenario: str = 'default') -> Dict[str, float]:
        """
        Get model weights for ensemble combination.

        Args:
            confidence_scenario: Weighting scenario ('default', 'high_confidence', etc.)

        Returns:
            Dictionary mapping model names to weights
        """
        if confidence_scenario == 'high_confidence':
            # Favor tree-based models for high confidence
            return {
                'xgboost': 0.25,
                'random_forest': 0.20,
                'neural_network': 0.15,
                'svm': 0.15,
                'lightgbm': 0.20,
                'kmap': 0.05
            }
        elif confidence_scenario == 'exploratory':
            # Balanced weights for exploration
            return {
                'xgboost': 0.18,
                'random_forest': 0.18,
                'neural_network': 0.16,
                'svm': 0.16,
                'lightgbm': 0.18,
                'kmap': 0.14
            }
        else:
            # Default weights
            return {
                'xgboost': 0.22,
                'random_forest': 0.18,
                'neural_network': 0.16,
                'svm': 0.16,
                'lightgbm': 0.20,
                'kmap': 0.08
            }

    def save_all_models(self, base_path: str):
        """Save all trained models to disk."""
        import os
        os.makedirs(base_path, exist_ok=True)

        for model_name, model in self.models.items():
            if hasattr(model, 'is_trained') and model.is_trained:
                model_path = os.path.join(base_path, f"{model_name}.pkl")
                model.save_model(model_path)

        logger.info(f"All models saved to {base_path}")

    def load_all_models(self, base_path: str):
        """Load all trained models from disk."""
        import os

        for model_name, model in self.models.items():
            model_path = os.path.join(base_path, f"{model_name}.pkl")
            if os.path.exists(model_path):
                model.load_model(model_path)

        self.is_trained = True
        logger.info(f"All models loaded from {base_path}")
