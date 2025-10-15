"""XGBoost Classifier Module for Performance Prediction"""

import numpy as np
import xgboost as xgb
from typing import Dict, Optional
import logging
import pickle

from .base_model import BasePerformanceModel

logger = logging.getLogger(__name__)


class XGBoostClassifier(BasePerformanceModel):
    """
    XGBoost gradient boosting classifier with hyperparameter optimization.

    Features:
    - Bayesian optimization for hyperparameters
    - Grade-specific model instances
    - Decision tree ensemble for complex pattern recognition
    """

    def __init__(self, grade: Optional[int] = None, params: Optional[Dict] = None):
        """
        Initialize XGBoost classifier.

        Args:
            grade: Specific grade for grade-aware modeling
            params: Custom hyperparameters
        """
        super().__init__(f"XGBoost_Grade_{grade}" if grade else "XGBoost")
        self.grade = grade
        self.params = params or self._get_default_params()
        self.model = None

    def _get_default_params(self) -> Dict:
        """Get default optimized hyperparameters."""
        return {
            'objective': 'multi:softprob',
            'eval_metric': 'mlogloss',
            'max_depth': 6,
            'learning_rate': 0.1,
            'n_estimators': 100,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'min_child_weight': 1,
            'gamma': 0,
            'reg_alpha': 0.1,
            'reg_lambda': 1.0,
            'random_state': 42,
            'tree_method': 'hist',
            'enable_categorical': False
        }

    def train(self, X: np.ndarray, y: np.ndarray, **kwargs):
        """
        Train XGBoost model with optional validation data.

        Args:
            X: Training feature matrix
            y: Training labels
            **kwargs: Additional parameters (eval_set, early_stopping_rounds, etc.)
        """
        is_valid, error = self.validate_input(X)
        if not is_valid:
            raise ValueError(f"Invalid training data: {error}")

        logger.info(f"Training {self.model_name} with {X.shape[0]} samples")

        # Create XGBoost classifier
        self.model = xgb.XGBClassifier(**self.params)

        # Train model
        eval_set = kwargs.get('eval_set', None)
        early_stopping_rounds = kwargs.get('early_stopping_rounds', 10)
        verbose = kwargs.get('verbose', False)

        if eval_set:
            self.model.fit(
                X, y,
                eval_set=eval_set,
                early_stopping_rounds=early_stopping_rounds,
                verbose=verbose
            )
        else:
            self.model.fit(X, y)

        self.is_trained = True

        # Extract feature importance
        self._extract_feature_importance()

        logger.info(f"{self.model_name} training completed")

    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Predict class labels.

        Args:
            X: Feature matrix

        Returns:
            Predicted class labels
        """
        if not self.is_trained or self.model is None:
            raise RuntimeError(f"{self.model_name} is not trained yet")

        is_valid, error = self.validate_input(X)
        if not is_valid:
            raise ValueError(f"Invalid input data: {error}")

        return self.model.predict(X)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Predict class probabilities.

        Args:
            X: Feature matrix

        Returns:
            Probability matrix (n_samples, n_classes)
        """
        if not self.is_trained or self.model is None:
            raise RuntimeError(f"{self.model_name} is not trained yet")

        is_valid, error = self.validate_input(X)
        if not is_valid:
            raise ValueError(f"Invalid input data: {error}")

        return self.model.predict_proba(X)

    def _extract_feature_importance(self):
        """Extract and store feature importance scores."""
        if self.model is not None:
            importance_dict = self.model.get_booster().get_score(importance_type='gain')
            self.feature_importance = importance_dict
            logger.debug(f"Feature importance extracted: {len(importance_dict)} features")

    def save_model(self, path: str):
        """
        Save trained model to disk.

        Args:
            path: File path to save the model
        """
        if not self.is_trained or self.model is None:
            raise RuntimeError("Cannot save untrained model")

        with open(path, 'wb') as f:
            pickle.dump({
                'model': self.model,
                'params': self.params,
                'grade': self.grade,
                'feature_importance': self.feature_importance
            }, f)

        logger.info(f"{self.model_name} saved to {path}")

    def load_model(self, path: str):
        """
        Load trained model from disk.

        Args:
            path: File path to load the model from
        """
        with open(path, 'rb') as f:
            data = pickle.load(f)

        self.model = data['model']
        self.params = data['params']
        self.grade = data['grade']
        self.feature_importance = data.get('feature_importance')
        self.is_trained = True

        logger.info(f"{self.model_name} loaded from {path}")

    def optimize_hyperparameters(self, X: np.ndarray, y: np.ndarray,
                                  param_space: Dict, n_trials: int = 50):
        """
        Optimize hyperparameters using Bayesian optimization.

        Args:
            X: Training feature matrix
            y: Training labels
            param_space: Dictionary defining parameter search space
            n_trials: Number of optimization trials
        """
        try:
            import optuna
            from sklearn.model_selection import cross_val_score

            def objective(trial):
                # Sample hyperparameters
                params = {
                    'max_depth': trial.suggest_int('max_depth', 3, 10),
                    'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3),
                    'n_estimators': trial.suggest_int('n_estimators', 50, 300),
                    'subsample': trial.suggest_float('subsample', 0.6, 1.0),
                    'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0),
                    'min_child_weight': trial.suggest_int('min_child_weight', 1, 10),
                    'gamma': trial.suggest_float('gamma', 0, 5),
                    'reg_alpha': trial.suggest_float('reg_alpha', 0, 2),
                    'reg_lambda': trial.suggest_float('reg_lambda', 0, 2),
                }
                params.update(self._get_default_params())

                model = xgb.XGBClassifier(**params)
                score = cross_val_score(model, X, y, cv=5, scoring='accuracy').mean()
                return score

            study = optuna.create_study(direction='maximize')
            study.optimize(objective, n_trials=n_trials, show_progress_bar=True)

            # Update parameters with best found
            self.params.update(study.best_params)
            logger.info(f"Hyperparameter optimization completed. Best accuracy: {study.best_value:.4f}")

        except ImportError:
            logger.warning("Optuna not installed. Skipping hyperparameter optimization.")
