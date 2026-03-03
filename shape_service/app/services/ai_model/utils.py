"""
Utility functions for YOLOv8-based shape detection.
"""
from PIL import Image
import io
import tempfile
import os
from pathlib import Path


def load_image_from_bytes(image_bytes: bytes) -> Image.Image:
    """
    Load a PIL Image from bytes.
    
    Args:
        image_bytes: Raw image bytes
        
    Returns:
        PIL Image object
    """
    image = Image.open(io.BytesIO(image_bytes))
    return image


def load_image_from_file(file_like) -> Image.Image:
    """
    Load a PIL Image from a file-like object.
    
    Args:
        file_like: File-like object (e.g., UploadFile.file)
        
    Returns:
        PIL Image object
    """
    image = Image.open(file_like)
    return image


def save_temp_image(image: Image.Image) -> str:
    """
    Save PIL Image to a temporary file and return the path.
    YOLO requires file paths for inference.
    
    Args:
        image: PIL Image object
        
    Returns:
        Path to temporary image file
    """
    # Create temp file with proper extension
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
    temp_path = temp_file.name
    temp_file.close()
    
    # Convert to RGB if needed (JPEG doesn't support RGBA)
    if image.mode in ('RGBA', 'LA', 'P'):
        image = image.convert('RGB')
    
    # Save image
    image.save(temp_path, 'JPEG', quality=95)
    
    return temp_path


def cleanup_temp_image(image_path: str):
    """
    Remove temporary image file.
    
    Args:
        image_path: Path to temporary image file
    """
    try:
        if os.path.exists(image_path):
            os.unlink(image_path)
    except Exception as e:
        print(f"⚠️ Failed to cleanup temp file {image_path}: {e}")
