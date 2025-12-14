"""
Object Detection Service using YOLO
Handles real-time object detection and counting for the Number Learning Module
"""

from ultralytics import YOLO
import cv2
import numpy as np
from typing import List, Dict, Any, Optional
import base64
from collections import defaultdict
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ObjectDetectionService:
    """Service for YOLO-based object detection"""
    
    def __init__(self, model_path: str = "yolov8s.pt"):
        """
        Initialize YOLO model
        
        Args:
            model_path: Path to YOLO model weights (yolov8n.pt, yolov8s.pt, etc.)
        """
        try:
            logger.info(f"Loading YOLO model: {model_path}")
            self.model = YOLO(model_path)
            logger.info("YOLO model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load YOLO model: {e}")
            raise
    
    def detect_objects(
        self, 
        image: np.ndarray,
        target_object: Optional[str] = None,
        confidence_threshold: float = 0.5
    ) -> Dict[str, Any]:
        """
        Detect objects in an image
        
        Args:
            image: Input image as numpy array (BGR format from cv2)
            target_object: Specific object to count (e.g., "apple", "person")
            confidence_threshold: Minimum confidence for detection
            
        Returns:
            Dictionary containing:
                - total_count: Total objects detected
                - target_count: Count of target object (if specified)
                - detections: List of all detected objects with details
                - class_counts: Dictionary of counts per class
        """
        try:
            # Run YOLO detection
            results = self.model(image, conf=confidence_threshold)
            
            detections = []
            class_counts = defaultdict(int)
            target_count = 0
            
            for r in results:
                for box in r.boxes:
                    cls_id = int(box.cls[0])
                    cls_name = self.model.names[cls_id]
                    confidence = float(box.conf[0])
                    
                    # Get bounding box coordinates
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    
                    # Update counts
                    class_counts[cls_name] += 1
                    
                    # Check if this is the target object
                    if target_object and cls_name.lower() == target_object.lower():
                        target_count += 1
                    
                    # Store detection details
                    detections.append({
                        'class': cls_name,
                        'confidence': confidence,
                        'bbox': {
                            'x1': x1,
                            'y1': y1,
                            'x2': x2,
                            'y2': y2
                        },
                        'number': class_counts[cls_name]  # Live numbering per class
                    })
            
            return {
                'total_count': len(detections),
                'target_count': target_count if target_object else None,
                'target_object': target_object,
                'detections': detections,
                'class_counts': dict(class_counts)
            }
            
        except Exception as e:
            logger.error(f"Error during object detection: {e}")
            raise
    
    def detect_from_base64(
        self,
        base64_image: str,
        target_object: Optional[str] = None,
        confidence_threshold: float = 0.5
    ) -> Dict[str, Any]:
        """
        Detect objects from base64 encoded image
        
        Args:
            base64_image: Base64 encoded image string
            target_object: Specific object to count
            confidence_threshold: Minimum confidence for detection
            
        Returns:
            Detection results dictionary
        """
        try:
            # Decode base64 image
            image_data = base64.b64decode(base64_image)
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                raise ValueError("Failed to decode image")
            
            # Perform detection
            return self.detect_objects(image, target_object, confidence_threshold)
            
        except Exception as e:
            logger.error(f"Error processing base64 image: {e}")
            raise
    
    def draw_detections(
        self,
        image: np.ndarray,
        detections: List[Dict[str, Any]],
        target_object: Optional[str] = None
    ) -> np.ndarray:
        """
        Draw bounding boxes and labels on image
        
        Args:
            image: Input image
            detections: List of detections from detect_objects()
            target_object: Highlight this object type in different color
            
        Returns:
            Image with drawn detections
        """
        output_image = image.copy()
        
        for det in detections:
            bbox = det['bbox']
            cls_name = det['class']
            number = det['number']
            confidence = det['confidence']
            
            # Choose color (red for target, blue for others)
            if target_object and cls_name.lower() == target_object.lower():
                color = (0, 0, 255)  # Red for target object
                thickness = 3
            else:
                color = (255, 0, 0)  # Blue for other objects
                thickness = 2
            
            # Draw bounding box
            cv2.rectangle(
                output_image,
                (bbox['x1'], bbox['y1']),
                (bbox['x2'], bbox['y2']),
                color,
                thickness
            )
            
            # Draw label with class name and number
            label = f"{cls_name} {number} ({confidence:.2f})"
            cv2.putText(
                output_image,
                label,
                (bbox['x1'], bbox['y1'] - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2
            )
        
        return output_image
    
    def validate_count(
        self,
        detected_count: int,
        expected_count: int,
        tolerance: int = 0
    ) -> Dict[str, Any]:
        """
        Validate if detected count matches expected count
        
        Args:
            detected_count: Number of objects detected
            expected_count: Expected number of objects
            tolerance: Allowed difference
            
        Returns:
            Validation result with feedback
        """
        difference = abs(detected_count - expected_count)
        is_correct = difference <= tolerance
        
        if is_correct:
            feedback = "Perfect! You counted correctly!"
            points = 100
        elif difference == 1:
            feedback = "Very close! Try counting again."
            points = 50
        else:
            feedback = f"Not quite. Expected {expected_count}, but detected {detected_count}."
            points = 0
        
        return {
            'is_correct': is_correct,
            'detected_count': detected_count,
            'expected_count': expected_count,
            'difference': difference,
            'feedback': feedback,
            'points': points
        }
    
    def get_available_classes(self) -> List[str]:
        """Get list of all classes the model can detect"""
        return list(self.model.names.values())


# Global instance
_detection_service: Optional[ObjectDetectionService] = None


def get_detection_service() -> ObjectDetectionService:
    """Get or create singleton detection service instance"""
    global _detection_service
    if _detection_service is None:
        _detection_service = ObjectDetectionService()
    return _detection_service
