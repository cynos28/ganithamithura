# Model Comparison Chart

Quick reference guide for comparing all six models in the Performance Metrics System.

## Performance Matrix

| Metric | XGBoost | LightGBM | Random Forest | Neural Network | SVM | K-Map | Ensemble |
|--------|---------|----------|---------------|----------------|-----|-------|----------|
| **Accuracy** | 94-96% | 93-95% | 91-93% | 89-92% | 88-91% | 78-85% | **92-96%** |
| **Training Time** | 30-40s | 20-30s | 15-25s | 40-60s | 50-70s | <1s | ~120s |
| **Prediction Time** | 20-30ms | 15-20ms | 15-25ms | 10-15ms | 15-20ms | <1ms | 125ms |
| **Memory Usage** | 100-200MB | 50-100MB | 100-200MB | 10-20MB | 5-10MB | ~1KB | ~500MB |
| **Ensemble Weight** | 22% | 20% | 18% | 16% | 16% | 8% | 100% |

## Strengths & Weaknesses Quick Reference

### XGBoost
```
✅ Strengths:
  • Highest accuracy (94-96%)
  • Excellent feature importance
  • Handles non-linearity well
  • Robust to outliers
  • Built-in regularization

❌ Weaknesses:
  • Memory intensive
  • Slower training
  • Many hyperparameters
  • Hard to interpret
  • Can overfit small data
```

### LightGBM
```
✅ Strengths:
  • Very fast training (fastest)
  • Memory efficient
  • High accuracy (93-95%)
  • Handles large datasets
  • Categorical support

❌ Weaknesses:
  • Can overfit small data (<500)
  • Sensitive to parameters
  • Less stable than RF
  • Newer/less tested
  • Complex trees
```

### Random Forest
```
✅ Strengths:
  • Easy to use
  • No overfitting
  • Parallel training
  • Handles missing data
  • Interpretable trees

❌ Weaknesses:
  • Memory heavy
  • Slower predictions
  • Lower accuracy (91-93%)
  • Bias to majority class
  • Many trees needed
```

### Neural Network
```
✅ Strengths:
  • Learns complex patterns
  • Feature learning
  • Flexible architecture
  • Good for large data
  • Continuous learning

❌ Weaknesses:
  • Requires scaling
  • Black box
  • Training instability
  • Many hyperparameters
  • Needs more data
```

### Support Vector Machine
```
✅ Strengths:
  • Works in high dimensions
  • Memory efficient
  • Multiple kernels
  • Handles imbalance
  • Strong theory

❌ Weaknesses:
  • Requires scaling
  • Slow with large data
  • Hard to interpret
  • Sensitive to noise
  • Kernel selection tricky
```

### K-Map Rule Engine
```
✅ Strengths:
  • Completely interpretable
  • Very fast predictions
  • No hyperparameters
  • Works with small data
  • Deterministic

❌ Weaknesses:
  • Lower accuracy (78-85%)
  • Coarse discretization
  • Limited patterns (16)
  • No interpolation
  • Simple logic
```

## Use Case Decision Tree

```
Need interpretability?
│
├─ YES → K-Map (rules) or Random Forest (trees)
│
└─ NO → Continue
          │
          Need maximum accuracy?
          │
          ├─ YES → XGBoost or LightGBM
          │
          └─ NO → Continue
                    │
                    Have large dataset (>10K)?
                    │
                    ├─ YES → LightGBM or Neural Network
                    │
                    └─ NO → Continue
                              │
                              Limited memory?
                              │
                              ├─ YES → SVM or K-Map
                              │
                              └─ NO → Use Ensemble (recommended)
```

## Best For...

| Scenario | Best Model | Why? |
|----------|------------|------|
| Maximum accuracy | **XGBoost** | Highest individual accuracy (94-96%) |
| Fastest training | **K-Map** | <1 second training time |
| Fastest prediction | **K-Map** | <1ms per prediction |
| Large datasets | **LightGBM** | Handles millions of samples efficiently |
| Interpretability | **K-Map** | Clear if-then rules |
| Stability | **Random Forest** | Most robust to noise |
| Small data | **Random Forest** | Works well with 100+ samples |
| Complex patterns | **Neural Network** | Learns intricate relationships |
| High dimensions | **SVM** | Effective in high-dim spaces |
| Production | **Ensemble** | Best balance of all factors |

## Feature Requirements

| Model | Feature Scaling | Missing Data | Categorical | High Dimensions |
|-------|----------------|--------------|-------------|-----------------|
| XGBoost | ❌ Not needed | ✅ Handles | ⚠️ Encode | ✅ Good |
| LightGBM | ❌ Not needed | ✅ Handles | ✅ Native | ✅ Good |
| Random Forest | ❌ Not needed | ✅ Handles | ⚠️ Encode | ⚠️ Moderate |
| Neural Network | ✅ **Required** | ❌ Must impute | ⚠️ Encode | ✅ Excellent |
| SVM | ✅ **Required** | ❌ Must impute | ⚠️ Encode | ✅ Excellent |
| K-Map | ❌ Not needed | ✅ Handles | ✅ Native | ❌ Limited |

## Hyperparameter Sensitivity

```
Low Sensitivity (Easy to tune):
  ████████░░ Random Forest
  ███████░░░ K-Map
  ██████░░░░ LightGBM

Medium Sensitivity:
  ████████░░ XGBoost
  ██████░░░░ SVM

High Sensitivity (Hard to tune):
  █████████░ Neural Network
```

## Training Data Requirements

