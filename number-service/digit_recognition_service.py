"""
Digit Recognition Service for Handwriting Validation
Uses TensorFlow/Keras with MNIST model to recognize handwritten digits
"""

import numpy as np
import cv2
from PIL import Image
import io
import base64
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DigitRecognitionService:
    """Singleton service for digit recognition"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.model = None
        self._load_model()
        self._initialized = True
    
    def _load_model(self):
        """Load custom digit recognition model"""
        try:
            import tensorflow as tf
            from tensorflow import keras
            import os
            
            logger.info("Loading custom digit recognition model...")
            
            # Path to your custom model
            model_path = 'models/my_digit_model.h5'
            
            if os.path.exists(model_path):
                # Load your custom trained model
                self.model = keras.models.load_model(model_path)
                logger.info(f"✅ Loaded custom digit model from {model_path}")
                logger.info(f"   Model input shape: {self.model.input_shape}")
                logger.info(f"   Model output shape: {self.model.output_shape}")
            else:
                logger.warning(f"⚠️ Custom model not found at {model_path}")
                logger.info("Building default model architecture...")
                
                # Build the same architecture as in HandWritten.ipynb
                self.model = keras.models.Sequential([
                    keras.layers.Conv2D(32, (3,3), activation="relu", input_shape=(28,28,1)),
                    keras.layers.MaxPooling2D(),
                    keras.layers.Conv2D(64, (3,3), activation="relu"),
                    keras.layers.MaxPooling2D(),
                    keras.layers.Flatten(),
                    keras.layers.Dense(128, activation="relu"),
                    keras.layers.Dense(10, activation="softmax")
                ])
                
                self.model.compile(
                    optimizer="adam",
                    loss="sparse_categorical_crossentropy",
                    metrics=["accuracy"]
                )
                
                logger.warning("⚠️ Model loaded but not trained. Please train using HandWritten.ipynb")
            
        except ImportError:
            logger.error("❌ TensorFlow not installed. Install with: pip install tensorflow")
            self.model = None
        except Exception as e:
            logger.error(f"❌ Error loading digit recognition model: {e}")
            self.model = None
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for digit recognition"""
        try:
            if image is None:
                logger.error("Image is None")
                return np.zeros((1, 28, 28, 1), dtype=np.float32)
            
            # Convert to grayscale if needed
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            # NO INVERSION NEEDED - Flutter app sends white digits on black background
            # which matches the training data format from HandWritten.ipynb
            
            # Find bounding box of drawn content
            coords = cv2.findNonZero(gray)
            if coords is None:
                logger.warning("No content found in image")
                return np.zeros((1, 28, 28, 1), dtype=np.float32)
            
            x, y, w, h = cv2.boundingRect(coords)
            
            # Add padding
            padding = 20
            x = max(0, x - padding)
            y = max(0, y - padding)
            w = min(gray.shape[1] - x, w + 2 * padding)
            h = min(gray.shape[0] - y, h + 2 * padding)
            
            # Crop to content
            cropped = gray[y:y+h, x:x+w]
            
            # Resize to square with aspect ratio
            size = max(w, h)
            square = np.zeros((size, size), dtype=np.uint8)
            x_offset = (size - w) // 2
            y_offset = (size - h) // 2
            square[y_offset:y_offset+h, x_offset:x_offset+w] = cropped
            
            # Resize to 28x28 (MNIST size)
            resized = cv2.resize(square, (28, 28), interpolation=cv2.INTER_AREA)
            
            # Normalize
            normalized = resized.astype('float32') / 255.0
            
            # Reshape for model input
            processed = normalized.reshape(1, 28, 28, 1)
            
            logger.info(f"Image preprocessed: {image.shape} -> (28, 28)")
            
            return processed
            
        except Exception as e:
            logger.error(f"Error preprocessing image: {e}")
            return np.zeros((1, 28, 28, 1), dtype=np.float32)
    
    def recognize_digit(self, image: np.ndarray) -> dict:
        """
        Recognize digit from image
        
        Args:
            image: NumPy array of image (can be color or grayscale)
        
        Returns:
            dict with prediction results
        """
        if self.model is None:
            return {
                'predicted_digit': -1,
                'confidence': 0.0,
                'probabilities': [],
                'error': 'Model not loaded'
            }
        
        try:
            # Preprocess image
            processed_image = self.preprocess_image(image)
            
            # Validate processed image
            if processed_image.shape != (1, 28, 28, 1):
                raise ValueError(f"Invalid processed image shape: {processed_image.shape}")
            
            # Check if image is blank
            if np.sum(processed_image) < 0.01:
                return {
                    'predicted_digit': -1,
                    'confidence': 0.0,
                    'probabilities': [0.1] * 10,
                    'error': 'Image appears to be blank or has no content',
                    'top_3_predictions': []
                }
            
            # Get prediction
            predictions = self.model.predict(processed_image, verbose=0)
            probabilities = predictions[0].tolist()
            
            # Get predicted digit and confidence
            predicted_digit = int(np.argmax(probabilities))
            confidence = float(probabilities[predicted_digit])
            
            logger.info(f"Predicted digit: {predicted_digit} (confidence: {confidence:.2%})")
            
            return {
                'predicted_digit': predicted_digit,
                'confidence': confidence,
                'probabilities': probabilities,
                'top_3_predictions': self._get_top_predictions(probabilities, 3)
            }
            
        except Exception as e:
            logger.error(f"Error recognizing digit: {e}")
            return {
                'predicted_digit': -1,
                'confidence': 0.0,
                'probabilities': [],
                'error': str(e)
            }
    
    def recognize_from_base64(self, base64_image: str) -> dict:
        """Recognize digit from base64 encoded image"""
        try:
            import os
            from datetime import datetime
            
            # Decode base64
            image_data = base64.b64decode(base64_image)
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                raise ValueError("Failed to decode image")
            
            # Save incoming image for debugging
            debug_dir = "debug_images"
            os.makedirs(debug_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            debug_path = os.path.join(debug_dir, f"incoming_{timestamp}.png")
            cv2.imwrite(debug_path, image)
            logger.info(f"💾 Saved incoming image to: {debug_path}")
            
            return self.recognize_digit(image)
            
        except Exception as e:
            logger.error(f"Error decoding base64 image: {e}")
            return {
                'predicted_digit': -1,
                'confidence': 0.0,
                'probabilities': [],
                'error': f'Failed to decode image: {str(e)}'
            }
    
    def _get_top_predictions(self, probabilities: list, top_n: int = 3) -> list:
        """Get top N predictions with confidence scores"""
        predictions_with_idx = [(i, prob) for i, prob in enumerate(probabilities)]
        predictions_with_idx.sort(key=lambda x: x[1], reverse=True)
        
        return [
            {'digit': digit, 'confidence': float(conf)}
            for digit, conf in predictions_with_idx[:top_n]
        ]

    # ==================== Multi-Digit Recognition ====================

    def _segment_digits(self, gray: np.ndarray) -> list:
        """
        Segment an image into individual digit bounding boxes.
        
        Uses contour detection to find separate digit regions, then merges
        overlapping/close regions that likely belong to the same digit.
        
        Args:
            gray: Grayscale image (white digits on black background)
            
        Returns:
            List of (x, y, w, h) bounding boxes sorted left-to-right
        """
        # Apply threshold to get binary image
        _, binary = cv2.threshold(gray, 30, 255, cv2.THRESH_BINARY)
        
        # Optional: slight dilation to connect broken strokes within a digit
<<<<<<< HEAD
        # Reduced dilation to avoid merging separate digits
        kernel = np.ones((2, 2), np.uint8)
=======
        kernel = np.ones((3, 3), np.uint8)
>>>>>>> feature/shape_int
        dilated = cv2.dilate(binary, kernel, iterations=1)
        
        # Find contours
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return []
        
        # Get bounding boxes, filter out noise (tiny contours)
        img_area = gray.shape[0] * gray.shape[1]
        min_area = img_area * 0.001  # At least 0.1% of image area
        
        bboxes = []
        for c in contours:
            x, y, w, h = cv2.boundingRect(c)
            area = w * h
            if area >= min_area and h > 5 and w > 3:
                bboxes.append((x, y, w, h))
        
        if not bboxes:
            return []
        
        # Sort by x coordinate (left to right)
        bboxes.sort(key=lambda b: b[0])
        
        # Merge overlapping or very close bounding boxes (they belong to the same digit)
<<<<<<< HEAD
        # But be more conservative to avoid merging separate digits like "2" and "0"
=======
>>>>>>> feature/shape_int
        merged = [bboxes[0]]
        for box in bboxes[1:]:
            prev = merged[-1]
            prev_right = prev[0] + prev[2]
<<<<<<< HEAD
            # Reduced gap threshold to avoid merging separate digits
            # Only merge if overlapping or gap is tiny (< 15% of digit width)
            gap_threshold = max(prev[2], box[2]) * 0.15
=======
            # Merge if horizontally overlapping or gap is small relative to digit width
            gap_threshold = max(prev[2], box[2]) * 0.3
>>>>>>> feature/shape_int
            if box[0] <= prev_right + gap_threshold:
                # Merge: union of both boxes
                new_x = min(prev[0], box[0])
                new_y = min(prev[1], box[1])
                new_right = max(prev_right, box[0] + box[2])
                new_bottom = max(prev[1] + prev[3], box[1] + box[3])
                merged[-1] = (new_x, new_y, new_right - new_x, new_bottom - new_y)
            else:
                merged.append(box)
        
        logger.info(f"Segmented {len(merged)} digit region(s) from image")
        return merged

    def _preprocess_digit_region(self, gray: np.ndarray, bbox: tuple) -> np.ndarray:
        """
        Preprocess a single digit region for the model.
        
        Args:
            gray: Full grayscale image
            bbox: (x, y, w, h) bounding box of the digit region
            
        Returns:
            Preprocessed image ready for model input (1, 28, 28, 1)
        """
        x, y, w, h = bbox
        
        # Add padding around the digit
        padding = max(int(max(w, h) * 0.2), 10)
        x1 = max(0, x - padding)
        y1 = max(0, y - padding)
        x2 = min(gray.shape[1], x + w + padding)
        y2 = min(gray.shape[0], y + h + padding)
        
        cropped = gray[y1:y2, x1:x2]
        crop_h, crop_w = cropped.shape
        
        # Make square while preserving aspect ratio
        size = max(crop_w, crop_h)
        square = np.zeros((size, size), dtype=np.uint8)
        x_off = (size - crop_w) // 2
        y_off = (size - crop_h) // 2
        square[y_off:y_off + crop_h, x_off:x_off + crop_w] = cropped
        
        # Resize to 28x28 (MNIST size)
        resized = cv2.resize(square, (28, 28), interpolation=cv2.INTER_AREA)
        
        # Normalize and reshape
        normalized = resized.astype('float32') / 255.0
        return normalized.reshape(1, 28, 28, 1)

<<<<<<< HEAD
    def recognize_number(self, image: np.ndarray, save_debug: bool = False, debug_path: str = None) -> dict:
=======
    def recognize_number(self, image: np.ndarray) -> dict:
>>>>>>> feature/shape_int
        """
        Recognize a multi-digit number from an image.
        
        Segments the image into individual digits, recognizes each one,
        and combines them into the full number.
        
        Args:
            image: NumPy array of image (can be color or grayscale)
<<<<<<< HEAD
            save_debug: Whether to save debug visualization
            debug_path: Path prefix for debug images
=======
>>>>>>> feature/shape_int
            
        Returns:
            dict with:
                - predicted_number: The full recognized number (int)
                - digit_results: List of per-digit recognition results
                - confidence: Average confidence across all digits
        """
        if self.model is None:
            return {
                'predicted_number': -1,
                'confidence': 0.0,
                'digit_results': [],
                'error': 'Model not loaded'
            }
        
        try:
            # Convert to grayscale
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()
            
            # Check for blank image
            if np.sum(gray) < 100:
                return {
                    'predicted_number': -1,
                    'confidence': 0.0,
                    'digit_results': [],
                    'error': 'Image appears to be blank'
                }
            
            # Segment into digit regions
            digit_bboxes = self._segment_digits(gray)
            
<<<<<<< HEAD
            # Save debug visualization if requested
            if save_debug and debug_path and digit_bboxes:
                debug_img = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR) if len(gray.shape) == 2 else image.copy()
                for i, bbox in enumerate(digit_bboxes):
                    x, y, w, h = bbox
                    cv2.rectangle(debug_img, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    cv2.putText(debug_img, f"#{i}", (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                cv2.imwrite(debug_path, debug_img)
                logger.info(f"💾 Saved segmentation debug image to: {debug_path}")
            
=======
>>>>>>> feature/shape_int
            if not digit_bboxes:
                # Fallback: treat entire image as single digit
                logger.warning("No digit segments found, falling back to single-digit recognition")
                single_result = self.recognize_digit(image)
                return {
                    'predicted_number': single_result.get('predicted_digit', -1),
                    'confidence': single_result.get('confidence', 0.0),
                    'digit_results': [single_result],
                    'is_single_digit': True
                }
            
            # Recognize each digit
            digit_results = []
            digits_str = ""
            total_confidence = 0.0
            
            for i, bbox in enumerate(digit_bboxes):
                processed = self._preprocess_digit_region(gray, bbox)
                
                # Check if region has content
                if np.sum(processed) < 0.01:
                    logger.warning(f"Digit region {i} appears blank, skipping")
                    continue
                
                predictions = self.model.predict(processed, verbose=0)
                probabilities = predictions[0].tolist()
                predicted_digit = int(np.argmax(probabilities))
                confidence = float(probabilities[predicted_digit])
                
                digit_results.append({
                    'position': i,
                    'predicted_digit': predicted_digit,
                    'confidence': confidence,
                    'bbox': {'x': bbox[0], 'y': bbox[1], 'w': bbox[2], 'h': bbox[3]},
                    'top_3_predictions': self._get_top_predictions(probabilities, 3)
                })
                
                digits_str += str(predicted_digit)
                total_confidence += confidence
            
            if not digit_results:
                return {
                    'predicted_number': -1,
                    'confidence': 0.0,
                    'digit_results': [],
                    'error': 'No valid digit regions found'
                }
            
            predicted_number = int(digits_str)
            avg_confidence = total_confidence / len(digit_results)
            
            logger.info(f"Recognized number: {predicted_number} (avg confidence: {avg_confidence:.2%}, {len(digit_results)} digits)")
            
            return {
                'predicted_number': predicted_number,
                'confidence': avg_confidence,
                'digit_results': digit_results,
                'num_digits': len(digit_results),
                'is_single_digit': len(digit_results) == 1
            }
            
        except Exception as e:
            logger.error(f"Error recognizing number: {e}")
            return {
                'predicted_number': -1,
                'confidence': 0.0,
                'digit_results': [],
                'error': str(e)
            }

    def recognize_number_from_base64(self, base64_image: str) -> dict:
        """Recognize multi-digit number from base64 encoded image"""
        try:
            import os
            from datetime import datetime
            
            image_data = base64.b64decode(base64_image)
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                raise ValueError("Failed to decode image")
            
            # Save for debugging
            debug_dir = "debug_images"
            os.makedirs(debug_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            debug_path = os.path.join(debug_dir, f"number_incoming_{timestamp}.png")
            cv2.imwrite(debug_path, image)
            logger.info(f"💾 Saved incoming number image to: {debug_path}")
            
            return self.recognize_number(image)
            
        except Exception as e:
            logger.error(f"Error decoding base64 image: {e}")
            return {
                'predicted_number': -1,
                'confidence': 0.0,
                'digit_results': [],
                'error': f'Failed to decode image: {str(e)}'
            }

    def validate_number(self, image: np.ndarray, expected_number: int,
<<<<<<< HEAD
                        confidence_threshold: float = 0.1, save_debug: bool = False, debug_path: str = None) -> dict:
=======
                        confidence_threshold: float = 0.1) -> dict:
>>>>>>> feature/shape_int
        """
        Validate if drawn number matches expected number (supports multi-digit).
        
        Args:
            image: NumPy array of drawn image
            expected_number: The number that should have been drawn
            confidence_threshold: Minimum average confidence for validation
<<<<<<< HEAD
            save_debug: Whether to save debug visualization
            debug_path: Path prefix for debug images
=======
>>>>>>> feature/shape_int
            
        Returns:
            dict with validation results
        """
<<<<<<< HEAD
        result = self.recognize_number(image, save_debug=save_debug, debug_path=debug_path)
=======
        result = self.recognize_number(image)
>>>>>>> feature/shape_int
        
        if 'error' in result:
            return {
                'is_correct': False,
                'expected': expected_number,
                'predicted': -1,
                'confidence': 0.0,
                'feedback': 'Error processing image',
                'error': result['error']
            }
        
        predicted_number = result['predicted_number']
        confidence = result['confidence']
        
        is_correct = predicted_number == expected_number and confidence >= confidence_threshold
        
        # Generate feedback
        if is_correct:
            feedback = f"Perfect! You drew {expected_number} correctly!"
        elif predicted_number == expected_number:
            feedback = f"Good try! Your {expected_number} needs a bit more clarity."
        else:
            feedback = f"That looks like {predicted_number}. Try drawing {expected_number} again."
        
        return {
            'is_correct': is_correct,
            'expected': expected_number,
            'predicted': predicted_number,
            'confidence': confidence,
            'feedback': feedback,
            'digit_results': result.get('digit_results', []),
            'num_digits': result.get('num_digits', 0)
        }
    
    def validate_digit(self, image: np.ndarray, expected_digit: int, 
                      confidence_threshold: float = 0.1) -> dict: # TODO: adjust threshold back to 0.7 when model is better trained
        """
        Validate if drawn digit matches expected digit
        
        Args:
            image: NumPy array of drawn image
            expected_digit: The digit that should have been drawn (0-9)
            confidence_threshold: Minimum confidence for validation
        
        Returns:
            dict with validation results
        """
        result = self.recognize_digit(image)
        
        if 'error' in result:
            return {
                'is_correct': False,
                'expected': expected_digit,
                'predicted': -1,
                'confidence': 0.0,
                'feedback': 'Error processing image',
                'error': result['error']
            }
        
        predicted_digit = result['predicted_digit']
        confidence = result['confidence']
        
        is_correct = predicted_digit == expected_digit and confidence >= confidence_threshold
        
        # Generate feedback
        if is_correct:
            feedback = f"Perfect! You drew {expected_digit} correctly!"
        elif predicted_digit == expected_digit:
            feedback = f"Good try! Your {expected_digit} needs a bit more clarity."
        else:
            feedback = f"That looks like {predicted_digit}. Try drawing {expected_digit} again."
        
        return {
            'is_correct': is_correct,
            'expected': expected_digit,
            'predicted': predicted_digit,
            'confidence': confidence,
            'feedback': feedback,
            'top_3_predictions': result.get('top_3_predictions', [])
        }


# Singleton instance
_service_instance = None

def get_recognition_service() -> DigitRecognitionService:
    """Get singleton instance of digit recognition service"""
    global _service_instance
    if _service_instance is None:
        _service_instance = DigitRecognitionService()
    return _service_instance
