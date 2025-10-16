
import tensorflow as tf
import numpy as np
import cv2
import base64
import io
from PIL import Image
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class HandwritingRecognitionService:    
    def __init__(self, model_path, target_size=(64, 64)):
        self.model = None
        self.model_path = model_path
        self.target_size = target_size
        self.load_model()
    
    def load_model(self):
        try:
            self.model = tf.keras.models.load_model(self.model_path)
            logger.info(f"Model loaded successfully from {self.model_path}")
            
            # Warm up the model with a dummy prediction
            dummy_input = np.zeros((1, *self.target_size, 1))
            _ = self.model.predict(dummy_input, verbose=0)
            logger.info("Model warmed up successfully")
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise e
    
    def preprocess_image(self, image_data, source_type='base64'):
        """
        Preprocess image for model prediction
        
        Args:
            image_data: Base64 string or file path
            source_type: 'base64' or 'file'
            
        Returns:
            Preprocessed image array ready for prediction
        """
        try:
            if source_type == 'base64':
                if ',' in image_data:
                    image_data = image_data.split(',')[1]
                
                image_bytes = base64.b64decode(image_data)
                image = Image.open(io.BytesIO(image_bytes))
                
            elif source_type == 'file':
                image = Image.open(image_data)
            
            # Convert to grayscale
            if image.mode != 'L':
                image = image.convert('L')
            
            img_array = np.array(image)
            
            # Crop to content with padding
            coords = cv2.findNonZero(255 - img_array)
            if coords is not None:
                x, y, w, h = cv2.boundingRect(coords)
                
                padding = 10
                x = max(0, x - padding)
                y = max(0, y - padding)
                w = min(img_array.shape[1] - x, w + 2 * padding)
                h = min(img_array.shape[0] - y, h + 2 * padding)
                
                img_array = img_array[y:y+h, x:x+w]
            
            # Resize with padding to maintain aspect ratio
            img_array = self._resize_with_padding(img_array)
            
            # Invert colors (black on white -> white on black)
            img_array = 255 - img_array
            
            # Normalize to [0, 1]
            img_array = img_array.astype(np.float32) / 255.0
            
            # Add batch and channel dimensions
            img_array = np.expand_dims(img_array, axis=(0, -1))
            
            return img_array
            
        except Exception as e:
            logger.error(f"Image preprocessing failed: {e}")
            raise e
    
    def _resize_with_padding(self, image):
        """Resize image to target size with padding to maintain aspect ratio"""
        h, w = image.shape
        target_h, target_w = self.target_size
        
        # Calculate scale to fit within target size
        scale = min(target_w / w, target_h / h)
        new_w = int(w * scale)
        new_h = int(h * scale)
        
        # Resize image
        resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
        
        # Create padded image
        padded = np.zeros(self.target_size, dtype=image.dtype)
        
        # Center the resized image
        start_y = (target_h - new_h) // 2
        start_x = (target_w - new_w) // 2
        padded[start_y:start_y + new_h, start_x:start_x + new_w] = resized
        
        return padded
    
    def predict(self, processed_image, top_k=5):
        """
        Make prediction on preprocessed image
        
        Args:
            processed_image: Preprocessed image array
            top_k: Number of top predictions to return
            
        Returns:
            Dictionary with predictions and metadata
        """
        try:
            start_time = datetime.now()
            
            # Get predictions from model
            predictions = self.model.predict(processed_image, verbose=0)
            probabilities = predictions[0]
            
            end_time = datetime.now()
            inference_time = (end_time - start_time).total_seconds() * 1000
            
            # Get top k predictions
            top_indices = np.argsort(probabilities)[-top_k:][::-1]
            
            results = []
            for idx in top_indices:
                results.append({
                    'digit': int(idx),
                    'confidence': float(probabilities[idx]),
                    'percentage': float(probabilities[idx] * 100)
                })
            
            return {
                'predictions': results,
                'inference_time_ms': inference_time,
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return {
                'error': str(e),
                'success': False
            }