
from flask import Blueprint, request, jsonify
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('voice', __name__, url_prefix='/voice')


@bp.route('/generate', methods=['GET'])
def generate_voice_problem():
    """Generate a voice-based math question"""
    try:
        from app.services import VoiceMathService
        
        difficulty = request.args.get('difficulty', 'easy')
        if difficulty not in ['easy', 'medium', 'hard']:
            difficulty = 'easy'
        
        voice_service = VoiceMathService()
        question_data = voice_service.generate_question(difficulty)
        
        if not question_data.get('success'):
            return jsonify(question_data), 500
        
        question_data['timestamp'] = datetime.now().isoformat()
        
        return jsonify(question_data)
        
    except Exception as e:
        logger.error(f"Failed to generate voice question: {e}")
        return jsonify({
            'error': 'Failed to generate question',
            'success': False
        }), 500


@bp.route('/validate', methods=['POST'])
def validate_voice_response():
    """Validate user's voice response"""
    try:
        from app.services import VoiceMathService
        
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'No data provided',
                'success': False
            }), 400
        
        user_input = data.get('user_input', '')
        correct_answer = data.get('answer')
        question_type = data.get('type')
        
        if not user_input or correct_answer is None:
            return jsonify({
                'error': 'Missing required fields: user_input, answer',
                'success': False
            }), 400
        
        voice_service = VoiceMathService()
        validation_result = voice_service.validate_answer(user_input, correct_answer, question_type)
        
        if not validation_result.get('success'):
            return jsonify(validation_result), 500
        
        # Generate feedback
        feedback = voice_service.get_feedback_message(
            validation_result['is_correct'],
            validation_result['confidence'],
            correct_answer
        )
        
        return jsonify({
            'success': True,
            'is_correct': validation_result['is_correct'],
            'user_answer': validation_result.get('user_answer'),
            'correct_answer': correct_answer,
            'confidence': validation_result['confidence'],
            'feedback': feedback,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        return jsonify({
            'error': 'Validation failed',
            'success': False
        }), 500


@bp.route('/hints', methods=['POST'])
def get_hint():
    """Get a hint for the current question"""
    try:
        from app.services import VoiceMathService
        
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'No data provided',
                'success': False
            }), 400
        
        question_type = data.get('type')
        params = data.get('params', {})
        
        if not question_type:
            return jsonify({
                'error': 'Missing required field: type',
                'success': False
            }), 400
        
        voice_service = VoiceMathService()
        hint = voice_service.get_hint(question_type, params)
        
        return jsonify({
            'success': True,
            'hint': hint,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Failed to get hint: {e}")
        return jsonify({
            'error': 'Failed to get hint',
            'success': False
        }), 500