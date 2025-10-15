"""Base Model Interface for Performance Prediction"""

from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Optional
import numpy as np


class BasePerformanceModel(ABC):
    """Abstract base class for all performance prediction models."""

    def __init__(self, model_name: str):
        """
        Initialize base model.

        Args:
            model_name: Name of the model for logging and tracking
        """
        self.model_name = model_name
        self.is_trained = False
        self.feature_importance = None

    @abstractmethod
    def train(self, X: np.ndarray, y: np.ndarray, **kwargs):
        """
        Train the model on provided data.

        Args:
            X: Feature matrix
            y: Target labels
            **kwargs: Additional model-specific parameters
        """
        pass

    @abstractmethod
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Predict classes for input features.

        Args:
            X: Feature matrix

        Returns:
            Predicted class labels
        """
        pass

    @abstractmethod
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Predict class probabilities for input features.

        Args:
            X: Feature matrix

        Returns:
            Probability distributions for each class
        """
        pass

    @abstractmethod
    def save_model(self, path: str):
        """
        Save trained model to disk.

        Args:
            path: File path to save the model
        """
        pass

    @abstractmethod
    def load_model(self, path: str):
        """
        Load trained model from disk.

        Args:
            path: File path to load the model from
        """
        pass

    def get_feature_importance(self) -> Optional[Dict[str, float]]:
        """
        Get feature importance scores if available.

        Returns:
            Dictionary mapping feature names to importance scores
        """
        return self.feature_importance

    def validate_input(self, X: np.ndarray) -> Tuple[bool, Optional[str]]:
        """
        Validate input data shape and values.

        Args:
            X: Feature matrix

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(X, np.ndarray):
            return False, "Input must be a numpy array"

        if len(X.shape) != 2:
            return False, f"Input must be 2D, got shape {X.shape}"

        if np.isnan(X).any():
            return False, "Input contains NaN values"

        if np.isinf(X).any():
            return False, "Input contains infinite values"

        return True, None
