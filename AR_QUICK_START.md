# AR Feature - Quick Start Guide

## 🚀 Start Backend Services

### Option 1: Quick Start (Recommended)
```bash
# From ganithamithura root directory
chmod +x start_ar_services.sh
./start_ar_services.sh
```

### Option 2: Manual Start

**Terminal 1 - measurement-service (port 8001)**:
```bash
cd measurement-service
source venv/bin/activate  # or: venv\Scripts\activate on Windows
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

**Terminal 2 - unit-rag-service (port 8000)**:
```bash
cd unit-rag-service
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 📱 Run Flutter App

```bash
cd ganithamithura

# Install dependencies (first time only)
flutter pub get
flutter pub run build_runner build --delete-conflicting-outputs

# Run on iOS Simulator
flutter run
```

## 🎯 Testing the AR Feature

### Flow:
1. **Open Measurements Module** from home screen
2. **Tap an AR Challenge Card** (Length, Capacity, Weight, or Area)
3. **Enter Measurement Details**:
   - Object name: e.g., "pencil"
   - Value: e.g., "15"
   - Unit: Select "Centimeters"
4. **Tap "Generate Questions"**
5. **Answer Personalized Questions** about YOUR measurement
6. **View Results** and accuracy

### Example Test Cases:

**Length:**
- Object: "pencil"
- Value: 15
- Unit: Centimeters
- Expected: Questions like "Your pencil is 15cm. How many millimeters is that?"

**Capacity:**
- Object: "water bottle"
- Value: 500
- Unit: Milliliters
- Expected: Questions like "Your water bottle holds 500ml. Is that more or less than 1 liter?"

**Weight:**
- Object: "book"
- Value: 250
- Unit: Grams
- Expected: Questions like "Your book weighs 250g. How many kilograms is that?"

**Area:**
- Object: "notebook"
- Value: 300
- Unit: Square Centimeters
- Expected: Questions like "Your notebook has an area of 300cm². What's that in square meters?"

## 🔍 Health Checks

```bash
# Check if services are running
curl http://127.0.0.1:8001/health  # measurement-service
curl http://127.0.0.1:8000/health  # unit-rag-service

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

## 🐛 Troubleshooting

### Services won't start
```bash
# Kill existing processes
lsof -ti :8000 | xargs kill -9
lsof -ti :8001 | xargs kill -9

# Restart services
./start_ar_services.sh
```

### Flutter build errors
```bash
# Clean and rebuild
flutter clean
flutter pub get
flutter pub run build_runner build --delete-conflicting-outputs
```

### "Service not available" in app
1. Check both services are running: `lsof -i :8000` and `lsof -i :8001`
2. Verify URLs in Flutter use `127.0.0.1` (not `localhost`)
3. Check logs for errors

### No questions generated
1. Verify OpenAI API key is set in `unit-rag-service/.env`
2. Check if you have OpenAI credits (fallback questions will be used if no credits)
3. View logs: `tail -f logs/rag-service.log`

## 📊 Logs

Services write to:
- `logs/measurement-service.log`
- `logs/rag-service.log`

View in real-time:
```bash
tail -f logs/measurement-service.log
tail -f logs/rag-service.log
```

## 🛑 Stop Services

```bash
# Kill both services
lsof -ti :8000 | xargs kill -9
lsof -ti :8001 | xargs kill -9
```

## ✨ Features Implemented

✅ AR measurement input screen
✅ Personalized question generation
✅ MCQ question display with hints
✅ Answer checking and feedback
✅ Progress tracking
✅ Results summary
✅ Retry functionality

## 🎓 Next Steps

- [ ] Add camera integration for real AR measurements
- [ ] Implement photo capture of measured objects
- [ ] Add measurement history
- [ ] Create achievements for completing AR challenges
- [ ] Add social sharing of measurements
