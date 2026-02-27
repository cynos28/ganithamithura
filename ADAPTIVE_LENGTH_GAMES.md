# Adaptive Length Game Integration

Complete backend-frontend integration for all 4 length game variants with adaptive difficulty.

## 🎮 Game Variants

### **L-V1: Ruler Explorer** 🔍
- **Concept**: Drag object to ruler, measure its length
- **Adaptive Parameters**:
  - `object_size_range`: [5, 15] cm → Objects get smaller/larger based on performance
  - `choice_spread`: 3 → Wrong answers get closer/farther (±1-5 cm)
  - `hints`: 2 → Decreases to 0 or increases to 3

### **L-V2: Compare** ⚖️
- **Concept**: Compare two objects, which is longer?
- **Adaptive Parameters**:
  - `object_size_range`: [5, 20] cm → Object sizes adapt
  - `min_size_difference`: 3 cm → Objects become more/less similar
  - `hints`: 2 → Adjusts 0-3

### **L-V3: Calculate & Win** 🧮
- **Concept**: Convert mm/m to cm
- **Adaptive Parameters**:
  - `allow_decimals`: false → Enables harder decimal conversions
  - `value_range_mm`: [30, 150] → Adjusts to [50, 250] for harder mode
  - `value_range_m`: [0.05, 0.25] → Adjusts to [0.15, 0.45] for harder mode
  - `choice_spread`: 3 → Wrong answers adapt
  - `hints`: 2 → Adjusts 0-3

### **L-V4: Build a Bridge** 🌉
- **Concept**: Combine planks to reach target bridge length
- **Adaptive Parameters**:
  - `bridge_target_range`: [10, 18] cm → Longer/shorter bridges [8-25 cm]
  - `plank_sizes`: [3,4,5,6,7,8,9] → More variety [2-8] or simpler [3,5,7,9]
  - `plank_count`: 7 → More/fewer plank options (5-10)
  - `hints`: 2 → Adjusts 0-3

---

## 📊 Adaptive Logic Flow

```
Student Plays Game Session
         ↓
Backend Evaluates Performance
(attempts, time, hints used)
         ↓
Diagnosis: INCREASE / MAINTAIN / DECREASE
         ↓
Variant-Specific Parameter Adjustment
         ↓
Updated Params Saved to Database
         ↓
Next Game Uses New Parameters
```

---

## 🔧 Backend Files Modified

### 1. **`unit-rag-service/app/utils/game_domain_adapter.py`**
```python
def adjust_length_params(diagnosis, params):
    """Routes to variant-specific adjustment functions."""
    variant = params.get("current_variant", "L-V1")
    
    if variant == "L-V1":
        return _adjust_v1_params(diagnosis, params)
    elif variant == "L-V2":
        return _adjust_v2_params(diagnosis, params)
    # ... etc
```

**New Functions**:
- `_adjust_v1_params()` - Ruler Explorer adjustments
- `_adjust_v2_params()` - Compare adjustments
- `_adjust_v3_params()` - Calculate & Win adjustments
- `_adjust_v4_params()` - Bridge adjustments

### 2. **`gmfrontend/lib/services/api/games_api_service.dart`**
Updated default parameters to include all variant-specific fields:
```dart
'object_size_range': [5, 15],
'min_size_difference': 3,
'allow_decimals': false,
'bridge_target_range': [10, 18],
'plank_sizes': [3, 4, 5, 6, 7, 8, 9],
// ... etc
```

### 3. **`gmfrontend/lib/screens/measurements/games/length_game_play_screen.dart`**
Updated all `_genV1()`, `_genV2()`, `_genV3()`, `_genV4()` functions to:
- Read parameters from `_params` map
- Apply backend-provided ranges/settings
- Generate game content adaptively

---

## 🚀 Setup Instructions

### Backend Setup

1. **Initialize Database Parameters**:
```bash
cd unit-rag-service
python scripts/init_length_game_params.py
```

2. **Verify Parameters**:
```bash
# Check MongoDB
mongosh ganithamithura
db.game_parameters.find({"domain": "length"}).pretty()
```

### Frontend

No setup needed - automatically fetches parameters from backend on game start.

**Fallback**: If backend is offline, uses default parameters from `GamesApiService._defaultParams()`.

---

## 📈 Difficulty Progression Examples

### V1 (Ruler Explorer)
| Diagnosis | object_size_range | choice_spread | Effect |
|-----------|-------------------|---------------|--------|
| Initial   | [5, 15]          | 3             | Medium objects, ±3 cm choices |
| INCREASE  | [4, 12]          | 2             | Smaller objects, closer choices |
| DECREASE  | [6, 18]          | 4             | Larger objects, farther choices |

### V4 (Bridge)
| Diagnosis | bridge_target | plank_sizes | plank_count | Effect |
|-----------|---------------|-------------|-------------|--------|
| Initial   | [10, 18]     | [3,4,5,6,7,8,9] | 7 | Medium difficulty |
| INCREASE  | [15, 25]     | [2,3,4,5,6,7,8] | 8 | Longer bridge, more small planks |
| DECREASE  | [8, 14]      | [3,5,7,9]       | 5 | Shorter bridge, fewer simple planks |

---

## 🧪 Testing

### Test Parameter Adaptation

1. Play a game very well (1 attempt, fast time, no hints)
   - Should get INCREASE diagnosis
   - Next round should be harder

2. Play poorly (many attempts, slow, use hints)
   - Should get DECREASE diagnosis
   - Next round should be easier

3. Check logs:
```bash
# Backend logs
tail -f unit-rag-service/logs/app.log

# Look for:
# "📈 Increasing difficulty: L-V1 → L-V2"
# "📉 Decreasing difficulty: L-V3 → L-V2"
# "➡️ Maintaining difficulty: L-V2"
```

---

## 🎯 Success Criteria

✅ **Session Tracking**: Attempts, time, hints uploaded after each game
✅ **Variant Progression**: L-V1 → L-V2 → L-V3 → L-V4 based on 60% pass threshold
✅ **Parameter Adaptation**: Within-variant difficulty adjusts based on performance
✅ **Offline Fallback**: Works with default params when backend unavailable
✅ **All Variants Covered**: V1, V2, V3, V4 all have adaptive parameters

---

## 📝 API Endpoints Used

- **GET** `/adaptive-games/parameters/length` - Fetch current parameters
- **POST** `/adaptive-games/evaluate` - Submit session & get updated params

Response example:
```json
{
  "diagnosis": "increase",
  "new_params": {
    "current_variant": "L-V2",
    "hints": 1,
    "object_size_range": [4, 12],
    "min_size_difference": 2,
    ...
  }
}
```

---

## 🔄 Future Enhancements

- [ ] Student-specific parameter tracking (currently shared across all users)
- [ ] Time-of-day adaptive difficulty (easier in morning, harder in afternoon)
- [ ] Learning curve prediction (ML model to optimize param changes)
- [ ] A/B testing different parameter ranges
- [ ] Dashboard to visualize parameter evolution over time
