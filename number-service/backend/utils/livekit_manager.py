
import logging
from config import Config

logger = logging.getLogger(__name__)

# Global LiveKit service instance
_livekit_service = None


def initialize_livekit():
    global _livekit_service
    
    from app.services import LiveKitService
    
    if Config.LIVEKIT_URL and Config.LIVEKIT_API_KEY and Config.LIVEKIT_API_SECRET:
        try:
            _livekit_service = LiveKitService(
                Config.LIVEKIT_URL,
                Config.LIVEKIT_API_KEY,
                Config.LIVEKIT_API_SECRET
            )
            logger.info("LiveKit service initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize LiveKit service: {e}")
            return False
    else:
        logger.warning("LiveKit not configured. Voice features will not be available.")
        return False


def get_livekit_service():
    """Get the global LiveKit service instance"""
    global _livekit_service
    
    if _livekit_service is None:
        initialize_livekit()
    
    return _livekit_service