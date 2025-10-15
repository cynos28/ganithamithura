# How to Use the Performance Predictor

## Step-by-Step Guide

### Step 1: Install Dependencies (One-time setup)

```bash
pip install -r requirements.txt
```

This installs all required ML libraries (numpy, pandas, scikit-learn, xgboost, lightgbm, etc.)

### Step 2: Train the Models (One-time setup)

```bash
python scripts/train_performance_models.py --sample
```

This will:
- Generate 2000 sample student records
- Train 6 machine learning models
- Save models to `models/performance_metrics/`
- Take approximately 2-3 minutes

**You'll see output like:**
```
Training data: 2000 samples
✅ Data quality check passed
Training models...
✅ Training completed in 120.45 seconds
Overall Accuracy: 94.50%
```

### Step 3: Run the Interactive Predictor

```bash
python predict_performance.py
```

### Step 4: Enter Student Information

The script will prompt you for information **one by one**:

#### 4.1 Student ID
```
Student ID (e.g., student_123): mike_3421
```
Enter any unique identifier for the student.

#### 4.2 Average Score
```
📊 Average Score:
   The student's average performance score
Average Score (0-100): 75
```
Enter a number between 0 and 100.

#### 4.3 Average Time
```
⏱️  Average Time:
   Average time taken to complete tasks (in seconds)
Average Time (seconds): 65
```
Enter the average time in seconds (e.g., 65 means 65 seconds or about 1 minute).

#### 4.4 Grade Level
```
🎓 Grade Level:
   The student's current grade (1-3)
Grade Level (1-3): 2
```
Enter a grade from 1 to 3.

### Step 5: Review and Confirm

The script shows a summary:
```
INPUT SUMMARY
──────────────────────────────────────────────────────────────────────
  Student ID:     mike_3421
  Average Score:  75.0
  Average Time:   65.0 seconds
  Grade Level:    2

Proceed with prediction? (yes/no): yes
```

Type `yes` to continue.

### Step 6: View Results

The script displays detailed results:

```
PREDICTION RESULTS
──────────────────────────────────────────────────────────────────────

  🎯 CLASSIFICATION:
     Level:    Level 1 (Level 1)
     Sublevel: Explorer

  🟢 CONFIDENCE:
     Overall:  87.0% (High)
     Level:    69.0%
     Sublevel: 80.0%

  📊 LEVEL PROBABILITIES:
     Level 1: ████████████████████████████░░░░░░░░░░░░ 69.0%
     Level 2: ██████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 26.0%
     Level 3: ██░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 5.0%

  ⚡ PERFORMANCE:
     Efficiency Ratio:  1.15 pts/sec
     Score Percentile:  60th
     Prediction Time:   125.5ms

  💡 RECOMMENDATION:
     • Focus on speed improvement while maintaining accuracy
     • Continue building on your solid foundation
```

### Step 7: Understand the Results

**Level Classification:**
- **Level 1**: Beginning proficiency - Building foundations
- **Level 2**: Intermediate proficiency - Solid understanding
- **Level 3**: Advanced proficiency - Exceptional mastery

**Sublevel Classification:**
- **Starter**: Initial learning phase
- **Explorer**: Developing skills
- **Solver**: Competent problem-solving
- **Champion**: Exceptional performance

**Confidence Levels:**
- 🟢 **High** (>80%): Very reliable prediction
- 🟡 **Medium** (60-80%): Good prediction with some uncertainty
- 🔴 **Low** (<60%): Prediction has higher uncertainty

### Step 8: Make More Predictions (Optional)

After viewing results, you can:
- Type `yes` to predict for another student
- Type `no` to exit

## Example Complete Session

```bash
$ python predict_performance.py

======================================================================
  STUDENT PERFORMANCE LEVEL PREDICTOR
  Advanced ML-based Classification System
======================================================================

  🔄 Loading trained models...
  ✅ Models loaded successfully!

──────────────────────────────────────────────────────────────────────
  STUDENT DATA INPUT
──────────────────────────────────────────────────────────────────────
  Please provide the following information:
  (Type 'quit' at any time to exit)

  Student ID (e.g., student_123): alice_100

  📊 Average Score:
     The student's average performance score
  Average Score (0-100): 92

  ⏱️  Average Time:
     Average time taken to complete tasks (in seconds)
  Average Time (seconds): 35

  🎓 Grade Level:
     The student's current grade (1-3)
  Grade Level (1-3): 3

──────────────────────────────────────────────────────────────────────
  INPUT SUMMARY
──────────────────────────────────────────────────────────────────────
  Student ID:     alice_100
  Average Score:  92.0
  Average Time:   35.0 seconds
  Grade Level:    3

  Proceed with prediction? (yes/no): yes

  🔮 Analyzing student performance...

──────────────────────────────────────────────────────────────────────
  PREDICTION RESULTS
──────────────────────────────────────────────────────────────────────

  🎯 CLASSIFICATION:
     Level:    Level 3 (Level 3)
     Sublevel: Champion

  🟢 CONFIDENCE:
     Overall:  95.2% (High)
     Level:    94.5%
     Sublevel: 90.0%

  📊 LEVEL PROBABILITIES:
     Level 1: ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 2.0%
     Level 2: ████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 10.0%
     Level 3: ████████████████████████████████████████ 88.0%

  ⚡ PERFORMANCE:
     Efficiency Ratio:  2.63 pts/sec
     Score Percentile:  95th
     Prediction Time:   118.2ms

  💡 RECOMMENDATION:
     • Excellent work! Challenge yourself with advanced problems
     • Keep up the exceptional performance

  Would you like to see the level guide? (yes/no): no

  Would you like to predict for another student? (yes/no): no

======================================================================
  Thank you for using the Performance Predictor!
  For more information, see: QUICK_START.md
======================================================================
```

## Tips

1. **Quick Exit**: Type `quit`, `exit`, or `q` at any prompt to exit
2. **Invalid Input**: If you enter invalid data, the script will ask again
3. **Multiple Students**: You can predict for as many students as you want in one session
4. **View Guide**: Answer `yes` when asked to see the level guide for detailed explanations

## Troubleshooting

**Error: Model directory not found**
- Solution: Run the training script first: `python scripts/train_performance_models.py --sample`

**Error: Invalid input**
- Make sure scores are between 0-100
- Make sure times are positive numbers
- Make sure grades are between 1-3

**Import errors**
- Solution: Install dependencies: `pip install -r requirements.txt`

## What Happens Behind the Scenes?

When you enter student data:

1. **Feature Engineering**: System creates 15-20 advanced features from your input
2. **Model Ensemble**: 6 different ML models analyze the data:
   - XGBoost
   - Random Forest
   - Neural Network
   - Support Vector Machine
   - LightGBM
   - K-Map Rule Engine
3. **Decision Fusion**: Results are combined with weighted voting
4. **Confidence Assessment**: System checks model agreement
5. **Validation**: Logical consistency checks are performed
6. **Recommendation**: Personalized advice is generated

All in under 150 milliseconds!

## Next Steps

- See **[QUICK_START.md](QUICK_START.md)** for programmatic usage
- See **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** for technical details
- See **[src/performance_metrics/README.md](src/performance_metrics/README.md)** for API documentation

---

**Need Help?** Check the documentation or review the example file: `examples/performance_metrics_example.py`
