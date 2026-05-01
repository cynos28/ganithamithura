# Ganitha Mithura - Number Service

Backend API service for the **Number Learning Module** of the Ganitha Mithura application. This service handles activity management, handwriting recognition, and camera-based counting tests.

## 🚀 Features

- **Activity Management**: Serves structured learning content (videos, tracing, counting, etc.) for numbers 1-1000 across 5 difficulty levels.
- **Handwriting Recognition**: Uses a custom-trained CNN model (Keras/TensorFlow) to validate handwritten digits and multi-digit numbers.
- **Object Detection**: Integrates YOLO-based object detection to count real-world objects via the camera.
- **Assessment System**: Dynamic generation of progress tests (Beginner, Intermediate, Advanced) to track child development.

## 🛠️ Setup & Installation

### Prerequisites
- Python 3.10+
- Virtual Environment tool (`venv`)

### Installation Steps

1. **Navigate to the service directory:**
   ```bash
   cd number-service
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # macOS/Linux
   # or
   .venv\Scripts\activate     # Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## 🏃 Running the Service

Start the FastAPI server using Uvicorn:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The service will be available at `http://localhost:8000`. You can access the auto-generated documentation at `http://localhost:8000/docs`.

## 📍 Key API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/activities/level/{level}/number/{number}` | GET | Get learning activities for a specific number. |
| `/recognize/digit` | POST | Validate a single handwritten digit. |
| `/recognize/number` | POST | Validate multi-digit handwritten numbers. |
| `/test/beginner` | GET | Fetch questions for the beginner assessment. |
| `/health` | GET | Check service status. |

## 🏗️ Project Structure

- `main.py`: Primary FastAPI application and endpoint definitions.
- `digit_recognition_service.py`: Logic for preprocessing and classifying handwritten digits.
- `object_detection_service.py`: Service for real-world object counting using ML models.
- `data/`: JSON files containing activity content for different levels.
- `models/`: Pre-trained weights for the handwriting and detection models.
- `training/`: Jupyter notebooks and scripts used for model training.

---
*Part of the Ganitha Mithura Microservice Architecture.*
