"""K-Map Rule Engine for Pattern-Based Classification"""

import numpy as np
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class KMapRuleEngine:
    """
    Karnaugh Map-based rule engine for binary feature classification.

    Features:
    - Dynamic lookup tables for binary feature combinations
    - Rule confidence scoring based on historical accuracy
    - Pattern emergence detection
    """

    def __init__(self):
        self.model_name = "KMapRuleEngine"
        self.rule_table = {}
        self.confidence_scores = {}
        self.is_trained = False

    def train(self, X: np.ndarray, y: np.ndarray, binary_patterns: List[str], **kwargs):
        """
        Build rule table from training data.

        Args:
            X: Feature matrix (not used directly, rules based on patterns)
            y: Target labels
            binary_patterns: List of binary pattern strings for each sample
        """
        logger.info(f"Training {self.model_name} with {len(binary_patterns)} patterns")

        # Build lookup table
        pattern_labels = {}
        for pattern, label in zip(binary_patterns, y):
            if pattern not in pattern_labels:
                pattern_labels[pattern] = []
            pattern_labels[pattern].append(label)

        # Calculate most common label and confidence for each pattern
        for pattern, labels in pattern_labels.items():
            label_counts = {}
            for label in labels:
                label_counts[label] = label_counts.get(label, 0) + 1

            # Most common label
            most_common = max(label_counts.items(), key=lambda x: x[1])
            predicted_label = most_common[0]
            confidence = most_common[1] / len(labels)

            self.rule_table[pattern] = predicted_label
            self.confidence_scores[pattern] = confidence

        self.is_trained = True
        logger.info(f"{self.model_name} learned {len(self.rule_table)} rules")

    def predict(self, binary_patterns: List[str]) -> np.ndarray:
        """
        Predict labels based on binary patterns.

        Args:
            binary_patterns: List of binary pattern strings

        Returns:
            Predicted labels
        """
        if not self.is_trained:
            raise RuntimeError(f"{self.model_name} is not trained yet")

        predictions = []
        for pattern in binary_patterns:
            if pattern in self.rule_table:
                predictions.append(self.rule_table[pattern])
            else:
                # Default prediction for unseen patterns
                predictions.append(self._get_default_prediction())

        return np.array(predictions)

    def predict_proba(self, binary_patterns: List[str], num_classes: int = 3) -> np.ndarray:
        """
        Predict class probabilities based on binary patterns.

        Args:
            binary_patterns: List of binary pattern strings
            num_classes: Number of classes

        Returns:
            Probability matrix
        """
        if not self.is_trained:
            raise RuntimeError(f"{self.model_name} is not trained yet")

        probas = []
        for pattern in binary_patterns:
            proba = np.zeros(num_classes)
            if pattern in self.rule_table:
                predicted_class = self.rule_table[pattern]
                confidence = self.confidence_scores[pattern]
                proba[predicted_class] = confidence
                # Distribute remaining probability
                remaining = 1.0 - confidence
                for i in range(num_classes):
                    if i != predicted_class:
                        proba[i] = remaining / (num_classes - 1)
            else:
                # Uniform distribution for unseen patterns
                proba = np.ones(num_classes) / num_classes

            probas.append(proba)

        return np.array(probas)

    def get_rule_confidence(self, pattern: str) -> float:
        """Get confidence score for a specific pattern."""
        return self.confidence_scores.get(pattern, 0.0)

    def _get_default_prediction(self) -> int:
        """Get default prediction for unseen patterns."""
        if not self.rule_table:
            return 0
        # Return most common prediction
        label_counts = {}
        for label in self.rule_table.values():
            label_counts[label] = label_counts.get(label, 0) + 1
        return max(label_counts.items(), key=lambda x: x[1])[0]

    def save_model(self, path: str):
        """Save rule table to disk."""
        import pickle
        with open(path, 'wb') as f:
            pickle.dump({
                'rule_table': self.rule_table,
                'confidence_scores': self.confidence_scores
            }, f)
        logger.info(f"{self.model_name} saved to {path}")

    def load_model(self, path: str):
        """Load rule table from disk."""
        import pickle
        with open(path, 'rb') as f:
            data = pickle.load(f)
        self.rule_table = data['rule_table']
        self.confidence_scores = data['confidence_scores']
        self.is_trained = True
        logger.info(f"{self.model_name} loaded from {path}")
