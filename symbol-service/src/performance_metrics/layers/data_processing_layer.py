"""
Layer 1: Data Processing and Feature Engineering

Transforms raw student performance data into engineered features
suitable for machine learning models.
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class DataProcessingLayer:
    """
    Advanced feature engineering for student performance data.

    Transforms basic inputs (user_id, avg_score, avg_time, grade) into
    15-20 engineered features including:
    - Grade-normalized scores
    - Efficiency ratios
    - Percentile rankings
    - Performance stability indices
    - Binary feature patterns for K-Map classification
    """

    def __init__(self, grade_cohorts: Optional[Dict] = None):
        """
        Initialize data processing layer.

        Args:
            grade_cohorts: Historical data by grade for percentile calculations
        """
        self.grade_cohorts = grade_cohorts or {}
        self.thresholds = self._initialize_thresholds()
        logger.info("DataProcessingLayer initialized")

    def _initialize_thresholds(self) -> Dict:
        """Initialize adaptive thresholds for binary feature generation."""
        return {
            'score_threshold': 70.0,
            'time_threshold': 60.0,
            'efficiency_threshold': 1.0,
            'percentile_threshold': 50.0
        }

    def validate_input(self, data: Dict) -> Tuple[bool, Optional[str]]:
        """
        Validate input data for missing values and outliers.

        Args:
            data: Dictionary with user_id, avg_score, avg_time, grade

        Returns:
            Tuple of (is_valid, error_message)
        """
        required_fields = ['user_id', 'avg_score', 'avg_time', 'grade']

        # Check for missing fields
        for field in required_fields:
            if field not in data:
                return False, f"Missing required field: {field}"

        # Validate score range
        if not 0 <= data['avg_score'] <= 100:
            return False, f"avg_score must be between 0-100, got {data['avg_score']}"

        # Validate time (positive value)
        if data['avg_time'] <= 0:
            return False, f"avg_time must be positive, got {data['avg_time']}"

        # Validate grade
        if not isinstance(data['grade'], int) or data['grade'] < 1:
            return False, f"grade must be a positive integer, got {data['grade']}"

        # Outlier detection for time (3 standard deviations)
        if data['avg_time'] > 500:  # Reasonable upper bound
            logger.warning(f"Unusual avg_time detected: {data['avg_time']}s")

        return True, None

    def impute_missing_values(self, data: Dict) -> Dict:
        """
        Handle missing values using appropriate imputation strategies.

        Args:
            data: Input data dictionary

        Returns:
            Data with imputed values
        """
        cleaned_data = data.copy()

        # Impute missing score with grade-specific median
        if 'avg_score' not in cleaned_data or pd.isna(cleaned_data['avg_score']):
            grade = cleaned_data.get('grade', 5)
            cleaned_data['avg_score'] = self._get_grade_median_score(grade)
            logger.info(f"Imputed avg_score for grade {grade}")

        # Impute missing time with grade-specific median
        if 'avg_time' not in cleaned_data or pd.isna(cleaned_data['avg_time']):
            grade = cleaned_data.get('grade', 5)
            cleaned_data['avg_time'] = self._get_grade_median_time(grade)
            logger.info(f"Imputed avg_time for grade {grade}")

        return cleaned_data

    def _get_grade_median_score(self, grade: int) -> float:
        """Get median score for a grade cohort."""
        if grade in self.grade_cohorts and 'scores' in self.grade_cohorts[grade]:
            return np.median(self.grade_cohorts[grade]['scores'])
        return 50.0  # Default median

    def _get_grade_median_time(self, grade: int) -> float:
        """Get median time for a grade cohort."""
        if grade in self.grade_cohorts and 'times' in self.grade_cohorts[grade]:
            return np.median(self.grade_cohorts[grade]['times'])
        return 60.0  # Default median

    def engineer_features(self, data: Dict) -> Dict:
        """
        Create advanced engineered features from raw input.

        Args:
            data: Validated input data

        Returns:
            Dictionary with all engineered features
        """
        features = data.copy()

        # Extract base values
        score = data['avg_score']
        time = data['avg_time']
        grade = data['grade']

        # 1. Grade-normalized score (score per grade level)
        features['grade_normalized_score'] = score / grade if grade > 0 else score

        # 2. Efficiency ratio (points per second)
        features['efficiency_ratio'] = score / time if time > 0 else 0

        # 3. Time per grade factor
        features['time_per_grade'] = time / grade if grade > 0 else time

        # 4. Score-time interaction
        features['score_time_product'] = score * time
        features['score_time_ratio'] = (score ** 2) / time if time > 0 else 0

        # 5. Performance stability index
        features['stability_index'] = self._calculate_stability_index(score, time)

        # 6. Grade difficulty adjustment
        features['difficulty_adjusted_score'] = self._adjust_for_grade_difficulty(score, grade)

        # 7. Speed category (fast, medium, slow)
        features['speed_category'] = self._categorize_speed(time, grade)

        # 8. Score category (low, medium, high)
        features['score_category'] = self._categorize_score(score)

        # 9. Percentile rankings within grade cohort
        features['score_percentile'] = self._calculate_percentile(score, grade, 'score')
        features['time_percentile'] = self._calculate_percentile(time, grade, 'time')

        # 10. Efficiency percentile
        features['efficiency_percentile'] = self._calculate_percentile(
            features['efficiency_ratio'], grade, 'efficiency'
        )

        # 11. Performance zone (combination of score and time)
        features['performance_zone'] = self._determine_performance_zone(
            features['score_category'], features['speed_category']
        )

        # 12. Binary features for K-Map classification
        binary_features = self._generate_binary_features(features)
        features.update(binary_features)

        logger.debug(f"Generated {len(features)} features for user {data['user_id']}")

        return features

    def _calculate_stability_index(self, score: float, time: float) -> float:
        """Calculate performance stability based on score and time consistency."""
        # Higher stability when score is high and time is moderate
        score_stability = score / 100.0
        time_stability = 1.0 - abs(time - 60.0) / 100.0
        return (score_stability + max(0, time_stability)) / 2.0

    def _adjust_for_grade_difficulty(self, score: float, grade: int) -> float:
        """Adjust score based on grade difficulty (higher grades = harder)."""
        difficulty_multiplier = 1.0 + (grade - 1) * 0.05  # 5% increase per grade
        return score * difficulty_multiplier

    def _categorize_speed(self, time: float, grade: int) -> int:
        """Categorize speed: 0=slow, 1=medium, 2=fast."""
        grade_adjusted_time = time / grade if grade > 0 else time

        if grade_adjusted_time < 10:
            return 2  # Fast
        elif grade_adjusted_time < 15:
            return 1  # Medium
        else:
            return 0  # Slow

    def _categorize_score(self, score: float) -> int:
        """Categorize score: 0=low, 1=medium, 2=high."""
        if score >= 80:
            return 2  # High
        elif score >= 60:
            return 1  # Medium
        else:
            return 0  # Low

    def _calculate_percentile(self, value: float, grade: int, metric: str) -> float:
        """Calculate percentile ranking within grade cohort."""
        if grade not in self.grade_cohorts:
            return 50.0  # Default to median

        cohort_data = self.grade_cohorts.get(grade, {})

        if metric == 'score' and 'scores' in cohort_data:
            values = cohort_data['scores']
        elif metric == 'time' and 'times' in cohort_data:
            values = cohort_data['times']
        elif metric == 'efficiency' and 'efficiencies' in cohort_data:
            values = cohort_data['efficiencies']
        else:
            return 50.0

        # Calculate percentile
        percentile = (np.sum(values <= value) / len(values)) * 100
        return percentile

    def _determine_performance_zone(self, score_cat: int, speed_cat: int) -> int:
        """
        Determine performance zone based on score and speed categories.

        Zones:
        0: Low performance (low score, slow speed)
        1: Developing (mixed)
        2: Proficient (good score or good speed)
        3: Advanced (high score and fast speed)
        """
        if score_cat == 2 and speed_cat == 2:
            return 3  # Advanced
        elif score_cat >= 1 and speed_cat >= 1:
            return 2  # Proficient
        elif score_cat >= 1 or speed_cat >= 1:
            return 1  # Developing
        else:
            return 0  # Low performance

    def _generate_binary_features(self, features: Dict) -> Dict:
        """
        Generate binary features for K-Map rule-based classification.

        Binary features based on adaptive thresholds:
        - is_high_score: score > threshold
        - is_fast: time < threshold
        - is_efficient: efficiency_ratio > threshold
        - is_above_median: percentile > 50
        """
        binary = {}

        binary['is_high_score'] = int(
            features['avg_score'] > self.thresholds['score_threshold']
        )
        binary['is_fast'] = int(
            features['avg_time'] < self.thresholds['time_threshold']
        )
        binary['is_efficient'] = int(
            features['efficiency_ratio'] > self.thresholds['efficiency_threshold']
        )
        binary['is_above_median'] = int(
            features['score_percentile'] > self.thresholds['percentile_threshold']
        )

        # Create binary pattern string (for K-Map lookup)
        binary['binary_pattern'] = ''.join([
            str(binary['is_high_score']),
            str(binary['is_fast']),
            str(binary['is_efficient']),
            str(binary['is_above_median'])
        ])

        return binary

    def update_thresholds(self, new_thresholds: Dict):
        """Update adaptive thresholds based on performance feedback."""
        self.thresholds.update(new_thresholds)
        logger.info(f"Updated thresholds: {self.thresholds}")

    def update_grade_cohorts(self, grade: int, cohort_data: Dict):
        """Update grade-specific cohort data for percentile calculations."""
        self.grade_cohorts[grade] = cohort_data
        logger.info(f"Updated cohort data for grade {grade}")

    def process(self, data: Dict) -> Tuple[Optional[Dict], Optional[str]]:
        """
        Main processing pipeline for feature engineering.

        Args:
            data: Raw input data

        Returns:
            Tuple of (engineered_features, error_message)
        """
        # Validate input
        is_valid, error = self.validate_input(data)
        if not is_valid:
            logger.error(f"Validation failed: {error}")
            return None, error

        # Impute missing values
        cleaned_data = self.impute_missing_values(data)

        # Engineer features
        features = self.engineer_features(cleaned_data)

        logger.info(f"Successfully processed data for user {data['user_id']}")
        return features, None
