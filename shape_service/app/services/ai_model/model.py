"""
YOLOv8-based object detection and shape mapping.
"""
import json
from pathlib import Path
from typing import List, Dict
from ultralytics import YOLO


# Global model instance
_model = None
_shape_map = None


def get_model_instance():
    """
    Get the singleton YOLO model instance. Loads the model on first call.
    
    Returns:
        Tuple of (model, shape_map)
    """
    global _model, _shape_map
    
    if _model is None:
        # Load YOLOv8 model from Hugging Face
        print("🔄 Loading YOLOv8 model from Hugging Face...")
        _model = YOLO("yolov8n.pt")
        print("✅ YOLOv8 model loaded successfully")
        
        # Load shape mapping
        mapping_path = Path(__file__).parent / "mapping.json"
        with open(mapping_path, "r") as f:
            _shape_map = json.load(f)
        print(f"📊 Loaded shape mappings for {len(_shape_map)} object classes")
    
    return _model, _shape_map


def detect_objects_with_shapes(image_path: str) -> List[Dict]:
    """
    Detect objects in an image and map them to shapes.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        List of detections with class_id, class_name, and shape
    """
    model, shape_map = get_model_instance()
    
    # Run YOLO detection
    results = model(image_path)
    
    detections = []
    
    for r in results:
        for box in r.boxes:
            class_id = str(int(box.cls[0]))  # JSON keys are strings
            confidence = float(box.conf[0])
            
            if class_id in shape_map:
                detections.append({
                    "class_id": int(class_id),
                    "class_name": shape_map[class_id]["class_name"],
                    "shape": shape_map[class_id]["shape"],
                    "confidence": round(confidence, 4)
                })
            else:
                detections.append({
                    "class_id": int(class_id),
                    "class_name": model.names[int(class_id)],
                    "shape": "unknown",
                    "confidence": round(confidence, 4)
                })
    
    return detections
