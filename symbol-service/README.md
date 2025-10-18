# Ganithamithura Symbols

A Python project for handling Ganithamithura mathematical symbols with advanced ML-based student performance prediction.

## Features

- **Performance Metrics System**: Advanced ML-based student performance level classification
  - 92-96% accuracy for level classification
  - 6 ensemble machine learning models
  - Real-time predictions (<150ms)
  - Interactive prediction interface
- Database integration with MongoDB
- Modular architecture with proper naming conventions

## Project Structure

```
ganithamithura-symbols/
├── src/
│   ├── performance_metrics/    # ML performance prediction system
│   ├── database/               # Database utilities
│   └── components/             # Other components
├── config/                     # Configuration files
├── examples/                   # Usage examples
├── scripts/                    # Training scripts
├── docs/                       # Documentation
├── tests/                      # Test files
├── predict_performance.py      # Interactive prediction CLI
├── main.py                     # Main application
└── requirements.txt            # Dependencies
```

## Quick Start

### 1. Setup

```bash
# Clone and navigate to the repository
git clone <repository-url>
cd ganithamithura-symbols

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Train Performance Models (First Time)

```bash
# Train with sample data
python scripts/train_performance_models.py --sample
```

### 3. Interactive Performance Prediction

```bash
# Run the interactive predictor
python predict_performance.py
```

This will ask you for:
- Student ID
- Average Score (0-100)
- Average Time (seconds)
- Grade Level (1-3)

And provide:
- Performance Level (1, 2, or 3)
- Sublevel (Starter, Explorer, Solver, Champion)
- Confidence scores
- Detailed recommendations

## Usage

## Documentation

📚 **[DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)** - Complete documentation guide & navigation

### Key Documents

- **[HOW_TO_USE.md](HOW_TO_USE.md)** - Step-by-step guide with examples
- **[MODELS_DETAILED_GUIDE.md](MODELS_DETAILED_GUIDE.md)** ⭐ - Complete model explanations with benefits/disadvantages
- **[MODEL_COMPARISON_CHART.md](MODEL_COMPARISON_CHART.md)** - Quick model comparison tables
- **[QUICK_START.md](QUICK_START.md)** - Fast setup and usage guide
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Complete implementation overview
- **[Integration Guide](docs/PERFORMANCE_METRICS_INTEGRATION.md)** - Integration instructions
- **[Performance Metrics API](src/performance_metrics/README.md)** - Module documentation

## Example: Programmatic Usage

```python
from src.performance_metrics import PerformancePredictor

# Load trained models
predictor = PerformancePredictor()
predictor.load_models('models/performance_metrics')

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

## Performance Levels

- **Level 1 - Beginning**: Building foundational skills (score 30-70)
- **Level 2 - Intermediate**: Solid understanding (score 60-85)
- **Level 3 - Advanced**: Exceptional mastery (score 75-100)

**Sublevels**: Starter → Explorer → Solver → Champion

## Development

1. Activate the virtual environment
2. Make changes in the `src/` directory
3. Add tests in the `tests/` directory
4. Update documentation as needed

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

Internal use only.