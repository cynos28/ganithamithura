
from flask import Blueprint, request, jsonify
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('livekit', __name__, url_prefix='/livekit')


@bp.route('/token', methods=['POST'])
def get_livekit_token():
    """Generate LiveKit access token"""
    try:
        from app.utils.livekit_manager import get_livekit_service
        
        livekit_service = get_livekit_service()
        
        if not livekit_service:
            return jsonify({
                'error': 'LiveKit not configured',
                'success': False
            }), 500
        
        data = request.get_json() or {}
        room_name = data.get('room')
        participant_name = data.get('participant')
        difficulty = data.get('difficulty', 'easy')
        
        result = livekit_service.generate_token(room_name, participant_name, difficulty)
        
        if not result.get('success'):
            return jsonify(result), 500
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Failed to generate token: {e}")
        return jsonify({
            'error': f'Failed to generate token: {str(e)}',
            'success': False
        }), 500


@bp.route('/rooms', methods=['GET'])
def list_livekit_rooms():
    """List active LiveKit rooms"""
    try:
        from app.utils.livekit_manager import get_livekit_service
        
        livekit_service = get_livekit_service()
        
        if not livekit_service:
            return jsonify({
                'error': 'LiveKit not configured',
                'success': False
            }), 500
        
        result = livekit_service.list_rooms()
        
        if not result.get('success'):
            return jsonify(result), 500
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Failed to list rooms: {e}")
        return jsonify({
            'error': f'Failed to list rooms: {str(e)}',
            'success': False
        }), 500


@bp.route('/webhook', methods=['POST'])
def livekit_webhook():
    """Handle LiveKit webhooks"""
    try:
        from app.utils.livekit_manager import get_livekit_service
        
        livekit_service = get_livekit_service()
        
        if not livekit_service:
            return jsonify({
                'error': 'LiveKit not configured',
                'success': False
            }), 500
        
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'No webhook data provided',
                'success': False
            }), 400
        
        result = livekit_service.process_webhook(data)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Webhook processing failed: {e}")
        return jsonify({
            'error': 'Webhook processing failed',
            'success': False
        }), 500