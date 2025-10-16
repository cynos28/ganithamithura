
from flask import Blueprint, request, jsonify
from datetime import datetime
import logging
import traceback

logger = logging.getLogger(__name__)

bp = Blueprint('prediction', __name__, url_prefix='')


@bp.route('/predict', methods=['POST'])
def predict_digit():
    """Predict handwritten digit from image"""
    try:
        from app.utils.model_manager import get_model_instance
        
        model_instance = get_model_instance()
        
        if model_instance is None or model_instance.model is None:
            return jsonify({
                'error': 'Model not loaded. Please train a model first.',
                'success': False
            }), 500
        
        data = request.get_json()
        
        if not data or 'image' not in data:
            return jsonify({
                'error': 'No image data provided',
                'success': False
            }), 400
        
        image_data = data['image']
        top_k = data.get('top_k', 5)
        expected_answer = data.get('expected_answer', None)
        
        # Preprocess image
        try:
            processed_image = model_instance.preprocess_image(image_data, source_type='base64')
        except Exception as e:
            return jsonify({
                'error': f'Image preprocessing failed: {str(e)}',
                'success': False
            }), 400
        
        # Make prediction
        result = model_instance.predict(processed_image, top_k=top_k)
        
        if not result['success']:
            return jsonify(result), 500
        
        # Check if prediction matches expected answer
        if expected_answer is not None:
            top_prediction = result['predictions'][0]['digit']
            result['is_correct'] = top_prediction == expected_answer
            result['expected_answer'] = expected_answer
        
        result['timestamp'] = datetime.now().isoformat()
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Prediction endpoint error: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': 'Internal server error',
            'success': False
        }), 500


@bp.route('/generate/problem', methods=['GET'])
def generate_problem():
    """Generate a random math problem for practice"""
    try:
        from app.services import ProblemGenerationService
        
        problem_service = ProblemGenerationService()
        problem = problem_service.generate_problem()
        
        return jsonify(problem)
        
    except Exception as e:
        logger.error(f"Problem generation failed: {e}")
        return jsonify({
            'error': 'Failed to generate problem',
            'success': False
        }), 500