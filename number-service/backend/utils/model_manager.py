
import os
import logging
from config import Config

logger = logging.getLogger(__name__)

# Global model instance
_model_instance = None


def initialize_model():
    """Initialize the handwriting recognition model"""
    global _model_instance
    
    from app.services import HandwritingRecognitionService
    
    model_path = Config.MODEL_PATH
    
    # Try to find model if path doesn't exist
    if not os.path.exists(model_path or ''):
        possible_paths = [
            'models/handwriting_model_latest.h5',
            '../models/handwriting_model_latest.h5',
            'handwriting_model_latest.h5',
            os.path.join(os.path.dirname(__file__), '..', '..', 'models', 'handwriting_model_latest.h5'),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                model_path = path
                logger.info(f"Found model at: {path}")
                break
    
    if model_path and os.path.exists(model_path):
        try:
            _model_instance = HandwritingRecognitionService(
                model_path, 
                target_size=Config.TARGET_IMAGE_SIZE
            )
            logger.info("Model initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize model: {e}")
            return False
    else:
        logger.warning("Model file not found. API will not be available until model is trained.")
        return False


def get_model_instance():
    """Get the global model instance"""
    global _model_instance
    
    if _model_instance is None:
        initialize_model()
    
    return _model_instance