"""Training Utilities for Performance Metrics"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, StratifiedKFold
from typing import Dict, Tuple, List
import logging

logger = logging.getLogger(__name__)


class TrainingUtils:
    """Utilities for training and validation."""

    @staticmethod
    def stratified_split(X: np.ndarray, y: np.ndarray,
                        test_size: float = 0.2,
                        random_state: int = 42) -> Tuple[np.ndarray, np.ndarray,
                                                         np.ndarray, np.ndarray]:
        """
        Create stratified train-test split.

        Args:
            X: Feature matrix
            y: Target labels
            test_size: Proportion of test set
            random_state: Random seed

        Returns:
            X_train, X_test, y_train, y_test
        """
        return train_test_split(
            X, y,
            test_size=test_size,
            stratify=y,
            random_state=random_state
        )

    @staticmethod
    def create_grade_cohorts(data: pd.DataFrame) -> Dict:
        """
        Create grade-specific cohort data for percentile calculations.

        Args:
            data: DataFrame with grade, avg_score, avg_time columns

        Returns:
            Dictionary mapping grades to cohort statistics
        """
        cohorts = {}

        for grade in data['grade'].unique():
            grade_data = data[data['grade'] == grade]

            cohorts[grade] = {
                'scores': grade_data['avg_score'].values,
                'times': grade_data['avg_time'].values,
                'efficiencies': (
                    grade_data['avg_score'] / grade_data['avg_time']
                ).values,
                'count': len(grade_data)
            }

        logger.info(f"Created cohorts for {len(cohorts)} grades")
        return cohorts

    @staticmethod
    def calculate_adaptive_thresholds(data: pd.DataFrame) -> Dict:
        """
        Calculate adaptive thresholds from training data.

        Args:
            data: Training DataFrame

        Returns:
            Dictionary of threshold values
        """
        thresholds = {
            'score_threshold': data['avg_score'].median(),
            'time_threshold': data['avg_time'].median(),
            'efficiency_threshold': (data['avg_score'] / data['avg_time']).median(),
            'percentile_threshold': 50.0
        }

        logger.info(f"Calculated adaptive thresholds: {thresholds}")
        return thresholds

    @staticmethod
    def create_cv_folds(X: np.ndarray, y: np.ndarray,
                       n_splits: int = 5) -> StratifiedKFold:
        """
        Create stratified K-fold cross-validation splits.

        Args:
            X: Feature matrix
            y: Target labels
            n_splits: Number of folds

        Returns:
            StratifiedKFold object
        """
        return StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)

    @staticmethod
    def detect_class_imbalance(y: np.ndarray) -> Dict:
        """
        Detect class imbalance in target labels.

        Args:
            y: Target labels

        Returns:
            Dictionary with class distribution statistics
        """
        unique, counts = np.unique(y, return_counts=True)
        distribution = dict(zip(unique, counts))

        total = len(y)
        percentages = {k: (v / total) * 100 for k, v in distribution.items()}

        imbalance_ratio = max(counts) / min(counts) if min(counts) > 0 else float('inf')

        return {
            'distribution': distribution,
            'percentages': percentages,
            'imbalance_ratio': imbalance_ratio,
            'is_imbalanced': imbalance_ratio > 2.0
        }

    @staticmethod
    def calculate_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict:
        """
        Calculate comprehensive evaluation metrics.

        Args:
            y_true: True labels
            y_pred: Predicted labels

        Returns:
            Dictionary of metrics
        """
        from sklearn.metrics import (
            accuracy_score, precision_score, recall_score,
            f1_score, confusion_matrix
        )

        metrics = {
            'accuracy': accuracy_score(y_true, y_pred),
            'precision': precision_score(y_true, y_pred, average='weighted'),
            'recall': recall_score(y_true, y_pred, average='weighted'),
            'f1_score': f1_score(y_true, y_pred, average='weighted'),
            'confusion_matrix': confusion_matrix(y_true, y_pred).tolist()
        }

        # Per-class metrics
        for level in np.unique(y_true):
            mask = y_true == level
            if mask.sum() > 0:
                class_acc = accuracy_score(y_true[mask], y_pred[mask])
                metrics[f'class_{level}_accuracy'] = class_acc

        return metrics
