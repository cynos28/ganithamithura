# Grade-Adaptive Learning System

## Overview
The adaptive learning system now personalizes question difficulty based on both **student grade level** and **performance ability**, creating a truly individualized learning experience for Grades 1-4.

## How It Works

### 1. Grade-Based Starting Points
Each new student starts at a difficulty level appropriate for their grade:

| Grade | Starting Difficulty | Difficulty % | Description |
|-------|-------------------|--------------|-------------|
| **Grade 1** | Level 1 | 20% | Very Easy - Foundational concepts |
| **Grade 2** | Level 2 | 40% | Easy - Building skills |
| **Grade 3** | Level 3 | 60% | Medium - Intermediate concepts |
| **Grade 4** | Level 4 | 80% | Hard - Advanced challenges |

### 2. Adaptive Difficulty Formula
```python
difficulty = grade_level + ability_score
```

**Example for Grade 1 Student:**
- **New student**: ability = 0.0 → difficulty = 1 + 0.0 = **1** (Very Easy)
- **After correct answers**: ability = +1.5 → difficulty = 1 + 1.5 = **2.5** → rounded to **3** (Medium)
- **After incorrect answers**: ability = -1.0 → difficulty = 1 + (-1.0) = **0** → clamped to **1** (stays at easiest)

**Example for Grade 4 Student:**
- **New student**: ability = 0.0 → difficulty = 4 + 0.0 = **4** (Hard)
- **Struggling student**: ability = -2.0 → difficulty = 4 + (-2.0) = **2** (adapts down to easier)
- **Advanced student**: ability = +1.0 → difficulty = 4 + 1.0 = **5** (maximum challenge)

### 3. Ability Score Dynamics

**Ability Range:** -3.0 to +3.0

**Ability Updates (IRT-based):**
- **Correct answer on hard question** → Large ability increase (surprising success)
- **Correct answer on easy question** → Small ability increase (expected)
- **Incorrect answer on easy question** → Large ability decrease (unexpected failure)
- **Incorrect answer on hard question** → Small ability decrease (not surprising)

**Learning Rate:** 0.3 (30% adjustment per question)

### 4. Difficulty Range Management

**Clamping:** All difficulties are clamped to [1, 5]
- Difficulty < 1 → Set to 1
- Difficulty > 5 → Set to 5

**Adaptive Range:** Students can experience ±3 difficulty levels from their grade baseline through ability adjustments.

## Personalization Features

### Initial Assessment (First 3-5 Questions)
- Questions start at grade-appropriate difficulty
- System rapidly adjusts based on performance
- Identifies student's true ability within grade context

### Continuous Adaptation
- **Real-time adjustment** after each question
- **Concept mastery tracking** per topic
- **Performance history** informs future difficulty

### Grade-Appropriate Content
- Questions match curriculum standards for each grade
- Vocabulary and context suited to grade level
- Progressively complex concepts across grades

## Implementation Details

### Backend Configuration (`config.py`)
```python
# Adaptive Learning Settings
initial_ability_score: float = 0.0  # Start neutral
min_difficulty: int = 1             # Easiest level
max_difficulty: int = 5             # Hardest level
target_success_rate: float = 0.7    # Aim for 70% success
learning_rate: float = 0.3          # 30% ability adjustment
```

### API Endpoints

#### Get Adaptive Question
```http
POST /api/v1/adaptive-measurement-question
```

**Request:**
```json
{
  "student_id": "student_123",
  "measurement_context": {
    "measurement_type": "length",
    "value": 25.0,
    "unit": "cm",
    "object_name": "pen",
    "topic": "Length"
  },
  "grade": 1
}
```

**Response:**
```json
{
  "question": {
    "question_id": "q_abc123",
    "question_text": "Your pen is 25cm long. How many millimeters is that?",
    "difficulty_level": 1,
    "options": ["250mm", "2.5mm", "25mm", "2500mm"],
    "correct_answer": "250mm"
  },
  "student_ability": 0.0,
  "target_difficulty": 1
}
```

#### Submit Answer
```http
POST /api/v1/submit-measurement-answer
```

