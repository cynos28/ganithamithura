# Adaptive Learning System Documentation

## Overview

The Ganithamithura app uses an **adaptive learning system** based on **Item Response Theory (IRT)** to personalize question difficulty for each student. The system automatically adjusts question difficulty based on student performance, ensuring optimal learning challenge.

---

## 🎯 Core Components

### 1. Student Ability Score
- **Range**: -3.0 to +3.0
- **Starting Value**: 0.0 (neutral)
- **Meaning**: 
  - Negative scores = Below grade level
  - 0.0 = At grade level
  - Positive scores = Above grade level

### 2. Question Difficulty Levels
- **Range**: 1 to 5 stars (⭐ to ⭐⭐⭐⭐⭐)
- **Level 1**: Very Easy (Basic concepts)
- **Level 2**: Easy (Simple application)
- **Level 3**: Medium (Standard problems)
- **Level 4**: Hard (Complex problems)
- **Level 5**: Very Hard (Advanced challenges)

### 3. Grade Level
- **Range**: Grade 1 to Grade 5
- **Purpose**: Sets the baseline difficulty expectations
- Students at different grades have different starting difficulty levels

---

## 📐 How It Works

### Difficulty Selection Formula

```
Target Difficulty = round(Grade Level + Ability Score)
```

#### Examples for Grade 1 Student:

| Ability Score | Calculation | Target Difficulty | Level |
|--------------|-------------|-------------------|-------|
| -1.5 | 1 + (-1.5) = -0.5 | 1 (min) | ⭐ |
| 0.0 | 1 + 0.0 = 1.0 | 1 | ⭐ |
| 0.3 | 1 + 0.3 = 1.3 | 1 | ⭐ |
| 0.5 | 1 + 0.5 = 1.5 | 2 | ⭐⭐ |
| 1.0 | 1 + 1.0 = 2.0 | 2 | ⭐⭐ |
| 1.5 | 1 + 1.5 = 2.5 | 3 | ⭐⭐⭐ |
| 2.0 | 1 + 2.0 = 3.0 | 3 | ⭐⭐⭐ |
| 2.5 | 1 + 2.5 = 3.5 | 4 | ⭐⭐⭐⭐ |
| 3.0 | 1 + 3.0 = 4.0 | 4 | ⭐⭐⭐⭐ |

#### Examples for Grade 3 Student:

| Ability Score | Calculation | Target Difficulty | Level |
|--------------|-------------|-------------------|-------|
| -2.0 | 3 + (-2.0) = 1.0 | 1 | ⭐ |
| -1.0 | 3 + (-1.0) = 2.0 | 2 | ⭐⭐ |
| 0.0 | 3 + 0.0 = 3.0 | 3 | ⭐⭐⭐ |
| 0.5 | 3 + 0.5 = 3.5 | 4 | ⭐⭐⭐⭐ |
| 1.0 | 3 + 1.0 = 4.0 | 4 | ⭐⭐⭐⭐ |
| 2.0 | 3 + 2.0 = 5.0 | 5 | ⭐⭐⭐⭐⭐ |

---

## 🔄 Ability Update Mechanism

### IRT 1-Parameter Logistic Model (Rasch Model)

The system uses the **probability function**:

```
P(correct) = 1 / (1 + e^(-(ability - difficulty)))
```

### Ability Update Formula

When a student answers a question:

```python
if correct:
    ability_change = learning_rate × (1 - probability_correct)
else:
    ability_change = -learning_rate × probability_correct
```

Where:
- **Learning Rate**: 0.3 (configurable)
- **Probability**: Calculated based on current ability vs question difficulty

### How Much Does Ability Change?

#### At Ability = 0.0, Difficulty = 1:

**Correct Answer:**
- Probability = 1/(1 + e^(-(0-1))) = 0.27 (27% expected success)
- Change = 0.3 × (1 - 0.27) = **+0.22**
- New Ability = 0.0 + 0.22 = **0.22**

**Wrong Answer:**
- Change = -0.3 × 0.27 = **-0.08**
- New Ability = 0.0 - 0.08 = **-0.08**

#### At Ability = 1.0, Difficulty = 2:

**Correct Answer:**
- Probability = 1/(1 + e^(-(1-2))) = 0.27
- Change = 0.3 × (1 - 0.27) = **+0.22**
- New Ability = 1.0 + 0.22 = **1.22**

**Wrong Answer:**
- Change = -0.3 × 0.27 = **-0.08**
- New Ability = 1.0 - 0.08 = **0.92**

---

## 📈 Progression Path

### Grade 1 Student Progression Example

Starting at **Ability 0.0**, **Difficulty 1**:

