"""Data Loading Utilities for Performance Metrics"""

import pandas as pd
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)


class DataLoader:
    """Utilities for loading and preparing data."""

    @staticmethod
    def load_training_data(file_path: str) -> pd.DataFrame:
        """
        Load training data from file.

        Args:
            file_path: Path to training data file (CSV or JSON)

        Returns:
            DataFrame with training data
        """
        logger.info(f"Loading training data from {file_path}")

        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith('.json'):
            df = pd.read_json(file_path)
        else:
            raise ValueError("Unsupported file format. Use CSV or JSON.")

        # Validate required columns
        required_columns = ['user_id', 'avg_score', 'avg_time', 'grade', 'level']
        missing = [col for col in required_columns if col not in df.columns]

        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        logger.info(f"Loaded {len(df)} training samples")
        return df

    @staticmethod
    def load_from_database(db_connection, query: Optional[str] = None) -> pd.DataFrame:
        """
        Load training data from database.

        Args:
            db_connection: Database connection object
            query: Optional SQL query (if None, loads all performance data)

        Returns:
            DataFrame with training data
        """
        if query is None:
            query = """
                SELECT user_id, avg_score, avg_time, grade, level
                FROM student_performance
                WHERE level IS NOT NULL
            """

        logger.info("Loading training data from database")
        df = pd.read_sql(query, db_connection)

        logger.info(f"Loaded {len(df)} samples from database")
        return df

    @staticmethod
    def prepare_student_data(user_id: str, avg_score: float,
                           avg_time: float, grade: int) -> Dict:
        """
        Prepare student data dictionary for prediction.

        Args:
            user_id: Student identifier
            avg_score: Average performance score
            avg_time: Average completion time
            grade: Academic grade level

        Returns:
            Dictionary with formatted student data
        """
        return {
            'user_id': user_id,
            'avg_score': float(avg_score),
            'avg_time': float(avg_time),
            'grade': int(grade)
        }

    @staticmethod
    def validate_data_quality(df: pd.DataFrame) -> Dict:
        """
        Validate data quality and report issues.

        Args:
            df: DataFrame to validate

        Returns:
            Dictionary with validation results
        """
        issues = []

        # Check for missing values
        missing = df.isnull().sum()
        if missing.any():
            issues.append(f"Missing values: {missing[missing > 0].to_dict()}")

        # Check for outliers in scores
        if 'avg_score' in df.columns:
            invalid_scores = df[(df['avg_score'] < 0) | (df['avg_score'] > 100)]
            if len(invalid_scores) > 0:
                issues.append(f"Invalid scores: {len(invalid_scores)} samples")

        # Check for negative times
        if 'avg_time' in df.columns:
            negative_times = df[df['avg_time'] <= 0]
            if len(negative_times) > 0:
                issues.append(f"Negative/zero times: {len(negative_times)} samples")

        # Check for valid grades
        if 'grade' in df.columns:
            invalid_grades = df[df['grade'] < 1]
            if len(invalid_grades) > 0:
                issues.append(f"Invalid grades: {len(invalid_grades)} samples")

        return {
            'is_valid': len(issues) == 0,
            'issues': issues,
            'total_samples': len(df)
        }
