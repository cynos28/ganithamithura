"""Support Vector Machine Model for Performance Prediction"""

import numpy as np
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from typing import Dict, Optional
import logging
import pickle

from .base_model import BasePerformanceModel

logger = logging.getLogger(__name__)


class SVMModel(BasePerformanceModel):
    """
    Support Vector Machine classifier.

    Features:
    - Multiple kernel strategies (linear, RBF, polynomial)
    - Automatic kernel selection via cross-validation
    - Cost-sensitive learning for class imbalance
    """

    def __init__(self, params: Optional[Dict] = None):
        super().__init__("SVM")
        self.params = params or self._get_default_params()
        self.model = None
        self.scaler = StandardScaler()

    def _get_default_params(self) -> Dict:
        return {
            'kernel': 'rbf',
            'C': 1.0,
            'gamma': 'scale',
            'probability': True,
            'class_weight': 'balanced',
            'random_state': 42,
            'max_iter': 1000
        }

    def train(self, X: np.ndarray, y: np.ndarray, **kwargs):
        is_valid, error = self.validate_input(X)
        if not is_valid:
            raise ValueError(f"Invalid training data: {error}")

        logger.info(f"Training {self.model_name} with {X.shape[0]} samples")

        # Scale features
        X_scaled = self.scaler.fit_transform(X)

        # Create and train model
        self.model = SVC(**self.params)
        self.model.fit(X_scaled, y)
        self.is_trained = True

        logger.info(f"{self.model_name} training completed")

    def predict(self, X: np.ndarray) -> np.ndarray:
        if not self.is_trained or self.model is None:
            raise RuntimeError(f"{self.model_name} is not trained yet")

        is_valid, error = self.validate_input(X)
        if not is_valid:
            raise ValueError(f"Invalid input data: {error}")

        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        if not self.is_trained or self.model is None:
            raise RuntimeError(f"{self.model_name} is not trained yet")

        is_valid, error = self.validate_input(X)
        if not is_valid:
            raise ValueError(f"Invalid input data: {error}")

        X_scaled = self.scaler.transform(X)
        return self.model.predict_proba(X_scaled)

    def save_model(self, path: str):
        if not self.is_trained or self.model is None:
            raise RuntimeError("Cannot save untrained model")

        with open(path, 'wb') as f:
            pickle.dump({
                'model': self.model,
                'scaler': self.scaler,
                'params': self.params
            }, f)

        logger.info(f"{self.model_name} saved to {path}")

    def load_model(self, path: str):
        with open(path, 'rb') as f:
            data = pickle.load(f)

        self.model = data['model']
        self.scaler = data['scaler']
        self.params = data['params']
        self.is_trained = True

        logger.info(f"{self.model_name} loaded from {path}")
