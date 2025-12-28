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
