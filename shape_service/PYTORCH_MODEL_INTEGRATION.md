# PyTorch Model Integration - Shape Classifier

## 🎯 Overview

Your trained PyTorch model (`shape_classifier.pt`) has been successfully integrated into the Shape Service. The model uses **ResNet18 architecture** and can classify **25 different shapes**.

## 📊 Model Details

- **Architecture**: ResNet18 (fine-tuned)
- **Number of Classes**: 25
- **Input Size**: 224x224 RGB images
- **Model File**: `ganithamithura/shape_service/app/services/ai_model/shape_classifier.pt`

### Supported Shapes (25 classes):
```
circle, cone, cube, cuboid, cylinder, decagon, dodecahedron, ellipse, 
heptagon, hexagon, icosahedron, nonagon, octagon, octahedron, 
parallelogram, pentagon, prism, pyramid, rectangle, rhombus, sphere, 
square, tetrahedron, trapezoid, triangle
```

## 🏗️ Project Structure

```
ganithamithura/
├── api-gateway/                      # Main entry point
│   ├── start_gateway.ps1            # 🚀 Start all services here
│   └── app/main.py                  # Gateway that mounts all services
├── shape_service/
│   ├── app/
│   │   └── services/
│   │       ├── ai_model/
│   │       │   ├── shape_classifier.pt    # Your trained model
│   │       │   ├── model.py               # Model loader
│   │       │   └── utils.py               # Preprocessing utilities
│   │       └── shape_predict.py           # Prediction service
│   ├── test_pytorch_integration.py        # Test script
│   └── start_service.ps1                  # Standalone service starter
└── common/                                # Shared utilities
```

## 🚀 Quick Start

### Option 1: Start All Services via API Gateway (Recommended)

```powershell
cd D:\Project\RrsearchPrpject\ganithamithura\api-gateway
.\start_gateway.ps1
```

The API Gateway will be available at: **http://localhost:8000**

### Option 2: Start Shape Service Standalone

```powershell
cd D:\Project\RrsearchPrpject\ganithamithura\shape_service
.\start_service.ps1
```

The service will be available at: **http://localhost:8001**

## 🧪 Testing the Integration

### 1. Run Integration Tests

```powershell
cd ganithamithura\shape_service
uv run test_pytorch_integration.py
```

### 2. Test via API Gateway

**Endpoint**: `POST http://localhost:8000/shapes-patterns/detect-shape`

#### Upload a file:

```bash
curl -X POST "http://localhost:8000/shapes-patterns/detect-shape" \
  -F "image_file=@path/to/your/shape.jpg"
```

**Response:**
```json
{
  "shape": "Circle"
}
```

#### Use an image URL:

```bash
curl -X POST "http://localhost:8000/shapes-patterns/detect-shape" \
  -H "Content-Type: application/json" \
  -d '{"image_url": "https://example.com/shape.jpg"}'
```

### 3. Test Standalone Service

If running the shape service standalone on port 8001:

```bash
curl -X POST "http://localhost:8001/detect-shape" \
  -F "image_file=@path/to/your/shape.jpg"
```

### 4. Interactive API Documentation

Visit: **http://localhost:8000/docs**

You can test the endpoints directly in the browser with the Swagger UI.

## 📝 Code Implementation

### Model Loading (model.py)

```python
from app.services.ai_model.model import get_model_instance

# Loads model once and caches it
model, class_names, device = get_model_instance()
```

### Image Preprocessing (utils.py)

```python
from app.services.ai_model.utils import preprocess_image
from PIL import Image

image = Image.open("shape.jpg")
tensor = preprocess_image(image)  # Returns [1, 3, 224, 224] tensor
```

### Making Predictions (shape_predict.py)

```python
from app.services.shape_predict import get_shape_from_image, get_shape_with_confidence

# Simple prediction
shape = get_shape_from_image("shape.jpg")
# Returns: "Circle"

# Prediction with confidence
result = get_shape_with_confidence("shape.jpg")
# Returns: {"predicted_shape": "Circle", "confidence": 0.9816}
```

## 🔧 Technical Details

### Model Architecture

The model uses a ResNet18 backbone with a modified final layer:

```python
import torch.nn as nn
from torchvision import models

model = models.resnet18(weights=None)
model.fc = nn.Linear(model.fc.in_features, 25)  # 25 classes
```

### Image Preprocessing Pipeline

Images are preprocessed to match training conditions:

1. Convert to RGB (if not already)
2. Resize to 224x224
3. Convert to tensor (values 0-1)
4. Add batch dimension

```python
transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])
```

### Prediction Process

1. Load image from file or URL
2. Preprocess to tensor
3. Forward pass through model
4. Apply softmax to get probabilities
5. Return class with highest probability

## 📦 Dependencies

Added to `pyproject.toml`:

```toml
dependencies = [
    "torch>=2.9.1",
    "torchvision>=0.20.1",
    "pillow>=12.0.0",
    "numpy>=2.3.5",
    "requests>=2.32.5",
    ...
]
```

Install with:
```powershell
uv sync
```

## 🎨 API Endpoints

### Shape Detection

**POST** `/shapes-patterns/detect-shape`

**Headers:**
- `Content-Type: multipart/form-data` (for file upload)
- `Content-Type: application/json` (for URL)

**Request Body (File Upload):**
```
image_file: <binary file>
```

**Request Body (URL):**
```json
{
  "image_url": "https://example.com/shape.jpg"
}
```

**Response:**
```json
{
  "shape": "Hexagon"
}
```

## 🐛 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'common'"

**Solution**: Use the provided startup scripts which set the correct Python path:
```powershell
.\start_gateway.ps1
```

### Issue: Model not loading

**Check**:
1. Model file exists at: `ganithamithura/shape_service/app/services/ai_model/shape_classifier.pt`
2. Run: `uv run test_pytorch_integration.py` to verify

### Issue: "Failed to hardlink files" warning

This is normal on Windows when cache and target are on different drives. You can safely ignore it or set:
```powershell
$env:UV_LINK_MODE = "copy"
```

## 📈 Performance

- **Model Size**: ~44MB (ResNet18)
- **Inference Time**: ~50-200ms per image (CPU)
- **GPU Support**: Automatically detected and used if available

## 🔐 Security Notes

- The service accepts both file uploads and URLs
- URL requests have a 10-second timeout
- Consider adding file size limits in production
- Validate image formats before processing

## 📚 Additional Resources

- **Test Script**: `test_pytorch_integration.py` - Verify setup
- **Inspect Model**: `inspect_model.py` - View model structure
- **API Docs**: http://localhost:8000/docs - Interactive testing

## ✅ Next Steps

1. ✅ Model integrated and tested
2. ✅ API endpoints configured
3. ✅ Startup scripts created
4. 🔄 Consider adding:
   - Batch prediction support
   - Model versioning
   - Prediction caching
   - Confidence threshold filtering
   - A/B testing with multiple models

---

**Last Updated**: January 4, 2026
**Model Version**: shape_classifier.pt (ResNet18, 25 classes)
