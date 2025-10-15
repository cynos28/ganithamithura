"""
Performance Predictor - Main Orchestrator

Coordinates all three layers for end-to-end student performance prediction.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
import logging
import time

from .layers.data_processing_layer import DataProcessingLayer
from .layers.prediction_layer import MultiModelPredictionLayer
from .layers.fusion_layer import DecisionFusionLayer

logger = logging.getLogger(__name__)


class PerformancePredictor:
    """
    Main orchestrator for student performance prediction system.

    Three-layer architecture:
    1. Data Processing Layer - Feature engineering
    2. Multi-Model Prediction Layer - Ensemble ML models
    3. Decision Fusion Layer - Prediction combination and output
    """

    def __init__(self, grade: Optional[int] = None,
                 grade_cohorts: Optional[Dict] = None):
        """
        Initialize performance predictor.

        Args:
            grade: Specific grade for grade-aware modeling
            grade_cohorts: Historical data by grade for percentile calculations
        """
        self.grade = grade

        # Initialize three layers
        self.data_layer = DataProcessingLayer(grade_cohorts=grade_cohorts)
        self.prediction_layer = MultiModelPredictionLayer(grade=grade)
        self.fusion_layer = DecisionFusionLayer()

        self.is_trained = False

        logger.info("PerformancePredictor initialized")

    def train(self, training_data: pd.DataFrame, **kwargs):
        """
        Train the complete prediction system.

        Args:
            training_data: DataFrame with columns: user_id, avg_score, avg_time, grade, level
            **kwargs: Additional training parameters
        """
        logger.info(f"Training PerformancePredictor with {len(training_data)} samples")

        start_time = time.time()

        # Validate training data
        required_columns = ['user_id', 'avg_score', 'avg_time', 'grade', 'level']
        for col in required_columns:
            if col not in training_data.columns:
                raise ValueError(f"Missing required column: {col}")

        # Process features for all training samples
        processed_features = []
        binary_patterns = []

        for idx, row in training_data.iterrows():
            data_dict = row.to_dict()
            features, error = self.data_layer.process(data_dict)

            if error:
                logger.warning(f"Skipping sample {idx}: {error}")
                continue

            processed_features.append(features)
            binary_patterns.append(features.get('binary_pattern', '0000'))

        # Create feature matrix
        feature_names = self._get_feature_names()
        X = self._create_feature_matrix(processed_features, feature_names)
        y = training_data['level'].values[:len(X)]

        # Train all models
        self.prediction_layer.train_all_models(X, y, binary_patterns=binary_patterns, **kwargs)

        self.is_trained = True

        elapsed_time = time.time() - start_time
        logger.info(f"Training completed in {elapsed_time:.2f} seconds")

    def predict(self, student_data: Dict, confidence_scenario: str = 'default') -> Dict:
        """
        Predict performance level and sublevel for a student.

        Args:
            student_data: Dictionary with user_id, avg_score, avg_time, grade
            confidence_scenario: Weighting scenario for ensemble

        Returns:
            Complete prediction output with confidence scores and recommendations
        """
        if not self.is_trained:
            raise RuntimeError("Predictor is not trained yet. Call train() first.")

        start_time = time.time()

        # Layer 1: Process and engineer features
        features, error = self.data_layer.process(student_data)
        if error:
            raise ValueError(f"Data processing failed: {error}")

        # Create feature matrix for prediction
        feature_names = self._get_feature_names()
        X = self._create_feature_matrix([features], feature_names)

        # Get binary pattern for K-Map
        binary_pattern = features.get('binary_pattern', '0000')

        # Layer 2: Get predictions from all models
        model_predictions = self.prediction_layer.predict_ensemble(X, binary_pattern)

        # Layer 3: Fuse predictions and generate output
        weights = self.prediction_layer.get_model_weights(confidence_scenario)

        # Combine predictions
        level, combined_proba, level_confidence = self.fusion_layer.fuse_predictions(
            model_predictions, weights
        )

        # Convert level index to actual level (1, 2, 3)
        level = level + 1

        # Assess confidence
        confidence_level, confidence_score = self.fusion_layer.assess_confidence(
            model_predictions, combined_proba
        )

        # Predict sublevel
        sublevel, sublevel_name, sublevel_confidence = self.fusion_layer.predict_sublevel(
            level, features, combined_proba
        )

        # Validate prediction
        is_valid, warnings = self.fusion_layer.validate_prediction(
            level, sublevel, features
        )

        # Create final output
        output = self.fusion_layer.create_output(
            level=level,
            sublevel=sublevel,
            sublevel_name=sublevel_name,
            combined_proba=combined_proba,
            confidence_level=confidence_level,
            confidence_score=confidence_score,
            sublevel_confidence=sublevel_confidence,
            features=features,
            warnings=warnings
        )

        # Add prediction latency
        elapsed_time = time.time() - start_time
        output['prediction_latency_ms'] = round(elapsed_time * 1000, 2)

        logger.info(f"Prediction for user {student_data['user_id']}: "
                   f"Level {level}, {sublevel_name} ({confidence_level} confidence)")

        return output

    def predict_batch(self, students_data: List[Dict],
                     confidence_scenario: str = 'default') -> List[Dict]:
        """
        Predict performance for multiple students.

        Args:
            students_data: List of student data dictionaries
            confidence_scenario: Weighting scenario for ensemble

        Returns:
            List of prediction outputs
        """
        logger.info(f"Batch prediction for {len(students_data)} students")

        results = []
        for student_data in students_data:
            try:
                result = self.predict(student_data, confidence_scenario)
                results.append(result)
            except Exception as e:
                logger.error(f"Prediction failed for user {student_data.get('user_id')}: {e}")
                results.append({
                    'user_id': student_data.get('user_id'),
                    'error': str(e)
                })

        return results

    def _get_feature_names(self) -> List[str]:
        """Get list of feature names for matrix creation."""
        return [
            'avg_score', 'avg_time', 'grade',
            'grade_normalized_score', 'efficiency_ratio', 'time_per_grade',
            'score_time_product', 'score_time_ratio', 'stability_index',
            'difficulty_adjusted_score', 'speed_category', 'score_category',
            'score_percentile', 'time_percentile', 'efficiency_percentile',
            'performance_zone', 'is_high_score', 'is_fast',
            'is_efficient', 'is_above_median'
        ]

    def _create_feature_matrix(self, features_list: List[Dict],
                               feature_names: List[str]) -> np.ndarray:
        """Create numpy feature matrix from feature dictionaries."""
        matrix = []
        for features in features_list:
            row = [features.get(name, 0) for name in feature_names]
            matrix.append(row)
        return np.array(matrix)

    def update_grade_cohorts(self, grade: int, cohort_data: Dict):
        """Update grade-specific cohort data for percentile calculations."""
        self.data_layer.update_grade_cohorts(grade, cohort_data)

    def update_thresholds(self, new_thresholds: Dict):
        """Update adaptive thresholds for binary feature generation."""
        self.data_layer.update_thresholds(new_thresholds)

    def save_models(self, model_dir: str):
        """
        Save all trained models to disk.

        Args:
            model_dir: Directory to save models
        """
        if not self.is_trained:
            raise RuntimeError("Cannot save untrained models")

        self.prediction_layer.save_all_models(model_dir)
        logger.info(f"Models saved to {model_dir}")

    def load_models(self, model_dir: str):
        """
        Load trained models from disk.

        Args:
            model_dir: Directory containing saved models
        """
        self.prediction_layer.load_all_models(model_dir)
        self.is_trained = True
        logger.info(f"Models loaded from {model_dir}")

    def get_feature_importance(self) -> Dict[str, Dict]:
        """
        Get feature importance from all models that support it.

        Returns:
            Dictionary mapping model names to feature importance scores
        """
        importance = {}

        for model_name, model in self.prediction_layer.models.items():
            if hasattr(model, 'get_feature_importance'):
                model_importance = model.get_feature_importance()
                if model_importance:
                    importance[model_name] = model_importance

        return importance

    def evaluate(self, test_data: pd.DataFrame) -> Dict:
        """
        Evaluate predictor performance on test data.

        Args:
            test_data: DataFrame with columns: user_id, avg_score, avg_time, grade, level

        Returns:
            Dictionary with evaluation metrics
        """
        if not self.is_trained:
            raise RuntimeError("Predictor is not trained yet")

        logger.info(f"Evaluating on {len(test_data)} samples")

        predictions = []
        true_labels = []

        for idx, row in test_data.iterrows():
            try:
                result = self.predict(row.to_dict())
                predictions.append(result['level'])
                true_labels.append(row['level'])
            except Exception as e:
                logger.warning(f"Prediction failed for sample {idx}: {e}")

        # Calculate accuracy
        accuracy = np.mean(np.array(predictions) == np.array(true_labels))

        # Calculate per-class accuracy
        class_accuracies = {}
        for level in [1, 2, 3]:
            mask = np.array(true_labels) == level
            if mask.sum() > 0:
                class_acc = np.mean(np.array(predictions)[mask] == np.array(true_labels)[mask])
                class_accuracies[f"Level {level}"] = class_acc

        evaluation_results = {
            'overall_accuracy': accuracy,
            'class_accuracies': class_accuracies,
            'num_samples': len(predictions)
        }

        logger.info(f"Evaluation completed: Accuracy = {accuracy:.4f}")

        return evaluation_results
