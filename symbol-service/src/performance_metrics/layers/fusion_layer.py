"""
Layer 3: Decision Fusion and Output Generation

Combines predictions from multiple models and generates final classification
with confidence scores.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class DecisionFusionLayer:
    """
    Meta-learning coordinator for combining model predictions.

    Features:
    - Weighted voting ensemble
    - Hierarchical classification (level → sublevel)
    - Confidence assessment based on model agreement
    - Validation and quality control
    """

    def __init__(self):
        """Initialize decision fusion layer."""
        self.level_labels = {1: "Level 1", 2: "Level 2", 3: "Level 3"}
        self.sublevel_labels = {
            0: "Starter",
            1: "Explorer",
            2: "Solver",
            3: "Champion"
        }
        logger.info("DecisionFusionLayer initialized")

    def fuse_predictions(self, predictions: Dict[str, np.ndarray],
                        weights: Dict[str, float]) -> Tuple[int, np.ndarray, float]:
        """
        Combine predictions from multiple models using weighted voting.

        Args:
            predictions: Dictionary mapping model names to probability arrays
            weights: Dictionary mapping model names to weights

        Returns:
            Tuple of (predicted_class, combined_probabilities, confidence)
        """
        if not predictions:
            raise ValueError("No predictions provided")

        # Get number of classes from first prediction
        first_pred = next(iter(predictions.values()))
        num_classes = first_pred.shape[1] if len(first_pred.shape) > 1 else 3

        # Initialize combined probabilities
        combined_proba = np.zeros(num_classes)
        total_weight = 0.0

        # Weighted combination
        for model_name, proba in predictions.items():
            weight = weights.get(model_name, 0.0)
            if weight > 0:
                # Handle single sample prediction
                if len(proba.shape) == 1:
                    combined_proba += proba * weight
                else:
                    combined_proba += proba[0] * weight
                total_weight += weight

        # Normalize probabilities
        if total_weight > 0:
            combined_proba /= total_weight

        # Get predicted class
        predicted_class = int(np.argmax(combined_proba))

        # Calculate confidence based on max probability
        confidence = float(combined_proba[predicted_class])

        logger.debug(f"Fused prediction: class={predicted_class}, confidence={confidence:.3f}")

        return predicted_class, combined_proba, confidence

    def assess_confidence(self, predictions: Dict[str, np.ndarray],
                         combined_proba: np.ndarray) -> Tuple[str, float]:
        """
        Assess prediction confidence based on model agreement.

        Args:
            predictions: Dictionary of model predictions
            combined_proba: Combined probability distribution

        Returns:
            Tuple of (confidence_level, confidence_score)
        """
        # Calculate model agreement
        predicted_classes = []
        for proba in predictions.values():
            if len(proba.shape) == 1:
                predicted_classes.append(np.argmax(proba))
            else:
                predicted_classes.append(np.argmax(proba[0]))

        # Agreement percentage
        most_common = max(set(predicted_classes), key=predicted_classes.count)
        agreement = predicted_classes.count(most_common) / len(predicted_classes)

        # Max probability from combined prediction
        max_prob = float(np.max(combined_proba))

        # Combined confidence score
        confidence_score = (agreement * 0.5 + max_prob * 0.5)

        # Categorize confidence
        if confidence_score >= 0.80:
            confidence_level = "High"
        elif confidence_score >= 0.60:
            confidence_level = "Medium"
        else:
            confidence_level = "Low"

        logger.debug(f"Confidence: {confidence_level} ({confidence_score:.3f})")

        return confidence_level, confidence_score

    def predict_sublevel(self, level: int, features: Dict,
                        combined_proba: np.ndarray) -> Tuple[int, str, float]:
        """
        Predict sublevel based on main level and features.

        Args:
            level: Predicted main level (1, 2, or 3)
            features: Engineered features dictionary
            combined_proba: Probability distribution for level prediction

        Returns:
            Tuple of (sublevel_id, sublevel_name, sublevel_confidence)
        """
        # Extract key features
        score = features.get('avg_score', 50.0)
        efficiency = features.get('efficiency_ratio', 1.0)
        percentile = features.get('score_percentile', 50.0)
        performance_zone = features.get('performance_zone', 1)

        # Sublevel prediction logic based on level
        if level == 1:
            # Level 1: Starter or Explorer
            if score < 50 or percentile < 30:
                sublevel = 0  # Starter
                confidence = 0.85
            else:
                sublevel = 1  # Explorer
                confidence = 0.80
        elif level == 2:
            # Level 2: Explorer or Solver
            if percentile >= 60 and efficiency >= 1.0:
                sublevel = 2  # Solver
                confidence = 0.82
            else:
                sublevel = 1  # Explorer
                confidence = 0.78
        else:  # level == 3
            # Level 3: Solver or Champion
            if score >= 90 and percentile >= 80 and performance_zone >= 3:
                sublevel = 3  # Champion
                confidence = 0.90
            else:
                sublevel = 2  # Solver
                confidence = 0.85

        sublevel_name = self.sublevel_labels[sublevel]

        logger.debug(f"Sublevel prediction: {sublevel_name} ({confidence:.3f})")

        return sublevel, sublevel_name, confidence

    def validate_prediction(self, level: int, sublevel: int,
                          features: Dict) -> Tuple[bool, Optional[str]]:
        """
        Validate logical consistency of predictions.

        Args:
            level: Predicted level
            sublevel: Predicted sublevel
            features: Engineered features

        Returns:
            Tuple of (is_valid, warning_message)
        """
        warnings = []

        # Check level-sublevel consistency
        if level == 1 and sublevel >= 2:
            warnings.append("Inconsistent: Level 1 with advanced sublevel")

        if level == 3 and sublevel == 0:
            warnings.append("Inconsistent: Level 3 with Starter sublevel")

        # Check feature consistency
        score = features.get('avg_score', 50.0)
        if level == 3 and score < 70:
            warnings.append(f"Unusual: Level 3 with low score ({score})")

        if level == 1 and score > 85:
            warnings.append(f"Unusual: Level 1 with high score ({score})")

        # Edge case flagging
        time = features.get('avg_time', 60.0)
        if time > 200:
            warnings.append(f"Edge case: Very high completion time ({time}s)")

        if time < 10:
            warnings.append(f"Edge case: Very low completion time ({time}s)")

        is_valid = len(warnings) == 0
        warning_message = "; ".join(warnings) if warnings else None

        if warnings:
            logger.warning(f"Validation warnings: {warning_message}")

        return is_valid, warning_message

    def generate_recommendation(self, level: int, sublevel: int,
                               features: Dict) -> str:
        """
        Generate personalized recommendation based on prediction.

        Args:
            level: Predicted level
            sublevel: Predicted sublevel
            features: Engineered features

        Returns:
            Recommendation string
        """
        score = features.get('avg_score', 50.0)
        time = features.get('avg_time', 60.0)
        efficiency = features.get('efficiency_ratio', 1.0)
        speed_category = features.get('speed_category', 1)

        recommendations = []

        # Level-based recommendations
        if level == 1:
            recommendations.append("Focus on mastering fundamental concepts")
        elif level == 2:
            recommendations.append("Continue building on your solid foundation")
        else:
            recommendations.append("Excellent work! Challenge yourself with advanced problems")

        # Performance-specific recommendations
        if speed_category == 0:  # Slow
            recommendations.append("Work on improving speed while maintaining accuracy")
        elif speed_category == 2 and score < 80:  # Fast but low accuracy
            recommendations.append("Take more time to ensure accuracy")

        if efficiency < 0.8:
            recommendations.append("Practice efficiency in problem-solving")

        if sublevel <= 1:
            recommendations.append("Keep practicing to advance to the next level")

        return "; ".join(recommendations)

    def create_output(self, level: int, sublevel: int, sublevel_name: str,
                     combined_proba: np.ndarray, confidence_level: str,
                     confidence_score: float, sublevel_confidence: float,
                     features: Dict, warnings: Optional[str] = None) -> Dict:
        """
        Create final output dictionary with all prediction information.

        Args:
            level: Predicted level
            sublevel: Predicted sublevel ID
            sublevel_name: Predicted sublevel name
            combined_proba: Combined probability distribution
            confidence_level: Confidence category (High/Medium/Low)
            confidence_score: Numeric confidence score
            sublevel_confidence: Sublevel prediction confidence
            features: Engineered features
            warnings: Validation warnings if any

        Returns:
            Complete prediction output dictionary
        """
        output = {
            'user_id': features.get('user_id', 'unknown'),
            'level': level,
            'level_name': self.level_labels[level],
            'sublevel': sublevel,
            'sublevel_name': sublevel_name,
            'level_confidence': float(combined_proba[level - 1]),
            'sublevel_confidence': sublevel_confidence,
            'overall_confidence': confidence_score,
            'confidence_category': confidence_level,
            'level_probabilities': {
                'Level 1': float(combined_proba[0]),
                'Level 2': float(combined_proba[1]),
                'Level 3': float(combined_proba[2])
            },
            'recommendation': self.generate_recommendation(level, sublevel, features),
            'validation_warnings': warnings,
            'features_summary': {
                'avg_score': features.get('avg_score'),
                'avg_time': features.get('avg_time'),
                'efficiency_ratio': features.get('efficiency_ratio'),
                'score_percentile': features.get('score_percentile'),
                'performance_zone': features.get('performance_zone')
            }
        }

        return output
