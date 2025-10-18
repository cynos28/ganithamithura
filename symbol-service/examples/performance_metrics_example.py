"""
Example Usage: Performance Metrics System

Demonstrates how to train and use the performance prediction system.
"""

import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import pandas as pd
import numpy as np
from src.performance_metrics import PerformancePredictor
from src.performance_metrics.utils import TrainingUtils, DataLoader


def example_training():
    """Example: Training the performance predictor."""
    print("=" * 70)
    print("Example 1: Training Performance Predictor")
    print("=" * 70)

    # Create sample training data
    np.random.seed(42)
    n_samples = 1000

    training_data = pd.DataFrame({
        'user_id': [f'student_{i}' for i in range(n_samples)],
        'avg_score': np.random.uniform(30, 100, n_samples),
        'avg_time': np.random.uniform(20, 150, n_samples),
        'grade': np.random.randint(1, 4, n_samples),  # Grades 1-3
        'level': np.random.choice([1, 2, 3], n_samples, p=[0.4, 0.4, 0.2])
    })

    print(f"\nTraining data: {len(training_data)} samples")
    print(f"Level distribution:\n{training_data['level'].value_counts().sort_index()}\n")

    # Create grade cohorts
    cohorts = TrainingUtils.create_grade_cohorts(training_data)
    print(f"Created cohorts for {len(cohorts)} grades\n")

    # Initialize predictor
    predictor = PerformancePredictor(grade_cohorts=cohorts)

    # Train the system
    print("Training models...")
    predictor.train(training_data)

    print("\nTraining completed!")
    print("=" * 70)

    return predictor, training_data


def example_single_prediction(predictor):
    """Example: Single student prediction."""
    print("\n" + "=" * 70)
    print("Example 2: Single Student Prediction")
    print("=" * 70)

    # Example student: Mike (from README)
    student_data = {
        'user_id': 'mike_3421',
        'avg_score': 75.0,
        'avg_time': 65.0,
        'grade': 2
    }

    print(f"\nStudent Data:")
    print(f"  User ID: {student_data['user_id']}")
    print(f"  Avg Score: {student_data['avg_score']}")
    print(f"  Avg Time: {student_data['avg_time']}s")
    print(f"  Grade: {student_data['grade']}")

    # Make prediction
    result = predictor.predict(student_data, confidence_scenario='default')

    print(f"\nPrediction Results:")
    print(f"  Level: {result['level_name']}")
    print(f"  Sublevel: {result['sublevel_name']}")
    print(f"  Overall Confidence: {result['overall_confidence']:.2%} ({result['confidence_category']})")
    print(f"  Prediction Latency: {result['prediction_latency_ms']}ms")

    print(f"\nLevel Probabilities:")
    for level, prob in result['level_probabilities'].items():
        print(f"  {level}: {prob:.2%}")

    print(f"\nRecommendation:")
    print(f"  {result['recommendation']}")

    if result['validation_warnings']:
        print(f"\nWarnings: {result['validation_warnings']}")

    print("=" * 70)

    return result


def example_batch_prediction(predictor):
    """Example: Batch prediction for multiple students."""
    print("\n" + "=" * 70)
    print("Example 3: Batch Prediction")
    print("=" * 70)

    # Create batch of students
    students = [
        {'user_id': 'student_a', 'avg_score': 45.0, 'avg_time': 90.0, 'grade': 1},
        {'user_id': 'student_b', 'avg_score': 75.0, 'avg_time': 55.0, 'grade': 2},
        {'user_id': 'student_c', 'avg_score': 92.0, 'avg_time': 35.0, 'grade': 3},
        {'user_id': 'student_d', 'avg_score': 68.0, 'avg_time': 70.0, 'grade': 2},
    ]

    print(f"\nPredicting for {len(students)} students...\n")

    results = predictor.predict_batch(students, confidence_scenario='default')

    # Display results in table format
    print(f"{'User ID':<15} {'Level':<10} {'Sublevel':<12} {'Confidence':<12} {'Latency':<10}")
    print("-" * 70)

    for result in results:
        if 'error' not in result:
            print(f"{result['user_id']:<15} "
                  f"{result['level_name']:<10} "
                  f"{result['sublevel_name']:<12} "
                  f"{result['confidence_category']:<12} "
                  f"{result['prediction_latency_ms']:<10.2f}ms")

    print("=" * 70)

    return results


def example_model_evaluation(predictor, training_data):
    """Example: Evaluate model performance."""
    print("\n" + "=" * 70)
    print("Example 4: Model Evaluation")
    print("=" * 70)

    # Use a subset for evaluation
    eval_data = training_data.sample(n=100, random_state=42)

    print(f"\nEvaluating on {len(eval_data)} samples...")

    evaluation = predictor.evaluate(eval_data)

    print(f"\nEvaluation Results:")
    print(f"  Overall Accuracy: {evaluation['overall_accuracy']:.2%}")

    print(f"\n  Per-Class Accuracy:")
    for level, acc in evaluation['class_accuracies'].items():
        print(f"    {level}: {acc:.2%}")

    print("=" * 70)


def example_save_and_load(predictor):
    """Example: Save and load models."""
    print("\n" + "=" * 70)
    print("Example 5: Save and Load Models")
    print("=" * 70)

    model_dir = "/tmp/performance_models"

    # Save models
    print(f"\nSaving models to {model_dir}...")
    predictor.save_models(model_dir)
    print("Models saved successfully!")

    # Load models
    print(f"\nLoading models from {model_dir}...")
    new_predictor = PerformancePredictor()
    new_predictor.load_models(model_dir)
    print("Models loaded successfully!")

    # Test prediction with loaded model
    test_student = {
        'user_id': 'test_student',
        'avg_score': 80.0,
        'avg_time': 50.0,
        'grade': 2
    }

    result = new_predictor.predict(test_student)
    print(f"\nTest prediction with loaded model:")
    print(f"  Level: {result['level_name']}")
    print(f"  Sublevel: {result['sublevel_name']}")

    print("=" * 70)


def example_feature_importance(predictor):
    """Example: View feature importance."""
    print("\n" + "=" * 70)
    print("Example 6: Feature Importance Analysis")
    print("=" * 70)

    importance = predictor.get_feature_importance()

    print("\nFeature Importance by Model:")
    for model_name, features in importance.items():
        print(f"\n{model_name}:")
        # Sort by importance
        sorted_features = sorted(features.items(), key=lambda x: x[1], reverse=True)
        for feat_name, importance_score in sorted_features[:5]:  # Top 5
            print(f"  {feat_name}: {importance_score:.4f}")

    print("=" * 70)


def main():
    """Run all examples."""
    print("\n")
    print("*" * 70)
    print("PERFORMANCE METRICS SYSTEM - COMPLETE EXAMPLES")
    print("*" * 70)

    # Example 1: Training
    predictor, training_data = example_training()

    # Example 2: Single prediction
    example_single_prediction(predictor)

    # Example 3: Batch prediction
    example_batch_prediction(predictor)

    # Example 4: Evaluation
    example_model_evaluation(predictor, training_data)

    # Example 5: Save and load
    example_save_and_load(predictor)

    # Example 6: Feature importance
    example_feature_importance(predictor)

    print("\n")
    print("*" * 70)
    print("ALL EXAMPLES COMPLETED SUCCESSFULLY!")
    print("*" * 70)
    print("\n")


if __name__ == "__main__":
    main()
