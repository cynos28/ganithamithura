#!/usr/bin/env python3
"""
Training Script for Performance Metrics Models

This script trains all performance prediction models and saves them to disk.
"""

import sys
import os
import argparse
from datetime import datetime

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.performance_metrics import PerformancePredictor
from src.performance_metrics.utils import TrainingUtils, DataLoader
import pandas as pd
import numpy as np
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_sample_data(n_samples=1000):
    """
    Create sample training data for testing.

    Args:
        n_samples: Number of samples to generate

    Returns:
        DataFrame with sample data
    """
    logger.info(f"Generating {n_samples} sample training records...")

    np.random.seed(42)

    # Generate realistic student performance data
    data = {
        'user_id': [f'student_{i:04d}' for i in range(n_samples)],
        'avg_score': [],
        'avg_time': [],
        'grade': [],
        'level': []
    }

    for i in range(n_samples):
        grade = np.random.randint(1, 4)  # Grades 1-3

        # Generate correlated score and level
        level = np.random.choice([1, 2, 3], p=[0.35, 0.45, 0.20])

        if level == 1:
            avg_score = np.random.uniform(30, 70)
            avg_time = np.random.uniform(60, 150)
        elif level == 2:
            avg_score = np.random.uniform(60, 85)
            avg_time = np.random.uniform(40, 90)
        else:  # level == 3
            avg_score = np.random.uniform(75, 100)
            avg_time = np.random.uniform(20, 60)

        data['avg_score'].append(avg_score)
        data['avg_time'].append(avg_time)
        data['grade'].append(grade)
        data['level'].append(level)

    df = pd.DataFrame(data)
    logger.info(f"Generated sample data with {len(df)} records")
    logger.info(f"Level distribution:\n{df['level'].value_counts().sort_index()}")

    return df


