"""LightGBM Model for Performance Prediction"""

import numpy as np
import lightgbm as lgb
from typing import Dict, Optional
import logging
import pickle

from .base_model import BasePerformanceModel

logger = logging.getLogger(__name__)


class LightGBMModel(BasePerformanceModel):
    """
    LightGBM gradient boosting classifier.

    Features:
    - Memory-efficient gradient boosting
    - Early stopping and feature selection
    - Speed optimization without accuracy loss
    """

    def __init__(self, params: Optional[Dict] = None):
        super().__init__("LightGBM")
        self.params = params or self._get_default_params()
        self.model = None

    def _get_default_params(self) -> Dict:
        return {
            'objective': 'multiclass',
            'metric': 'multi_logloss',
            'boosting_type': 'gbdt',
            'num_leaves': 31,
            'learning_rate': 0.05,
            'n_estimators': 100,
            'max_depth': -1,
            'min_child_samples': 20,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'reg_alpha': 0.1,
            'reg_lambda': 0.1,
            'random_state': 42,
            'verbose': -1
        }

    def train(self, X: np.ndarray, y: np.ndarray, **kwargs):
        is_valid, error = self.validate_input(X)
        if not is_valid:
            raise ValueError(f"Invalid training data: {error}")

        logger.info(f"Training {self.model_name} with {X.shape[0]} samples")

        # Determine number of classes
        num_classes = len(np.unique(y))
        params = self.params.copy()
        params['num_class'] = num_classes

        # Create and train model
        self.model = lgb.LGBMClassifier(**params)

        eval_set = kwargs.get('eval_set', None)
        if eval_set:
            self.model.fit(X, y, eval_set=eval_set)
        else:
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
