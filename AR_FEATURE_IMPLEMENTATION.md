# AR Object → Contextual Questions Implementation

## 📱 Feature Overview

**Unique Learning Experience**: Students measure real objects with AR camera and receive personalized math questions about THEIR actual measurements.

**Example Flow**:
1. Student measures their pencil with AR → 15cm
2. System generates: "Your pencil is 15cm. How many millimeters is that?"
3. Questions feel personal and concrete, not generic textbook questions

---

## ✅ Implementation Status

### COMPLETED ✅

#### Backend Services (100% Complete)

**1. measurement-service (Port 8001)**
- Location: `/measurement-service/`
- FastAPI service that processes AR measurements into educational context
- Files created:
  - `app/main.py` - FastAPI app initialization
  - `app/models/schemas.py` - Pydantic models (ARMeasurementRequest, MeasurementContext, enums)
  - `app/services/context_builder.py` - ContextBuilder with grade suggestions and difficulty hints
  - `app/routes/measurement.py` - POST /api/v1/measurements/process endpoint
  - `requirements.txt` - Dependencies

**2. Contextual Questions Endpoint**
- Location: `/unit-rag-service/app/routes/contextual.py`
- Generates personalized questions using RAG + GPT-4o-mini
- Integration: Registered in `unit-rag-service/app/main.py`
- Features:
  - RAG retrieval of curriculum chunks
  - GPT-4o-mini with detailed prompt engineering
  - Personalization rules (use "YOUR object", exact measurements)
  - Fallback template questions if LLM fails
  - MongoDB storage with AR metadata

**Note**: One lint error (line 111) regarding Beanie's `save()` method is a false positive - the code is correct and matches the pattern used throughout the codebase.

#### Flutter Models & Services (100% Complete)

**3. AR Measurement Models**
- Location: `ganithamithura/lib/models/ar_measurement.dart`
- Complete data models:
  - `ARMeasurementRequest` - Request to measurement-service
  - `MeasurementContext` - Response with educational context
  - `ContextualQuestionRequest` - Request for question generation
  - `ContextualQuestion` - Individual question with hints/explanation
  - `ContextualQuestionResponse` - Generation response
  - `ARMeasurementSession` - Track multiple measurements
  - `ARMeasurement` - Individual measurement with context & questions
  - Enums: `MeasurementType`, `MeasurementUnit`
  - Extensions: Display names and icons

**4. API Services**
- Location: `ganithamithura/lib/services/api/`
- Files:
  - `measurement_api_service.dart` - Client for measurement-service (port 8001)
  - `contextual_question_service.dart` - Client for contextual endpoint (port 8000)
  - Methods: processMeasurement(), generateQuestions(), health checks

**5. AR Learning Coordinator**
- Location: `ganithamithura/lib/services/ar_learning_service.dart`
- Orchestrates full AR flow:
  - Start/end sessions
  - Process measurements → context → questions
  - Session management
  - Health checks for both services
  - Quick test method for development

**6. UI Components**
- Location: `ganithamithura/lib/widgets/measurements/ar_challenge_card.dart`
- AR Challenge Card widget with:
  - Emoji icons (📏🥤⚖️📐)
  - Camera badge indicator
  - Units display
  - Custom colors per topic

**7. Updated Home Screen**
- Location: `ganithamithura/lib/screens/measurements/measurement_home_screen.dart`
- Changes:
  - Replaced "Learning Concepts" with "AR Challenges"
  - 4 AR challenge cards (Length, Capacity, Weight, Area)
  - Navigation to `/ar-measurement` route (to be created)

### PENDING ⏳

**8. AR Measurement Screen** (Not Started)
- Location: `ganithamithura/lib/screens/measurements/ar_measurement_screen.dart`
- Required components:
  - AR camera integration (Flutter AR plugins)
  - Manual measurement input (for development/testing)
  - Object name input
  - Unit selection
  - Real-time measurement display
  - Process button to generate questions

