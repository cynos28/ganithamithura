# Performance Metrics - Quick Start Guide

## Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

## Interactive Prediction (Easiest Way!)

Run the interactive script to predict student performance:

```bash
python predict_performance.py
```

This will:

1. Ask for student information (ID, score, time, grade)
2. Show a summary of your input
3. Display detailed prediction results with visualization
4. Provide recommendations
5. Allow multiple predictions

**Example Session:**

```
  Student ID: mike_3421
  Average Score (0-100): 75
  Average Time (seconds): 65
  Grade Level (1-12): 5

  🎯 CLASSIFICATION:
     Level:    Level 1 (Level 1)
     Sublevel: Explorer

  🟢 CONFIDENCE:
     Overall:  87.0% (High)
```

## Training Models (First Time)

### Option 1: Use Sample Data (Recommended for Testing)

```bash
python scripts/train_performance_models.py --sample
```

This will:

- Generate 2000 sample student records
- Train all 6 ML models
- Save models to `models/performance_metrics/`
- Display accuracy metrics
- Test a prediction

### Option 2: Use Your Own Data

```bash
python scripts/train_performance_models.py --data path/to/your/data.csv
```

Your CSV should have columns:

- `user_id` - Student identifier
- `avg_score` - Average score (0-100)
- `avg_time` - Average time in seconds
- `grade` - Grade level (1-3)
- `level` - Performance level (1, 2, or 3)

## Making Predictions

### Single Prediction

```python
from src.performance_metrics import PerformancePredictor

# Load trained models
predictor = PerformancePredictor()
predictor.load_models('models/performance_metrics')

# Predict for a student
student = {
    'user_id': 'student_123',
    'avg_score': 75.0,
    'avg_time': 65.0,
    'grade': 5
}

result = predictor.predict(student)

print(f"Level: {result['level_name']}")           # e.g., "Level 1"
print(f"Sublevel: {result['sublevel_name']}")     # e.g., "Explorer"
print(f"Confidence: {result['confidence_category']}")  # e.g., "High"
print(f"Recommendation: {result['recommendation']}")
```

### Batch Prediction

```python
students = [
    {'user_id': 'student_a', 'avg_score': 45.0, 'avg_time': 90.0, 'grade': 3},
    {'user_id': 'student_b', 'avg_score': 75.0, 'avg_time': 55.0, 'grade': 5},
    {'user_id': 'student_c', 'avg_score': 92.0, 'avg_time': 35.0, 'grade': 8},
]

results = predictor.predict_batch(students)

for result in results:
    print(f"{result['user_id']}: {result['level_name']} - {result['sublevel_name']}")
```

## Running Examples

```bash
python examples/performance_metrics_example.py
```

This demonstrates:

1. Training the system
2. Single student prediction
3. Batch prediction
4. Model evaluation
5. Saving and loading models
6. Feature importance analysis

## Output Format

```python
{
    'user_id': 'student_123',
    'level': 1,                          # 1, 2, or 3
    'level_name': 'Level 1',             # Level 1, 2, or 3
    'sublevel': 1,                       # 0-3
    'sublevel_name': 'Explorer',         # Starter, Explorer, Solver, Champion
    'level_confidence': 0.69,            # 0.0 - 1.0
    'sublevel_confidence': 0.80,         # 0.0 - 1.0
    'overall_confidence': 0.87,          # 0.0 - 1.0
    'confidence_category': 'High',       # High, Medium, Low
    'level_probabilities': {
        'Level 1': 0.69,
        'Level 2': 0.26,
        'Level 3': 0.05
    },
    'recommendation': 'Focus on speed improvement while maintaining accuracy',
    'validation_warnings': None,         # Or warning message if any
    'prediction_latency_ms': 125.5,      # Prediction time in milliseconds
    'features_summary': {
        'avg_score': 75.0,
        'avg_time': 65.0,
        'efficiency_ratio': 1.15,
        'score_percentile': 60.0,
        'performance_zone': 2
    }
}
```

## Performance Levels

### Levels

- **Level 1**: Beginning proficiency (typically score 30-70)
- **Level 2**: Intermediate proficiency (typically score 60-85)
- **Level 3**: Advanced proficiency (typically score 75-100)

### Sublevels

- **Starter**: Initial learning phase
- **Explorer**: Developing skills
- **Solver**: Competent problem solving
- **Champion**: Exceptional performance

## Common Tasks

### Evaluate Model Performance

```python
import pandas as pd

test_data = pd.read_csv('test_data.csv')
evaluation = predictor.evaluate(test_data)

print(f"Accuracy: {evaluation['overall_accuracy']:.2%}")
print(f"Per-class accuracy: {evaluation['class_accuracies']}")
```

### View Feature Importance

```python
importance = predictor.get_feature_importance()

for model_name, features in importance.items():
    print(f"\n{model_name} top features:")
    sorted_features = sorted(features.items(), key=lambda x: x[1], reverse=True)
    for feat, score in sorted_features[:5]:
        print(f"  {feat}: {score:.4f}")
```

### Update Grade Cohorts

```python
# Update percentile calculations for a specific grade
cohort_data = {
    'scores': [65, 70, 75, 80, 85],
    'times': [60, 65, 55, 50, 45],
    'efficiencies': [1.08, 1.08, 1.36, 1.60, 1.89],
    'count': 5
}
predictor.update_grade_cohorts(grade=5, cohort_data=cohort_data)
```

### Retrain Models

```python
# Load new training data
new_training_data = pd.read_csv('updated_data.csv')

# Retrain
predictor.train(new_training_data)

# Save updated models
predictor.save_models('models/performance_metrics')
```

## Troubleshooting

### Models not loading?

```bash
# Check if models exist
ls -la models/performance_metrics/
```

### Low accuracy?

- Ensure training data has balanced classes
- Increase training data size
- Check data quality

### High latency?

- Models may not be optimized
- Check system resources
- Consider reducing ensemble size

## Documentation

- **Full Documentation**: `src/performance_metrics/README.md`
- **Integration Guide**: `docs/PERFORMANCE_METRICS_INTEGRATION.md`
- **Implementation Summary**: `IMPLEMENTATION_SUMMARY.md`
- **Original Specification**: `perfromaceMetrix.md`

## Support

If you encounter issues:

1. Check the logs for error messages
2. Review the documentation
3. Run the example script to verify setup
4. Ensure all dependencies are installed

---

**Last Updated**: 2024-10-11
