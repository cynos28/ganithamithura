"""Random Forest Model for Performance Prediction"""

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from typing import Dict, Optional
import logging
import pickle

from .base_model import BasePerformanceModel

logger = logging.getLogger(__name__)


class RandomForestModel(BasePerformanceModel):
    """
    Random Forest classifier with diverse tree generation.

    Features:
    - Controlled randomization for diversity
    - Feature importance tracking
    - Bootstrap sampling for robust predictions
    """

    def __init__(self, params: Optional[Dict] = None):
        super().__init__("RandomForest")
        self.params = params or self._get_default_params()
        self.model = None

    def _get_default_params(self) -> Dict:
        return {
            'n_estimators': 100,
            'max_depth': 10,
            'min_samples_split': 5,
            'min_samples_leaf': 2,
            'max_features': 'sqrt',
            'bootstrap': True,
            'random_state': 42,
            'n_jobs': -1
        }

    def train(self, X: np.ndarray, y: np.ndarray, **kwargs):
        is_valid, error = self.validate_input(X)
        if not is_valid:
            raise ValueError(f"Invalid training data: {error}")

        logger.info(f"Training {self.model_name} with {X.shape[0]} samples")

        self.model = RandomForestClassifier(**self.params)
        self.model.fit(X, y)
        self.is_trained = True

        # Extract feature importance
        self.feature_importance = dict(enumerate(self.model.feature_importances_))
        logger.info(f"{self.model_name} training completed")

    def predict(self, X: np.ndarray) -> np.ndarray:
        if not self.is_trained or self.model is None:
            raise RuntimeError(f"{self.model_name} is not trained yet")

        is_valid, error = self.validate_input(X)
        if not is_valid:
            raise ValueError(f"Invalid input data: {error}")

        return self.model.predict(X)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        if not self.is_trained or self.model is None:
            raise RuntimeError(f"{self.model_name} is not trained yet")

        is_valid, error = self.validate_input(X)
        if not is_valid:
            raise ValueError(f"Invalid input data: {error}")

        return self.model.predict_proba(X)

    def save_model(self, path: str):
        if not self.is_trained or self.model is None:
            raise RuntimeError("Cannot save untrained model")

        with open(path, 'wb') as f:
            pickle.dump({
                'model': self.model,
                'params': self.params,
                'feature_importance': self.feature_importance
            }, f)

        logger.info(f"{self.model_name} saved to {path}")

    def load_model(self, path: str):
        with open(path, 'rb') as f:
            data = pickle.load(f)

        self.model = data['model']
        self.params = data['params']
        self.feature_importance = data.get('feature_importance')
        self.is_trained = True

        logger.info(f"{self.model_name} loaded from {path}")