def train_models(data_path=None, output_dir='models/performance_metrics',
                use_sample_data=False):
    """
    Train all performance prediction models.

    Args:
        data_path: Path to training data CSV file
        output_dir: Directory to save trained models
        use_sample_data: If True, generate sample data instead of loading from file

    Returns:
        Trained PerformancePredictor instance
    """
    logger.info("=" * 80)
    logger.info("PERFORMANCE METRICS MODEL TRAINING")
    logger.info("=" * 80)

    # Step 1: Load or generate training data
    if use_sample_data:
        logger.info("Using sample data for training...")
        training_data = create_sample_data(n_samples=2000)
    elif data_path:
        logger.info(f"Loading training data from {data_path}...")
        try:
            training_data = DataLoader.load_training_data(data_path)
        except Exception as e:
            logger.error(f"Failed to load data: {e}")
            logger.info("Falling back to sample data...")
            training_data = create_sample_data(n_samples=2000)
    else:
        logger.info("No data path provided. Using sample data...")
        training_data = create_sample_data(n_samples=2000)

    logger.info(f"Training data: {len(training_data)} samples")

    # Step 2: Validate data quality
    logger.info("\nValidating data quality...")
    validation = DataLoader.validate_data_quality(training_data)

    if validation['is_valid']:
        logger.info("✅ Data quality check passed")
    else:
        logger.warning(f"⚠️  Data quality issues: {validation['issues']}")

    # Step 3: Detect class imbalance
    logger.info("\nChecking class distribution...")
    X_temp = training_data[['avg_score', 'avg_time', 'grade']].values
    y_temp = training_data['level'].values

    imbalance_info = TrainingUtils.detect_class_imbalance(y_temp)
    logger.info(f"Class distribution: {imbalance_info['distribution']}")
    logger.info(f"Percentages: {imbalance_info['percentages']}")

    if imbalance_info['is_imbalanced']:
        logger.warning(f"⚠️  Class imbalance detected (ratio: {imbalance_info['imbalance_ratio']:.2f})")
    else:
        logger.info("✅ Classes are balanced")

    # Step 4: Create grade cohorts
    logger.info("\nCreating grade-specific cohorts...")
    cohorts = TrainingUtils.create_grade_cohorts(training_data)
    logger.info(f"Created cohorts for {len(cohorts)} grades")

    # Step 5: Calculate adaptive thresholds
    logger.info("\nCalculating adaptive thresholds...")
    thresholds = TrainingUtils.calculate_adaptive_thresholds(training_data)
    logger.info(f"Thresholds: {thresholds}")

    # Step 6: Initialize predictor
    logger.info("\nInitializing Performance Predictor...")
    predictor = PerformancePredictor(grade_cohorts=cohorts)
    predictor.update_thresholds(thresholds)

    # Step 7: Train models
    logger.info("\n" + "=" * 80)
    logger.info("TRAINING MODELS")
    logger.info("=" * 80)

    start_time = datetime.now()
    predictor.train(training_data)
    end_time = datetime.now()

    training_duration = (end_time - start_time).total_seconds()
    logger.info(f"\n✅ Training completed in {training_duration:.2f} seconds")

    # Step 8: Evaluate models
    logger.info("\n" + "=" * 80)
    logger.info("EVALUATING MODELS")
    logger.info("=" * 80)

    # Use 20% of data for evaluation
    eval_data = training_data.sample(frac=0.2, random_state=42)
    evaluation = predictor.evaluate(eval_data)

    logger.info(f"\nEvaluation Results:")
    logger.info(f"  Overall Accuracy: {evaluation['overall_accuracy']:.2%}")
    logger.info(f"  Per-Class Accuracy:")
    for level, acc in evaluation['class_accuracies'].items():
        logger.info(f"    {level}: {acc:.2%}")
    logger.info(f"  Evaluated on: {evaluation['num_samples']} samples")

    # Step 9: Feature importance
    logger.info("\n" + "=" * 80)
    logger.info("FEATURE IMPORTANCE")
    logger.info("=" * 80)

    importance = predictor.get_feature_importance()
    for model_name, features in importance.items():
        logger.info(f"\n{model_name}:")
        sorted_features = sorted(features.items(), key=lambda x: x[1], reverse=True)
        for feat_name, importance_score in sorted_features[:5]:
            logger.info(f"  {feat_name}: {importance_score:.4f}")

    # Step 10: Save models
    logger.info("\n" + "=" * 80)
    logger.info("SAVING MODELS")
    logger.info("=" * 80)

    os.makedirs(output_dir, exist_ok=True)
    predictor.save_models(output_dir)
    logger.info(f"✅ Models saved to: {output_dir}")

    # Save metadata
    metadata = {
        'training_date': datetime.now().isoformat(),
        'training_samples': len(training_data),
        'overall_accuracy': evaluation['overall_accuracy'],
        'class_accuracies': evaluation['class_accuracies'],
        'training_duration_seconds': training_duration,
        'thresholds': thresholds,
        'num_grades': len(cohorts)
    }

    import json
    metadata_path = os.path.join(output_dir, 'training_metadata.json')
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    logger.info(f"✅ Metadata saved to: {metadata_path}")

    # Step 11: Test prediction
    logger.info("\n" + "=" * 80)
    logger.info("TEST PREDICTION")
    logger.info("=" * 80)

    test_student = {
        'user_id': 'test_student',
        'avg_score': 75.0,
        'avg_time': 65.0,
        'grade': 2
    }

    logger.info(f"\nTest student data: {test_student}")
    result = predictor.predict(test_student)

    logger.info(f"\nPrediction Results:")
    logger.info(f"  Level: {result['level_name']}")
    logger.info(f"  Sublevel: {result['sublevel_name']}")
    logger.info(f"  Confidence: {result['confidence_category']} ({result['overall_confidence']:.2%})")
    logger.info(f"  Latency: {result['prediction_latency_ms']:.2f}ms")
    logger.info(f"  Recommendation: {result['recommendation']}")

    logger.info("\n" + "=" * 80)
    logger.info("TRAINING COMPLETE!")
    logger.info("=" * 80)

    return predictor


def main():
    """Main function with argument parsing."""
    parser = argparse.ArgumentParser(
        description='Train Performance Metrics Models'
    )
    parser.add_argument(
        '--data',
        type=str,
        help='Path to training data CSV file'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='models/performance_metrics',
        help='Output directory for trained models (default: models/performance_metrics)'
    )
    parser.add_argument(
        '--sample',
        action='store_true',
        help='Use sample data instead of loading from file'
    )

    args = parser.parse_args()

    try:
        predictor = train_models(
            data_path=args.data,
            output_dir=args.output,
            use_sample_data=args.sample
        )
        logger.info("\n✅ Training script completed successfully!")
        return 0
    except Exception as e:
        logger.error(f"\n❌ Training failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit(main())
