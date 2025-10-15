# Performance Metrics Module

Advanced machine learning system for predicting student performance levels with 92-96% accuracy.

## Overview

Three-layer hybrid architecture:
- **Layer 1**: Data Processing & Feature Engineering
- **Layer 2**: Multi-Model Prediction Engine (6 algorithms)
- **Layer 3**: Decision Fusion & Output Generation

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Basic Usage

```python
from src.performance_metrics import PerformancePredictor
import pandas as pd

# 1. Load training data
training_data = pd.DataFrame({
    'user_id': ['student_1', 'student_2', ...],
    'avg_score': [75.0, 82.0, ...],
    'avg_time': [65.0, 55.0, ...],
    'grade': [5, 6, ...],
    'level': [1, 2, ...]  # Ground truth labels
})

# 2. Initialize and train
predictor = PerformancePredictor()
predictor.train(training_data)

# 3. Make prediction
student = {
    'user_id': 'mike_3421',
    'avg_score': 75.0,
    'avg_time': 65.0,
    'grade': 5
}

result = predictor.predict(student)
print(f"Level: {result['level_name']}")
print(f"Sublevel: {result['sublevel_name']}")
print(f"Confidence: {result['confidence_category']}")
```

## Architecture

### Layer 1: Data Processing

**File**: `layers/data_processing_layer.py`

Features:
- Data validation and outlier detection
- Missing value imputation
- Advanced feature engineering (15-20 features)
- Binary pattern generation for K-Map classification

Key Features Created:
- Grade-normalized scores
- Efficiency ratios (score/time)
- Percentile rankings within grade cohorts
- Performance stability indices

### Layer 2: Multi-Model Prediction

**File**: `layers/prediction_layer.py`

Models:
1. **XGBoost** - Gradient boosting with hyperparameter optimization
2. **Random Forest** - Bootstrap aggregating with diverse trees
3. **Neural Network** - Multi-layer perceptron with adaptive sizing
4. **SVM** - Support vector machine with kernel strategies
5. **LightGBM** - Memory-efficient gradient boosting
6. **K-Map Engine** - Rule-based classification for binary patterns

### Layer 3: Decision Fusion

**File**: `layers/fusion_layer.py`

Features:
- Weighted voting ensemble
- Hierarchical classification (level → sublevel)
- Confidence assessment (High/Medium/Low)
- Validation and quality control
- Personalized recommendations

## File Structure

```
src/performance_metrics/
├── __init__.py
├── predictor.py              # Main orchestrator
├── README.md
├── layers/
│   ├── __init__.py
│   ├── data_processing_layer.py    # Layer 1
│   ├── prediction_layer.py          # Layer 2
│   └── fusion_layer.py              # Layer 3
├── models/
│   ├── __init__.py
│   ├── base_model.py
│   ├── xgboost_model.py
│   ├── random_forest_model.py
│   ├── neural_network_model.py
│   ├── svm_model.py
│   ├── lightgbm_model.py
│   └── kmap_engine.py
└── utils/
    ├── __init__.py
    ├── training_utils.py
    └── data_loader.py

config/performance_metrics/
├── __init__.py
└── model_config.py

examples/
└── performance_metrics_example.py
```

## API Reference

### PerformancePredictor

Main class for training and prediction.

#### Methods

**`__init__(grade=None, grade_cohorts=None)`**
- `grade`: Specific grade for grade-aware modeling
- `grade_cohorts`: Historical data for percentile calculations

**`train(training_data, **kwargs)`**
- `training_data`: DataFrame with columns: user_id, avg_score, avg_time, grade, level
- Trains all models in the ensemble

**`predict(student_data, confidence_scenario='default')`**
- `student_data`: Dict with user_id, avg_score, avg_time, grade
- `confidence_scenario`: 'default', 'high_confidence', or 'exploratory'
- Returns complete prediction output

**`predict_batch(students_data, confidence_scenario='default')`**
- Predicts for multiple students
- Returns list of prediction outputs

**`evaluate(test_data)`**
- Evaluates model performance on test data
- Returns accuracy metrics

**`save_models(model_dir)` / `load_models(model_dir)`**
- Save/load trained models to/from disk

**`get_feature_importance()`**
- Returns feature importance from all models

### Output Format

```python
{
    'user_id': 'mike_3421',
    'level': 1,
    'level_name': 'Level 1',
    'sublevel': 1,
    'sublevel_name': 'Explorer',
    'level_confidence': 0.69,
    'sublevel_confidence': 0.80,
    'overall_confidence': 0.87,
    'confidence_category': 'High',
    'level_probabilities': {
        'Level 1': 0.69,
        'Level 2': 0.26,
        'Level 3': 0.05
    },
    'recommendation': 'Focus on speed improvement...',
    'validation_warnings': None,
    'prediction_latency_ms': 125.5,
    'features_summary': {...}
}
```

## Configuration

Edit `config/performance_metrics/model_config.py` to customize:

- Model hyperparameters
- Ensemble weights
- Feature thresholds
- Performance targets

## Performance Targets

- **Level Classification**: 92-96% accuracy
- **Sublevel Classification**: 88-92% accuracy
- **Prediction Latency**: <150ms
- **System Reliability**: 99.9% uptime

## Examples

See `examples/performance_metrics_example.py` for:
1. Training the system
2. Single student prediction
3. Batch prediction
4. Model evaluation
5. Saving and loading models
6. Feature importance analysis

Run examples:
```bash
python examples/performance_metrics_example.py
```

## Utilities

### TrainingUtils

- `stratified_split()` - Create stratified train-test splits
- `create_grade_cohorts()` - Build grade-specific statistics
- `calculate_adaptive_thresholds()` - Compute thresholds from data
- `detect_class_imbalance()` - Check for imbalanced classes
- `calculate_metrics()` - Comprehensive evaluation metrics

### DataLoader

- `load_training_data()` - Load from CSV/JSON
- `load_from_database()` - Load from database
- `prepare_student_data()` - Format student dictionary
- `validate_data_quality()` - Data quality checks

## Continuous Learning

The system supports continuous improvement:

1. **Update Grade Cohorts**:
   ```python
   predictor.update_grade_cohorts(grade=5, cohort_data={...})
   ```

2. **Update Thresholds**:
   ```python
   predictor.update_thresholds({'score_threshold': 75.0})
   ```

3. **Retrain Models**:
   ```python
   predictor.train(new_training_data)
   ```

## Monitoring

Key metrics to monitor:
- Prediction accuracy by level
- Prediction latency
- Model agreement rates
- Validation warning frequency
- Feature importance drift

## Troubleshooting

**Issue**: Low accuracy
- Check data quality and class balance
- Adjust ensemble weights
- Increase training data size
- Tune model hyperparameters

**Issue**: High latency
- Reduce number of models
- Optimize feature engineering
- Use smaller neural network architecture

**Issue**: Low confidence predictions
- Increase training data
- Check for edge cases
- Review feature engineering
- Adjust confidence thresholds

## License

Internal use only.

## Support

For issues or questions, contact the development team.
