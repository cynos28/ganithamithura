
import os
import logging
from app import create_app
from config import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    # Get configuration environment
    config_name = os.environ.get('FLASK_ENV', 'development')
    app_config = config.get(config_name, config['default'])
    
    # Create Flask app
    app = create_app(app_config)
    
    # Initialize services
    from app.utils import initialize_model, initialize_livekit
    
    model_loaded = initialize_model()
    livekit_configured = initialize_livekit()
    
    # Print startup information
    print("\n" + "="*70)
    print(" Backend - Starting...")
    print("="*70)
    print(f"Environment: {config_name}")
    print(f"Model Path: {app_config.MODEL_PATH}")
    print(f"Model Loaded: {'✓' if model_loaded else '✗'}")
    print(f"LiveKit URL: {app_config.LIVEKIT_URL}")
    print(f"LiveKit Configured: {'✓' if livekit_configured else '✗'}")
    print(f"Server: http://{app_config.HOST}:{app_config.PORT}")
    print("="*70)
    
    if not model_loaded:
        print("\n⚠️  WARNING: No model loaded!")
        print("To train a model, you can:")
        print("1. Run: python quick_train.py")
        print("2. Or use the API: POST /train")
        print()
    
    # Run the application
    app.run(
        host=app_config.HOST,
        port=app_config.PORT,
        debug=app_config.DEBUG
    )


if __name__ == '__main__':
    main()