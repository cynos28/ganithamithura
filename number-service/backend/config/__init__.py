
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration"""
    
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    # Server
    HOST = '0.0.0.0'
    PORT = int(os.environ.get('PORT', 5000))
    
    # Model Configuration
    MODEL_PATH = os.environ.get('MODEL_PATH', 'models/handwriting_model_latest.h5')
    TARGET_IMAGE_SIZE = (64, 64)
    
    # LiveKit Configuration
    LIVEKIT_URL = os.environ.get('LIVEKIT_URL', 'ws://localhost:7880')
    LIVEKIT_API_KEY = os.environ.get('LIVEKIT_API_KEY', 'devkey')
    LIVEKIT_API_SECRET = os.environ.get('LIVEKIT_API_SECRET', 'secret')
    
    @staticmethod
    def init_app(app):
        """Initialize application configuration"""
        pass


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True


config = {
    'development': DevelopmentConfig,
    'default': DevelopmentConfig
}