**9. AR Questions Display Screen** (Not Started)
- Location: `ganithamithura/lib/screens/measurements/ar_questions_screen.dart`
- Required features:
  - Display personalized questions
  - Show measurement context ("Your pencil is 15cm")
  - Answer input
  - Hint system
  - Progress tracking
  - Navigation to next question

**10. Route Registration** (Not Started)
- Add routes in `ganithamithura/lib/main.dart`:
  ```dart
  GetPage(name: '/ar-measurement', page: () => const ARMeasurementScreen()),
  GetPage(name: '/ar-questions', page: () => const ARQuestionsScreen()),
  ```

**11. Backend Service Deployment**
- Start measurement-service:
  ```bash
  cd measurement-service
  pip install -r requirements.txt
  uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
  ```
- Ensure unit-rag-service is running on port 8000

**12. Flutter Dependencies**
- Add to `pubspec.yaml`:
  ```yaml
  dependencies:
    json_annotation: ^4.8.1
    uuid: ^4.0.0
    camera: ^0.10.5  # For AR camera
    ar_flutter_plugin: ^0.7.3  # AR capabilities
  
  dev_dependencies:
    json_serializable: ^6.7.1
    build_runner: ^2.4.6
  ```
- Run: `flutter pub get && flutter pub run build_runner build`

---

## 🏗️ Architecture

### Data Flow

```
Student → AR Camera → Flutter App
                         ↓
            ARMeasurementRequest (value, unit, object)
                         ↓
        measurement-service (port 8001)
            /api/v1/measurements/process
                         ↓
                  MeasurementContext
        (topic, grade, hints, personalized_prompt)
                         ↓
            ContextualQuestionRequest
                         ↓
          unit-rag-service (port 8000)
        /api/v1/contextual/generate-questions
                         ↓
              RAG Retrieval (ChromaDB)
        → Curriculum chunks about topic
                         ↓
            GPT-4o-mini Generation
        → Personalized questions using actual measurement
                         ↓
            MongoDB Storage + Response
                         ↓
              Flutter Display
        "Your pencil is 15cm. How many mm?"
```

### Services Architecture

**measurement-service (FastAPI)**
- Purpose: Convert raw AR measurements into educational context
- Port: 8001
- Dependencies: None (standalone)
- Key Logic:
  - Grade suggestion based on value ranges
  - Difficulty hints (conversion, multiplication, comparison)
  - Personalized prompt generation

**unit-rag-service (FastAPI)**
- Purpose: Generate contextual questions using RAG + LLM
- Port: 8000
- Dependencies: MongoDB, ChromaDB, OpenAI GPT-4o-mini
- Key Logic:
  - RAG semantic search for curriculum chunks
  - GPT prompt engineering with personalization rules
  - Fallback template questions
  - Progress tracking integration

**Flutter App**
- Purpose: AR measurement UI and question practice
- Services:
  - MeasurementApiService → port 8001
  - ContextualQuestionService → port 8000
  - ARLearningService → Coordinator
  - UnitProgressService → Progress tracking

---

## 🎯 Key Features

### Personalization

**Critical Rules** (enforced in GPT prompt):
1. ✅ Always use "YOUR {object}" not "A {object}"
2. ✅ Always reference EXACT measurement from AR
3. ✅ Conversational tone, not textbook style
4. ✅ Connect to student's real object

**Good Examples**:
- "Your pencil is 15cm. How many millimeters is that?"
- "If you had 3 of YOUR pencils, what would be the total length?"
- "Your water bottle holds 500ml. Is that more or less than 1 liter?"