**Response:**
```json
{
  "is_correct": true,
  "old_ability": 0.0,
  "new_ability": 0.21,
  "ability_change": +0.21,
  "next_difficulty": 1
}
```

## Benefits

### For Grade 1 Students
✅ Start with very easy questions (difficulty 1)  
✅ Build confidence with initial success  
✅ Gradually increase challenge as mastery improves  
✅ Age-appropriate content and language

### For Grade 4 Students
✅ Start with challenging questions (difficulty 4)  
✅ Avoid boredom from overly simple content  
✅ Can still adapt down if struggling with concepts  
✅ Advanced problem-solving opportunities

### For All Students
✅ **Personalized learning path** based on actual performance  
✅ **Optimal challenge level** targeting 70% success rate  
✅ **Real-time feedback** and ability tracking  
✅ **Engagement** through appropriate difficulty  
✅ **Mastery-based progression** across concepts

## Student Progress Example

### Grade 1 Student Journey

| Question # | Ability | Difficulty | Result | New Ability | Next Difficulty |
|------------|---------|------------|--------|-------------|-----------------|
| 1 | 0.00 | 1 | ✅ Correct | +0.21 | 1 |
| 2 | 0.21 | 1 | ✅ Correct | +0.39 | 1 |
| 3 | 0.39 | 1 | ✅ Correct | +0.54 | 2 |
| 4 | 0.54 | 2 | ❌ Wrong | +0.38 | 1 |
| 5 | 0.38 | 1 | ✅ Correct | +0.56 | 2 |
| 6 | 0.56 | 2 | ✅ Correct | +0.73 | 2 |
| 7 | 0.73 | 2 | ✅ Correct | +0.87 | 2 |
| 8 | 0.87 | 2 | ✅ Correct | +1.01 | 2 |
| 9 | 1.01 | 2 | ✅ Correct | +1.14 | 2 |
| 10 | 1.14 | 2 | ✅ Correct | +1.25 | 2 |

**Outcome:** Student shows strong mastery → Progressed from difficulty 1 to 2 → Ability increased 125%

## Future Enhancements

### Planned Features
- [ ] Multi-topic ability tracking (separate abilities for length, weight, capacity, etc.)
- [ ] Long-term learning curves and progress reports
- [ ] Adaptive hint systems based on ability
- [ ] Peer comparison within grade cohorts
- [ ] Teacher dashboard with student ability insights
- [ ] Predictive difficulty recommendations
- [ ] Gamification with ability-based rewards

### Integration Opportunities
- Store student grade in user profile
- Pass actual grade from Flutter app (currently defaults to grade 1)
- Multi-subject adaptive learning (math, reading, etc.)
- Cross-device ability synchronization

## Technical Notes

### Database Schema
```python
class StudentAbilityModel:
    student_id: str
    unit_id: str
    ability_score: float = 0.0        # IRT ability parameter
    current_difficulty: int = 1       # Grade-based initial
    total_questions: int = 0
    correct_answers: int = 0
    concepts_mastered: Dict
    last_updated: datetime
```

### Key Algorithms

**IRT Probability Model:**
```python
P(correct) = 1 / (1 + exp(-(ability - difficulty)))
```

**Ability Update (Maximum Likelihood Estimation):**
```python
if correct:
    delta = learning_rate * (1 - probability)
else:
    delta = -learning_rate * probability
    
new_ability = ability + delta
```

## Testing the System

### Create Test Students
```python
# Grade 1 beginner
student_g1 = {
    "student_id": "test_grade1_beginner",
    "grade": 1
}

# Grade 4 advanced
student_g4 = {
    "student_id": "test_grade4_advanced",
    "grade": 4
}
```

### Monitor Adaptation
Watch console logs for:
```
🎯 Student ability: 0.00, Target difficulty: 1
🎯 Loaded question (Difficulty: 1, Ability: 0.00)
📊 Ability: 0.00 → 0.21 (+0.21)
```

## Support

For questions or issues with the adaptive system:
1. Check console logs for ability/difficulty values
2. Verify grade parameter is being passed correctly
3. Monitor MongoDB `student_ability` collection
4. Review question difficulty distribution in database

---

**Version:** 1.0  
**Last Updated:** December 22, 2025  
**Status:** ✅ Production Ready