| Question # | Answer | Old Ability | Change | New Ability | Next Difficulty |
|-----------|--------|-------------|--------|-------------|----------------|
| 1 | ✅ Correct | 0.00 | +0.22 | 0.22 | 1 ⭐ |
| 2 | ✅ Correct | 0.22 | +0.19 | 0.41 | 1 ⭐ |
| 3 | ✅ Correct | 0.41 | +0.17 | 0.58 | **2 ⭐⭐** |
| 4 | ✅ Correct | 0.58 | +0.13 | 0.71 | 2 ⭐⭐ |
| 5 | ✅ Correct | 0.71 | +0.11 | 0.82 | 2 ⭐⭐ |
| 6 | ✅ Correct | 0.82 | +0.09 | 0.91 | 2 ⭐⭐ |
| 7 | ✅ Correct | 0.91 | +0.08 | 0.99 | 2 ⭐⭐ |
| 8 | ✅ Correct | 0.99 | +0.07 | 1.06 | 2 ⭐⭐ |
| 9 | ✅ Correct | 1.06 | +0.06 | 1.12 | 2 ⭐⭐ |
| 10 | ✅ Correct | 1.12 | +0.05 | 1.17 | 2 ⭐⭐ |
| 11 | ✅ Correct | 1.17 | +0.04 | 1.21 | 2 ⭐⭐ |
| 12 | ✅ Correct | 1.21 | +0.04 | 1.25 | 2 ⭐⭐ |
| 13 | ✅ Correct | 1.25 | +0.03 | 1.28 | 2 ⭐⭐ |
| 14 | ✅ Correct | 1.28 | +0.03 | 1.31 | 2 ⭐⭐ |
| 15 | ✅ Correct | 1.31 | +0.03 | 1.34 | 2 ⭐⭐ |
| 16 | ✅ Correct | 1.34 | +0.03 | 1.37 | 2 ⭐⭐ |
| 17 | ✅ Correct | 1.37 | +0.02 | 1.39 | 2 ⭐⭐ |
| 18 | ✅ Correct | 1.39 | +0.02 | 1.41 | 2 ⭐⭐ |
| 19 | ✅ Correct | 1.41 | +0.02 | 1.43 | 2 ⭐⭐ |
| 20 | ✅ Correct | 1.43 | +0.02 | 1.45 | 2 ⭐⭐ |
| 21 | ✅ Correct | 1.45 | +0.02 | 1.47 | 2 ⭐⭐ |
| 22 | ✅ Correct | 1.47 | +0.02 | 1.49 | 2 ⭐⭐ |
| 23 | ✅ Correct | 1.49 | +0.02 | 1.51 | **3 ⭐⭐⭐** |

### With Mixed Results:

| Question # | Answer | Old Ability | Change | New Ability | Next Difficulty |
|-----------|--------|-------------|--------|-------------|----------------|
| 1 | ✅ Correct | 0.00 | +0.22 | 0.22 | 1 ⭐ |
| 2 | ❌ Wrong | 0.22 | -0.09 | 0.13 | 1 ⭐ |
| 3 | ✅ Correct | 0.13 | +0.21 | 0.34 | 1 ⭐ |
| 4 | ✅ Correct | 0.34 | +0.18 | 0.52 | **2 ⭐⭐** |
| 5 | ❌ Wrong | 0.52 | -0.08 | 0.44 | 1 ⭐ |
| 6 | ✅ Correct | 0.44 | +0.17 | 0.61 | **2 ⭐⭐** |

---

## 🎚️ Difficulty Thresholds

### For Grade 1 Students:

| Difficulty Level | Ability Range Required | Stars |
|-----------------|----------------------|-------|
| 1 (Very Easy) | -∞ to 0.49 | ⭐ |
| 2 (Easy) | 0.50 to 1.49 | ⭐⭐ |
| 3 (Medium) | 1.50 to 2.49 | ⭐⭐⭐ |
| 4 (Hard) | 2.50 to 3.00 | ⭐⭐⭐⭐ |
| 5 (Very Hard) | Never reached | ⭐⭐⭐⭐⭐ |

### For Grade 3 Students:

| Difficulty Level | Ability Range Required | Stars |
|-----------------|----------------------|-------|
| 1 (Very Easy) | -∞ to -1.51 | ⭐ |
| 2 (Easy) | -1.50 to -0.51 | ⭐⭐ |
| 3 (Medium) | -0.50 to 0.49 | ⭐⭐⭐ |
| 4 (Hard) | 0.50 to 1.49 | ⭐⭐⭐⭐ |
| 5 (Very Hard) | 1.50 to 3.00 | ⭐⭐⭐⭐⭐ |

---

## ⚙️ Configuration Parameters

Located in `unit-rag-service/app/config.py`:

```python
# Adaptive Learning Parameters
min_difficulty: int = 1           # Minimum difficulty level
max_difficulty: int = 5           # Maximum difficulty level
target_success_rate: float = 0.7  # Target 70% success rate
learning_rate: float = 0.3        # How fast ability changes

# Starting Ability
initial_ability_score: float = 0.0  # All students start at 0
```

---

## 🔍 How to Track Progress

### In the App UI

The AR Questions Screen shows:
```
Level 2 • Ability: 0.5
```

### In Console Logs

**After Submitting an Answer:**
```
📊 Ability: 0.22 → 0.43 (+0.21)
🎚️ Next difficulty level: 1
```

