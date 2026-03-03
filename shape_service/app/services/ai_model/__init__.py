"""
AI Model package for YOLOv8-based object detection and shape mapping.
"""
from app.services.ai_model.model import get_model_instance, detect_objects_with_shapes
from app.services.ai_model.utils import load_image_from_bytes, load_image_from_file, save_temp_image, cleanup_temp_image

__all__ = [
    "get_model_instance",
    "detect_objects_with_shapes",
    "load_image_from_bytes",
    "load_image_from_file",
    "save_temp_image",
    "cleanup_temp_image",
]
