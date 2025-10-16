
from flask import Flask
from flask_cors import CORS
import logging
from .config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize CORS
    CORS(app)
    
    # Register blueprints
    from app.routes import health, prediction, voice, livekit
    
    app.register_blueprint(health.bp)
    app.register_blueprint(prediction.bp)
    app.register_blueprint(voice.bp)
    app.register_blueprint(livekit.bp)
    
    # Register error handlers
    from app.routes.errors import register_error_handlers
    register_error_handlers(app)
    
    logger.info("Application initialized successfully")
    
    return app