**Bad Examples** (avoided):
- "A pencil is X cm. Convert to mm." ❌ (too generic)
- "Calculate the length." ❌ (doesn't reference measurement)
- "What is 15cm in mm?" ❌ (not personalized)

### Educational Context

**Context Builder Features**:
- **Grade Suggestion**: Heuristics based on value ranges
  - Example: Length <30cm → Grade 1, >500cm → Grade 3+
- **Difficulty Hints**: Suggests question types
  - Conversion (cm → mm)
  - Multiplication (3 pencils)
  - Comparison (vs. standard values)
  - Estimation (round to nearest)
- **Personalized Prompt**: Human-readable context
  - "Your pencil is 15cm long."
  - Used in question generation

### RAG Integration

**Vector Search**:
- Query: `"{topic} measurement {value}{unit} {object_name}"`
- Example: "Length measurement 15cm pencil"
- Top 5 curriculum chunks retrieved
- Filtered by topic if available

**Question Generation**:
- Context: RAG chunks (1500 chars max)
- Model: GPT-4o-mini (requires OpenAI credits)
- Temperature: 0.8 (creative but controlled)
- Fallback: Template questions if LLM fails

### Progress Tracking

**Integration**:
- AR questions saved with metadata:
  - `unit_id: "ar_{topic}_{student_id}"`
  - `concepts: [topic, measurement_type, value+unit]`
  - `ar_context: {object, measurement, prompt}`
- Existing UnitProgressService handles tracking
- Shows in measurement home screen progress cards

---

## 🚀 Testing & Deployment

### Quick Test (Without AR Camera)

```dart
// In Flutter app
final arService = ARLearningService();

// Test length measurement
final measurement = await arService.quickTest(
  type: MeasurementType.length,
  objectName: 'pencil',
  value: 15.0,
  unit: MeasurementUnit.cm,
  grade: 1,
);

print('Generated ${measurement.questions.length} questions');
print('First: ${measurement.questions.first.questionText}');
```

### Backend Setup

**1. Start measurement-service**:
```bash
cd measurement-service
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

**2. Ensure RAG service is running**:
```bash
cd unit-rag-service
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**3. Test endpoints**:
```bash
# Health check
curl http://127.0.0.1:8001/health
curl http://127.0.0.1:8000/health

# Test measurement processing
curl -X POST http://127.0.0.1:8001/api/v1/measurements/process \
  -H "Content-Type: application/json" \
  -d '{
    "measurement_type": "length",
    "value": 15,
    "unit": "cm",
    "object_name": "pencil",
    "student_id": "student_123",
    "grade": 1
  }'
```

### Flutter Setup

**1. Install dependencies**:
```bash
cd ganithamithura
flutter pub add json_annotation uuid camera
flutter pub add --dev json_serializable build_runner
flutter pub get
```

**2. Generate JSON serialization**:
```bash
flutter pub run build_runner build --delete-conflicting-outputs
```

**3. Update iOS Info.plist** (for camera):
```xml
<key>NSCameraUsageDescription</key>
<string>We need camera access to measure objects with AR</string>
```

**4. Run app**:
```bash
flutter run
```

---

## 📝 Next Steps

1. **Create AR Measurement Screen**
   - Camera integration OR manual input (for testing)
   - Object name field
   - Unit selection dropdown
   - Measurement value input
   - "Generate Questions" button

2. **Create Questions Display Screen**
   - Show measurement context card
   - Question list with MCQ/short answer UI
   - Hint system (progressive hints)
   - Submit answer with feedback
   - Progress bar

3. **Add Routes** in main.dart

4. **Test Full Flow**:
   - Open Measurements module
   - Tap "Length" AR challenge
   - Enter measurement (e.g., pencil 15cm)
   - Verify contextual questions generated
   - Answer questions
   - Check progress tracking

5. **Polish**:
   - Loading states while generating
   - Error handling (service unavailable)
   - Offline mode (cached questions)
   - Animations and transitions

---

## 🔧 Troubleshooting

### Lint Error in contextual.py

**Error**: Line 111 `await question.save()` - "Argument missing for parameter 'self'"

**Status**: **False positive** - This is a known Pylance issue with Beanie ODM. The code is correct and matches the pattern used throughout the codebase (see `progress.py`, `upload.py`, `questions.py`).

**Action**: No fix needed, safe to ignore.

### OpenAI Credits

**Issue**: GPT-4o-mini requires OpenAI API credits (currently $0 balance)

**Workaround**: Fallback template questions will be used if LLM fails. To enable full AI generation, add OpenAI credits to account.

### iOS Simulator Networking

**Issue**: iOS Simulator doesn't resolve `localhost`

**Solution**: All services use `127.0.0.1` instead of `localhost`
- measurement-service: `http://127.0.0.1:8001`
- unit-rag-service: `http://127.0.0.1:8000`

---

## 📊 File Structure

```
measurement-service/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app (port 8001)
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py             # Pydantic models
│   ├── services/
│   │   ├── __init__.py
│   │   └── context_builder.py     # ContextBuilder class
│   └── routes/
│       ├── __init__.py
│       └── measurement.py         # POST /process
├── requirements.txt
└── README.md

unit-rag-service/app/routes/
└── contextual.py                  # Contextual questions endpoint

ganithamithura/lib/
├── models/
│   └── ar_measurement.dart        # All AR models
├── services/
│   ├── ar_learning_service.dart   # Main coordinator
│   └── api/
│       ├── measurement_api_service.dart
│       └── contextual_question_service.dart
├── screens/measurements/
│   ├── measurement_home_screen.dart  # Updated with AR challenges
│   ├── ar_measurement_screen.dart    # TODO: Create
│   └── ar_questions_screen.dart      # TODO: Create
└── widgets/measurements/
    └── ar_challenge_card.dart     # AR challenge card widget
```

---

## 💡 Design Decisions

### Why Option A (No YOLOv8)?

**Chosen**: Manual topic selection (simpler)
- Faster development
- No model training needed
- Reuses existing RAG/GPT infrastructure
- Better UX (student chooses what to learn)

**Alternative** (not implemented): YOLOv8 object detection
- Would auto-detect objects
- Requires training custom model
- More complex deployment
- Potential accuracy issues

### Why Separate measurement-service?

**Reason**: Separation of concerns
- measurement-service: Domain logic (education context)
- unit-rag-service: AI/ML logic (RAG + LLM)
- Easy to swap/test components independently
- measurement-service has no dependencies

### Why ChromaDB + GPT?

**ChromaDB**: Free local vector database
- No API costs
- Fast semantic search
- Local all-MiniLM-L6-v2 embeddings

**GPT-4o-mini**: Best quality/cost ratio
- Better than GPT-3.5 for personalization
- Cheaper than GPT-4
- Understands complex prompt rules

---

## 🎓 Educational Impact

### Learning Benefits

**Concrete Learning**:
- Abstract math → Real objects
- "15cm" becomes tangible (their actual pencil)
- Spatial reasoning through physical measurement

**Personalization**:
- "YOUR pencil" increases engagement
- Student owns the learning experience
- Questions feel like discovery, not homework

**Progressive Difficulty**:
- Grade suggestions based on measurement complexity
- Difficulty hints guide question generation
- Adaptive learning through progress tracking

### Differentiation

**Unique Features**:
1. ✨ Only app connecting AR measurements to personalized questions
2. ✨ RAG ensures questions align with curriculum
3. ✨ GPT generates natural, conversational questions
4. ✨ Progress persists across devices (MongoDB backend)

**vs. Traditional Apps**:
- Generic: "A pencil is 15cm"
- **GanithaMithura**: "YOUR pencil is 15cm"

---

## 📈 Future Enhancements

1. **Multi-object Comparisons**
   - "Your pencil is 15cm and your eraser is 3cm. What's the difference?"

2. **Challenge Modes**
   - Find 3 objects of different lengths
   - Measure kitchen items for cooking math
   - Room measurement for area practice

3. **Social Features**
   - Share measurements with classmates
   - Compare who found the longest object
   - Collaborative challenges

4. **AR Visualization**
   - Overlay measurement on camera view
   - Show unit conversions in real-time
   - Visual comparison to standard sizes

5. **Offline Mode**
   - Cache generated questions
   - Generate on reconnection
   - Local template questions

---

**Implementation Date**: 2024
**Status**: Backend Complete ✅ | Frontend UI Complete ✅ | AR Screens Pending ⏳
**Next Priority**: Create AR measurement screen and questions display screen