| Model | Minimum Samples | Recommended Samples | Maximum Efficient Size |
|-------|----------------|---------------------|------------------------|
| K-Map | 50 | 200+ | Unlimited |
| Random Forest | 100 | 500+ | 100K |
| SVM | 50 | 500-5K | 10K |
| XGBoost | 200 | 1K+ | 1M+ |
| LightGBM | 500 | 5K+ | 10M+ |
| Neural Network | 500 | 2K+ | Unlimited |

## When NOT to Use Each Model

### ❌ Don't Use XGBoost If:
- You have <200 training samples
- Memory is very limited (<100MB)
- Need instant training (<10 seconds)
- Must have perfect interpretability

### ❌ Don't Use LightGBM If:
- You have <500 training samples
- Data has very few features (<5)
- Need maximum stability
- Cannot tune hyperparameters

### ❌ Don't Use Random Forest If:
- Memory is very limited
- Need maximum accuracy
- Have millions of samples
- Prediction speed is critical

### ❌ Don't Use Neural Network If:
- You have <500 samples
- Cannot scale features
- Need interpretability
- Want deterministic results
- Limited training time

### ❌ Don't Use SVM If:
- You have >10K samples
- Cannot scale features
- Need very fast training
- Need feature importance
- Want probability estimates

### ❌ Don't Use K-Map If:
- You need >90% accuracy
- Have continuous relationships
- Need smooth predictions
- Cannot define binary rules

## Ensemble Configuration

### Why These Weights?

```python
Default Weights:
{
    'xgboost': 0.22,        # Highest accuracy
    'lightgbm': 0.20,       # Fast + accurate
    'random_forest': 0.18,  # Stable
    'neural_network': 0.16, # Complex patterns
    'svm': 0.16,           # Good boundaries
    'kmap': 0.08           # Interpretable baseline
}
```

**Rationale:**
1. XGBoost gets highest weight due to best individual performance
2. LightGBM second due to speed + accuracy
3. Random Forest for stability
4. Neural Network and SVM equal for diversity
5. K-Map lowest but still valuable for interpretability

### Custom Weight Scenarios

```python
# Scenario 1: Favor accuracy over everything
{
    'xgboost': 0.35,
    'lightgbm': 0.30,
    'random_forest': 0.15,
    'neural_network': 0.10,
    'svm': 0.10,
    'kmap': 0.00
}

# Scenario 2: Favor interpretability
{
    'xgboost': 0.15,
    'lightgbm': 0.15,
    'random_forest': 0.30,
    'neural_network': 0.05,
    'svm': 0.10,
    'kmap': 0.25
}

# Scenario 3: Balanced diversity
{
    'xgboost': 0.18,
    'lightgbm': 0.18,
    'random_forest': 0.18,
    'neural_network': 0.16,
    'svm': 0.16,
    'kmap': 0.14
}
```

## Resource Requirements Comparison

### CPU Usage (Training)

```
High CPU:
  ████████████ Neural Network (multi-core)
  ██████████░░ Random Forest (parallel)
  ████████░░░░ XGBoost (partial parallel)

Medium CPU:
  ██████░░░░░░ LightGBM
  ████░░░░░░░░ SVM

Low CPU:
  ██░░░░░░░░░░ K-Map
```

### Memory Usage (Training)

```
High Memory:
  ████████████ Random Forest (many trees)
  ████████████ XGBoost (many trees)
  ████████░░░░ LightGBM (efficient trees)

Medium Memory:
  ██████░░░░░░ Neural Network (weights)
  ████░░░░░░░░ SVM (kernel matrix)

Low Memory:
  █░░░░░░░░░░░ K-Map (lookup table)
```

### Disk Storage (Model Size)

```
Large (>100MB):
  ████████████ Random Forest
  ████████████ XGBoost
  ████████░░░░ LightGBM

Medium (10-100MB):
  ██████░░░░░░ Neural Network
  ████░░░░░░░░ SVM

Small (<10MB):
  █░░░░░░░░░░░ K-Map
```

## Summary Recommendations

| Priority | Recommended Model(s) | Why? |
|----------|---------------------|------|
| **Best Overall** | **Ensemble (All 6)** | Maximizes accuracy and robustness |
| Single Best | XGBoost | Highest individual accuracy |
| Speed Priority | K-Map or LightGBM | K-Map for prediction, LightGBM for training |
| Memory Priority | K-Map or SVM | Minimal memory footprint |
| Interpretability | K-Map + Random Forest | Clear rules and tree visualization |
| Large Scale | LightGBM | Designed for big data |
| Robustness | Random Forest | Most stable across datasets |
| Complex Patterns | Neural Network + XGBoost | Best at learning intricate relationships |

## Quick Selection Guide

**Answer these questions:**

1. **Do you need >95% accuracy?**
   - YES → Use Ensemble or XGBoost
   - NO → Continue

2. **Is training time critical (<30s)?**
   - YES → Use LightGBM or Random Forest
   - NO → Continue

3. **Is memory limited (<50MB)?**
   - YES → Use SVM or K-Map
   - NO → Continue

4. **Must explain predictions?**
   - YES → Use K-Map or Random Forest
   - NO → Continue

5. **Have >10K training samples?**
   - YES → Use LightGBM or Neural Network
   - NO → Use XGBoost or Random Forest

**If none of the above apply strongly:**
→ **Use the Ensemble (recommended for production)**

---

**For detailed model information, see:** [MODELS_DETAILED_GUIDE.md](MODELS_DETAILED_GUIDE.md)

**Last Updated**: 2024-10-11
