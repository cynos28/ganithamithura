# Measurement Service

AR measurement context processing service for Ganithamithura.

## Purpose

This service processes AR measurements from the Flutter app and builds educational context for contextual question generation.

## Features

- ✅ Process AR measurement data (length, capacity, weight, area)
- ✅ Build personalized learning context
- ✅ Suggest appropriate grade levels
- ✅ Generate difficulty hints for questions

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run service
python -m app.main
```

Service runs on `http://localhost:8001`

## API Endpoints

### `POST /api/v1/measurements/process`

Process AR measurement and get context.

**Request:**
```json
{
  "measurement_type": "length",
  "value": 15,
  "unit": "cm",
  "object_name": "pencil",
  "student_id": "student_123",
  "grade": 1
}
```

**Response:**
```json
{
  "measurement_type": "length",
  "value": 15,
  "unit": "cm",
  "object_name": "pencil",
  "context_description": "Student measured pencil: 15cm",
  "topic": "Length",
  "suggested_grade": 1,
  "difficulty_hints": ["conversion_to_mm", "multiplication", "addition"],
  "personalized_prompt": "Your pencil is 15cm long."
}
```

## Integration

This service works with:
- **Flutter App**: Receives AR measurements
- **Unit RAG Service**: Provides context for question generation