**When Loading Next Question:**
```
🎯 Loaded question (Difficulty: 1, Ability: 0.43)
```

### In Backend Logs

**Difficulty Calculation:**
```
🎚️ Difficulty calc: grade=1 + ability=0.43 = 1.43 → 1
```

**Next Question Selection:**
```
🎯 Student ability: 0.43, Target difficulty: 1
```

---

## 📊 Database Schema

### Student Ability Record

```javascript
{
  student_id: "student_test_1704326400000",
  unit_id: "ar_length_1",
  ability_score: 0.43,
  current_difficulty: 1,
  concepts_mastered: {},
  created_at: "2026-01-03T10:30:00Z",
  updated_at: "2026-01-03T10:35:00Z"
}
```

### Answer Record

```javascript
{
  student_id: "student_test_1704326400000",
  question_id: "677777abc123def456",
  unit_id: "ar_length_1",
  answer_given: "75",
  is_correct: true,
  time_taken: 12,
  difficulty_at_attempt: 1,
  timestamp: "2026-01-03T10:35:00Z"
}
```

---

## 🎓 Benefits of This System

### 1. **Personalized Learning**
- Each student gets questions matched to their current ability
- No one is overwhelmed or bored

### 2. **Gradual Progression**
- Difficulty increases smoothly as skills improve
- Prevents frustration from sudden difficulty jumps

### 3. **Continuous Assessment**
- Real-time adaptation to student performance
- No need for separate placement tests

### 4. **Data-Driven**
- Based on proven IRT statistical model
- Used in major standardized tests (SAT, GRE, etc.)

### 5. **Motivating**
- Students see their ability score increase
- Clear visual feedback on progress (stars)

---

## 🔬 Technical Implementation

### Backend (`unit-rag-service`)

**Files:**
- `app/services/adaptive_engine.py` - IRT calculations
- `app/routes/contextual.py` - API endpoints
- `app/models/database.py` - Data models

**Key Endpoints:**
- `POST /api/v1/contextual/adaptive-measurement-question` - Get next question
- `POST /api/v1/contextual/submit-measurement-answer` - Submit answer & update ability

### Frontend (`gmfrontend`)

**Files:**
- `lib/screens/measurements/ar_challenges/ar_questions_screen.dart` - UI
- `lib/services/api/contextual_question_service.dart` - API calls

**State Management:**
- `_studentAbility` - Current ability score
- `_currentDifficulty` - Current difficulty level
- Updates in real-time after each answer

---

## 🎯 Example Session Flow

1. **Student starts AR measurement**
   - Measures a 45cm pencil
   - System generates measurement context

2. **First question requested**
   - Student ID: `student_123`
   - Grade: 1
   - Initial ability: 0.0
   - System calculates: 1 + 0.0 = **Difficulty 1**

3. **Question presented**
   - "Your pencil is 45cm. How many centimeters is that?"
   - Options: [40, 45, 50, 55]

4. **Student answers correctly**
   - Ability updated: 0.0 → 0.22
   - Next difficulty: round(1 + 0.22) = **Difficulty 1**

5. **Second question requested**
   - Ability: 0.22
   - Difficulty: 1
   - Question: "If your 45cm pencil is cut in half, how long is each piece?"

6. **Student answers correctly again**
   - Ability updated: 0.22 → 0.41
   - Next difficulty: round(1 + 0.41) = **Difficulty 1**

7. **Third question requested**
   - After another correct answer
   - Ability: 0.58
   - Difficulty: round(1 + 0.58) = **Difficulty 2** ⭐⭐
   - Question becomes more challenging!

---

## 🛠️ Troubleshooting

### Issue: Difficulty Not Changing

**Check:**
1. Student ability score increasing? (Should see +0.2 per correct answer initially)
2. Ability near threshold? (Need 0.5+ for level 2)
3. Frontend receiving `next_difficulty` from backend?
4. UI updating with `setState`?

**Logs to verify:**
```
📊 Ability: 0.22 → 0.43 (+0.21)
🎚️ Next difficulty level: 1
🎚️ Difficulty calc: grade=1 + ability=0.43 = 1.43 → 1
```

### Issue: Ability Not Persisting

**Check:**
1. Same `student_id` used across requests?
2. Same `unit_id` format in get and submit endpoints?
   - Should be: `ar_{topic}_{grade}` (e.g., `ar_length_1`)
3. Database connection working?

---

## 📚 Further Reading

- **Item Response Theory**: [Wikipedia](https://en.wikipedia.org/wiki/Item_response_theory)
- **Rasch Model**: [Wikipedia](https://en.wikipedia.org/wiki/Rasch_model)
- **Adaptive Testing**: Research papers on CAT (Computerized Adaptive Testing)

---

## 📝 Summary

The adaptive system ensures each student gets:
- ✅ Questions at the right difficulty
- ✅ Steady, measurable progress
- ✅ Motivation through visible improvement
- ✅ Personalized learning experience

The formula `Difficulty = Grade + Ability` is simple but powerful, ensuring grade-appropriate challenges while adapting to individual student performance.
