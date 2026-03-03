"""
Shape prediction service using YOLOv8 object detection.
Maps detected objects to geometric shapes.
"""
from PIL import Image
import requests
from typing import Union, Dict, List
from pathlib import Path

from app.services.ai_model.model import detect_objects_with_shapes
from app.services.ai_model.utils import (
    load_image_from_file,
    save_temp_image,
    cleanup_temp_image
)


def get_shape_from_image(image_input: Union[str, object], use_tta: bool = True) -> str:
    """
    Identifies the geometric shape in an image using YOLOv8 object detection.
    Detects objects and maps them to shapes based on mapping.json.

    Args:
        image_input: The input image, which can be a string (URL) or a
                     file-like object (e.g., from an uploaded file).
        use_tta: Not used anymore (kept for backward compatibility)

    Returns:
        A string representing the detected shape (e.g., "Rectangle", "Circle").
    """
    print("🔍 Detecting objects and mapping to shapes using YOLOv8...")
    
    # Load image based on input type
    if isinstance(image_input, str):
        # Assume it's a URL
        try:
            response = requests.get(image_input, stream=True, timeout=10)
            response.raise_for_status()
            image = Image.open(response.raw)
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Could not retrieve image from URL: {e}")
    else:
        # Assume it's a file-like object
        image = load_image_from_file(image_input)
    
    # Convert to RGB if needed
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Save to temp file (YOLO requires file path)
    temp_path = save_temp_image(image)
    
    try:
        # Detect objects and get shapes
        detections = detect_objects_with_shapes(temp_path)
        
        if not detections:
            print("⚠️ No objects detected in the image")
            return "Unknown"
        
        # Return the shape of the first (most confident) detection
        primary_shape = detections[0]["shape"]
        confidence = detections[0]["confidence"]
        object_name = detections[0]["class_name"]
        
        print(f"✅ Detected: {object_name} → Shape: {primary_shape} (confidence: {confidence:.4f})")
        
        # Return capitalized shape name
        return primary_shape.capitalize()
        
    finally:
        # Cleanup temp file
        cleanup_temp_image(temp_path)


def get_shape_with_confidence(image_input: Union[str, object], use_tta: bool = True) -> Dict[str, Union[str, float]]:
    """
    Identifies the geometric shape in an image and returns both prediction and confidence.
    Uses YOLOv8 for object detection and shape mapping.

    Args:
        image_input: The input image, which can be a string (URL) or a
                     file-like object (e.g., from an uploaded file).
        use_tta: Not used anymore (kept for backward compatibility)

    Returns:
        A dictionary containing:
        - predicted_shape: The predicted shape label
        - confidence: The confidence score (0-1)
        - object_name: The detected object name
        - method: Always 'yolo'
    """
    print("🔍 Detecting shape with confidence using YOLOv8...")
    
    # Load image based on input type
    if isinstance(image_input, str):
        try:
            response = requests.get(image_input, stream=True, timeout=10)
            response.raise_for_status()
            image = Image.open(response.raw)
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Could not retrieve image from URL: {e}")
    else:
        image = load_image_from_file(image_input)
    
    # Convert to RGB if needed
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Save to temp file
    temp_path = save_temp_image(image)
    
    try:
        # Detect objects and get shapes
        detections = detect_objects_with_shapes(temp_path)
        
        if not detections:
            return {
                "predicted_shape": "Unknown",
                "confidence": 0.0,
                "object_name": "none",
                "method": "yolo"
            }
        
        # Return first detection info
        primary = detections[0]
        
        print(f"✅ Detected: {primary['class_name']} → {primary['shape']} (confidence: {primary['confidence']:.4f})")
        
        return {
            "predicted_shape": primary["shape"].capitalize(),
            "confidence": primary["confidence"],
            "object_name": primary["class_name"],
            "method": "yolo"
        }
        
    finally:
        cleanup_temp_image(temp_path)


def get_shape_with_alternatives(image_input: Union[str, object], top_k: int = 3) -> Dict:
    """
    Get shape prediction with alternative possibilities.
    Useful for debugging and understanding why shapes might be misdetected.

    Argsall detected objects with their shapes.
    Returns multiple detections if available.

    Args:
        image_input: The input image
        top_k: Maximum number of detections to return (default: 3)

    Returns:
        Dictionary with all detected objects and their shapes
    """
    print(f"🔍 Getting all object detections (up to {top_k})...")
    
    # Load image based on input type
    if isinstance(image_input, str):
        try:
            response = requests.get(image_input, stream=True, timeout=10)
            response.raise_for_status()
            image = Image.open(response.raw)
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Could not retrieve image from URL: {e}")
    else:
        image = load_image_from_file(image_input)
    
    # Convert to RGB if needed
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Save to temp file
    temp_path = save_temp_image(image)
    
    try:
        # Detect all objects
        detections = detect_objects_with_shapes(temp_path)
        
        if not detections:
            return {
                "primary_prediction": "Unknown",
                "primary_confidence": 0.0,
                "alternatives": [],
                "all_detections": []
            }
        
        # Limit to top_k detections
        detections = detections[:top_k]
        
        # Format results
        formatted_detections = [
            {
                "object": det["class_name"],
                "shape": det["shape"].capitalize(),
                "confidence": det["confidence"]
            }
            for det in detections
        ]
        
        primary = formatted_detections[0]
        
        print(f"✅ Primary: {primary['object']} → {primary['shape']} ({primary['confidence']:.4f})")
        
        return {
            "primary_prediction": primary["shape"],
            "primary_confidence": primary["confidence"],
            "primary_object": primary["object"],
            "alternatives": formatted_detections[1:] if len(formatted_detections) > 1 else [],
            "all_detections": formatted_detections
        }
        
    finally:
        cleanup_temp_image(temp_path)