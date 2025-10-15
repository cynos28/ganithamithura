# Performance Metrics Integration Guide

Complete guide for integrating the Performance Metrics system into your application.

## Table of Contents

1. [Installation](#installation)
2. [Project Structure](#project-structure)
3. [Quick Start](#quick-start)
4. [Integration with Main Application](#integration-with-main-application)
5. [Database Integration](#database-integration)
6. [Training Pipeline](#training-pipeline)
7. [Production Deployment](#production-deployment)
8. [API Endpoints](#api-endpoints)
9. [Monitoring and Maintenance](#monitoring-and-maintenance)

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This includes:
- numpy >= 1.24.0
- pandas >= 2.0.0
- scikit-learn >= 1.3.0
- xgboost >= 2.0.0
- lightgbm >= 4.0.0
- optuna >= 3.0.0 (for hyperparameter optimization)

### 2. Verify Installation

```python
from src.performance_metrics import PerformancePredictor
print("Performance Metrics module loaded successfully!")
```

## Project Structure

```
ganithamithura-symbols/
├── src/
│   ├── performance_metrics/          # Performance prediction module
│   │   ├── __init__.py
│   │   ├── predictor.py              # Main orchestrator
│   │   ├── README.md
│   │   ├── layers/                   # Three-layer architecture
│   │   │   ├── data_processing_layer.py
│   │   │   ├── prediction_layer.py
│   │   │   └── fusion_layer.py
│   │   ├── models/                   # ML models
│   │   │   ├── base_model.py
│   │   │   ├── xgboost_model.py
│   │   │   ├── random_forest_model.py
│   │   │   ├── neural_network_model.py
│   │   │   ├── svm_model.py
│   │   │   ├── lightgbm_model.py
│   │   │   └── kmap_engine.py
│   │   └── utils/
│   │       ├── training_utils.py
│   │       └── data_loader.py
│   ├── database/                     # Database modules
│   └── components/                   # Other components
├── config/
│   ├── performance_metrics/
│   │   └── model_config.py          # Model configurations
│   └── database_config.py
├── examples/
│   └── performance_metrics_example.py
├── docs/
│   └── PERFORMANCE_METRICS_INTEGRATION.md
├── main.py
└── requirements.txt
```

## Quick Start

### Basic Prediction

```python
from src.performance_metrics import PerformancePredictor
import pandas as pd

# Initialize predictor
predictor = PerformancePredictor()

# Load and train (first time only)
training_data = pd.read_csv('student_performance_data.csv')
predictor.train(training_data)

# Save trained models
predictor.save_models('models/performance_metrics')

# Make prediction
student = {
    'user_id': 'student_123',
    'avg_score': 75.0,
    'avg_time': 65.0,
    'grade': 5
}

result = predictor.predict(student)
print(f"Level: {result['level_name']}")
print(f"Sublevel: {result['sublevel_name']}")
print(f"Confidence: {result['confidence_category']}")
```

## Integration with Main Application

### Update main.py

```python
import os
import sys
from dotenv import load_dotenv
import logging

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.database import get_db_connection, get_database
from src.performance_metrics import PerformancePredictor
from config.database_config import DatabaseConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def initialize_performance_predictor():
    """Initialize performance predictor with trained models"""
    model_dir = 'models/performance_metrics'

    predictor = PerformancePredictor()

    # Load pre-trained models if they exist
    if os.path.exists(model_dir):
        try:
            predictor.load_models(model_dir)
            logger.info("Performance predictor loaded successfully")
            return predictor
        except Exception as e:
            logger.warning(f"Failed to load models: {e}")
            logger.info("Predictor will need to be trained before use")
            return predictor
    else:
        logger.warning(f"Model directory {model_dir} not found")
        logger.info("Predictor will need to be trained before use")
        return predictor


def predict_student_performance(predictor, user_id, avg_score, avg_time, grade):
    """
    Predict performance for a student

    Args:
        predictor: PerformancePredictor instance
        user_id: Student identifier
        avg_score: Average score (0-100)
        avg_time: Average time in seconds
        grade: Grade level

    Returns:
        Prediction result dictionary
    """
    try:
        student_data = {
            'user_id': user_id,
            'avg_score': float(avg_score),
            'avg_time': float(avg_time),
            'grade': int(grade)
        }

        result = predictor.predict(student_data)
        logger.info(f"Prediction for {user_id}: {result['level_name']}, {result['sublevel_name']}")

        return result

    except Exception as e:
        logger.error(f"Prediction failed for {user_id}: {e}")
        return None


def main():
    """Main function"""
    print("🚀 Starting Ganithamithura Symbols Application\n")

    # Initialize database
    load_dotenv()
    db_config = DatabaseConfig.from_env()
    db_connection = get_db_connection()

    if not db_connection.connect():
        print("❌ Database connection failed")
        sys.exit(1)

    db = get_database()
    logger.info("✅ Database connection successful")

    # Initialize performance predictor
    predictor = initialize_performance_predictor()

    # Example: Make a prediction
    if predictor.is_trained:
        result = predict_student_performance(
            predictor=predictor,
            user_id='test_student',
            avg_score=75.0,
            avg_time=65.0,
            grade=5
        )

        if result:
            print(f"\n✅ Prediction successful:")
            print(f"   Level: {result['level_name']}")
            print(f"   Sublevel: {result['sublevel_name']}")
            print(f"   Confidence: {result['confidence_category']}")
    else:
        print("\n⚠️  Predictor not trained. Train models first.")

    print("\n✅ Application initialized successfully")


if __name__ == "__main__":
    main()
```

## Database Integration

### MongoDB Schema for Training Data

```javascript
// Collection: student_performance
{
    _id: ObjectId("..."),
    user_id: "student_123",
    avg_score: 75.0,
    avg_time: 65.0,
    grade: 5,
    level: 1,  // Ground truth (1, 2, or 3)
    sublevel: 1,  // Optional ground truth
    timestamp: ISODate("2024-10-11T00:00:00Z")
}
```

### Loading Training Data from MongoDB

```python
from src.performance_metrics.utils import DataLoader
from src.database import get_database
import pandas as pd

def load_training_data_from_db():
    """Load training data from MongoDB"""
    db = get_database()
    collection = db['student_performance']

    # Query for labeled data
    query = {'level': {'$exists': True, '$ne': None}}

    # Load data
    data = list(collection.find(query))
    df = pd.DataFrame(data)

    # Select relevant columns
    df = df[['user_id', 'avg_score', 'avg_time', 'grade', 'level']]

    return df
```

### Saving Predictions to MongoDB

```python
def save_prediction_to_db(result):
    """Save prediction result to database"""
    db = get_database()
    collection = db['performance_predictions']

    prediction_doc = {
        'user_id': result['user_id'],
        'level': result['level'],
        'level_name': result['level_name'],
        'sublevel': result['sublevel'],
        'sublevel_name': result['sublevel_name'],
        'confidence': result['overall_confidence'],
        'confidence_category': result['confidence_category'],
        'prediction_latency_ms': result['prediction_latency_ms'],
        'recommendation': result['recommendation'],
        'timestamp': datetime.now()
    }

    collection.insert_one(prediction_doc)
```

## Training Pipeline

### Script: train_performance_models.py

```python
"""
Training script for performance metrics models
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.performance_metrics import PerformancePredictor
from src.performance_metrics.utils import TrainingUtils, DataLoader
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def train_models():
    """Train all performance prediction models"""

    # 1. Load training data
    logger.info("Loading training data...")
    training_data = DataLoader.load_training_data('data/student_performance.csv')

    # Or from database:
    # from src.database import get_database
    # db = get_database()
    # training_data = load_training_data_from_db()

    logger.info(f"Loaded {len(training_data)} training samples")

    # 2. Validate data quality
    validation = DataLoader.validate_data_quality(training_data)
    if not validation['is_valid']:
        logger.warning(f"Data quality issues: {validation['issues']}")

    # 3. Create grade cohorts
    cohorts = TrainingUtils.create_grade_cohorts(training_data)
    logger.info(f"Created cohorts for {len(cohorts)} grades")

    # 4. Calculate adaptive thresholds
    thresholds = TrainingUtils.calculate_adaptive_thresholds(training_data)
    logger.info(f"Calculated thresholds: {thresholds}")

    # 5. Initialize predictor
    predictor = PerformancePredictor(grade_cohorts=cohorts)
    predictor.update_thresholds(thresholds)

    # 6. Train models
    logger.info("Training models...")
    predictor.train(training_data)

    # 7. Evaluate
    logger.info("Evaluating models...")
    evaluation = predictor.evaluate(training_data.sample(frac=0.2))
    logger.info(f"Accuracy: {evaluation['overall_accuracy']:.2%}")

    # 8. Save models
    model_dir = 'models/performance_metrics'
    os.makedirs(model_dir, exist_ok=True)
    predictor.save_models(model_dir)
    logger.info(f"Models saved to {model_dir}")

    return predictor


if __name__ == "__main__":
    train_models()
```

## Production Deployment

### 1. Model Versioning

```python
import datetime

def save_versioned_models(predictor):
    """Save models with version timestamp"""
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    model_dir = f'models/performance_metrics_v{timestamp}'
    predictor.save_models(model_dir)

    # Create symlink to latest
    import os
    latest_link = 'models/performance_metrics_latest'
    if os.path.exists(latest_link):
        os.remove(latest_link)
    os.symlink(model_dir, latest_link)
```

### 2. Performance Monitoring

```python
import time

def monitor_prediction_performance(predictor, student_data):
    """Monitor prediction performance"""
    start_time = time.time()

    result = predictor.predict(student_data)

    latency = (time.time() - start_time) * 1000  # ms

    # Log metrics
    metrics = {
        'user_id': student_data['user_id'],
        'latency_ms': latency,
        'confidence': result['overall_confidence'],
        'level': result['level'],
        'timestamp': datetime.now()
    }

    # Save to monitoring database
    # db['prediction_metrics'].insert_one(metrics)

    return result
```

### 3. Continuous Retraining

```python
def schedule_retraining():
    """Schedule monthly model retraining"""
    from apscheduler.schedulers.background import BackgroundScheduler

    scheduler = BackgroundScheduler()
    scheduler.add_job(
        func=train_models,
        trigger='cron',
        day=1,  # First day of month
        hour=2,  # 2 AM
        id='retrain_performance_models'
    )
    scheduler.start()
```

## API Endpoints

### Flask Example

```python
from flask import Flask, request, jsonify
from src.performance_metrics import PerformancePredictor

app = Flask(__name__)
predictor = PerformancePredictor()
predictor.load_models('models/performance_metrics')


@app.route('/api/predict', methods=['POST'])
def predict():
    """Predict student performance"""
    try:
        data = request.json
        result = predictor.predict(data)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/predict/batch', methods=['POST'])
def predict_batch():
    """Batch prediction"""
    try:
        students = request.json['students']
        results = predictor.predict_batch(students)
        return jsonify({'results': results}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
```

## Monitoring and Maintenance

### Key Metrics to Track

1. **Accuracy Metrics**
   - Overall accuracy
   - Per-class accuracy
   - Confidence distribution

2. **Performance Metrics**
   - Prediction latency (target: <150ms)
   - Throughput (predictions/second)
   - Model loading time

3. **Data Quality**
   - Input validation errors
   - Missing values
   - Outlier frequency

### Monthly Maintenance Checklist

- [ ] Review prediction accuracy
- [ ] Check for model drift
- [ ] Retrain models with new data
- [ ] Update grade cohorts
- [ ] Review and update thresholds
- [ ] Check system performance metrics
- [ ] Update documentation

## Troubleshooting

### Common Issues

**Issue**: Models not loading
```python
# Solution: Check model directory and file permissions
import os
print(os.path.exists('models/performance_metrics'))
print(os.listdir('models/performance_metrics'))
```

**Issue**: Low prediction accuracy
```python
# Solution: Check data quality and retrain
from src.performance_metrics.utils import DataLoader

validation = DataLoader.validate_data_quality(training_data)
print(validation)
```

**Issue**: High latency
```python
# Solution: Profile prediction pipeline
import cProfile
cProfile.run('predictor.predict(student_data)')
```

## Support

For issues or questions:
- Check the README: `src/performance_metrics/README.md`
- Run examples: `python examples/performance_metrics_example.py`
- Review logs for error messages

---

**Last Updated**: 2024-10-11
