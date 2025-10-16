
import random
import re
import logging

logger = logging.getLogger(__name__)


class VoiceMathService:
    
    # Question templates and configurations
    QUESTION_TEMPLATES = {
        'greater_than': {
            'templates': [
                'Which is greater, {a} or {b}?',
                'Which number is bigger, {a} or {b}?',
                'What is the larger number between {a} and {b}?',
            ],
            'answer_func': lambda a, b: max(a, b),
            'range': (0, 20)
        },
        'less_than': {
            'templates': [
                'Which is smaller, {a} or {b}?',
                'Which number is less, {a} or {b}?',
                'What is the smaller number between {a} and {b}?',
            ],
            'answer_func': lambda a, b: min(a, b),
            'range': (0, 20)
        },
        'what_comes_after': {
            'templates': [
                'What number comes after {num}?',
                'What is the next number after {num}?',
            ],
            'answer_func': lambda num: num + 1,
            'range': (0, 98)
        },
        'what_comes_before': {
            'templates': [
                'What number comes before {num}?',
                'What comes right before {num}?',
            ],
            'answer_func': lambda num: num - 1,
            'range': (1, 99)
        },
        'simple_addition': {
            'templates': [
                'What is {a} plus {b}?',
                '{a} plus {b} equals what?',
            ],
            'answer_func': lambda a, b: a + b,
            'range': (0, 10)
        },
        'simple_subtraction': {
            'templates': [
                'What is {a} minus {b}?',
                '{a} minus {b} equals what?',
            ],
            'answer_func': lambda a, b: a - b,
            'range': (0, 10)
        }
    }
    
    # Number word mappings for speech recognition
    NUMBER_WORDS = {
        'zero': '0', 'one': '1', 'two': '2', 'three': '3', 'four': '4',
        'five': '5', 'six': '6', 'seven': '7', 'eight': '8', 'nine': '9',
        'ten': '10', 'eleven': '11', 'twelve': '12', 'thirteen': '13',
        'fourteen': '14', 'fifteen': '15', 'sixteen': '16', 'seventeen': '17',
        'eighteen': '18', 'nineteen': '19', 'twenty': '20'
    }
    
    def generate_question(self, difficulty='easy'):
        """
        Generate a random math question based on difficulty
        
        Args:
            difficulty: 'easy', 'medium', or 'hard'
            
        Returns:
            Dictionary with question, answer, and metadata
        """
        try:
            # Select question types based on difficulty
            if difficulty == 'easy':
                question_types = ['greater_than', 'less_than', 'what_comes_after', 'what_comes_before']
            elif difficulty == 'medium':
                question_types = ['greater_than', 'less_than', 'simple_addition', 'what_comes_after']
            else:
                question_types = list(self.QUESTION_TEMPLATES.keys())
            
            question_type = random.choice(question_types)
            question_data = self.QUESTION_TEMPLATES[question_type]
            min_val, max_val = question_data['range']
            
            # Generate question based on type
            if question_type in ['greater_than', 'less_than', 'simple_addition', 'simple_subtraction']:
                a = random.randint(min_val, max_val)
                b = random.randint(min_val, max_val)
                
                # Ensure a != b for comparison questions
                while a == b:
                    b = random.randint(min_val, max_val)
                
                # For subtraction, ensure result is non-negative
                if question_type == 'simple_subtraction':
                    a, b = max(a, b), min(a, b)
                
                question_text = random.choice(question_data['templates']).format(a=a, b=b)
                answer = question_data['answer_func'](a, b)
                params = {'a': a, 'b': b}
                
            else:  # Single number questions
                num = random.randint(min_val, max_val)
                question_text = random.choice(question_data['templates']).format(num=num)
                answer = question_data['answer_func'](num)
                params = {'num': num}
            
            return {
                'question': question_text,
                'answer': answer,
                'type': question_type,
                'difficulty': difficulty,
                'params': params,
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Failed to generate question: {e}")
            return {
                'error': str(e),
                'success': False
            }
    
    def normalize_speech_input(self, text):
        """
        Normalize speech input for comparison
        
        Args:
            text: Raw speech-to-text input
            
        Returns:
            Tuple of (normalized_text, extracted_numbers)
        """
        if not text:
            return "", []
        
        text = text.lower().strip()
        
        # Convert number words to digits
        for word, digit in self.NUMBER_WORDS.items():
            text = text.replace(word, digit)
        
        # Extract all numbers from text
        numbers = re.findall(r'\d+', text)
        
        return text, numbers
    
    def validate_answer(self, user_input, correct_answer, question_type):
        """
        Validate user's voice answer
        
        Args:
            user_input: User's spoken answer
            correct_answer: Correct answer
            question_type: Type of question
            
        Returns:
            Dictionary with validation results
        """
        try:
            normalized_input, extracted_numbers = self.normalize_speech_input(user_input)
            
            if extracted_numbers:
                user_answer = int(extracted_numbers[0])
                is_correct = user_answer == correct_answer
                
                # Calculate confidence based on closeness
                if is_correct:
                    confidence = 1.0
                elif abs(user_answer - correct_answer) == 1:
                    confidence = 0.5  # Close answer
                else:
                    confidence = 0.0
                
                return {
                    'is_correct': is_correct,
                    'user_answer': user_answer,
                    'confidence': confidence,
                    'success': True
                }
            
            return {
                'is_correct': False,
                'user_answer': None,
                'confidence': 0.0,
                'message': 'Could not understand the answer. Please try again!',
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Answer validation failed: {e}")
            return {
                'error': str(e),
                'success': False
            }
    
    def get_hint(self, question_type, params):
        """
        Get a hint for the current question
        
        Args:
            question_type: Type of question
            params: Question parameters
            
        Returns:
            Hint string
        """
        hints = {
            'greater_than': f"Think about which number is bigger. Count up from {params.get('a')} and see if you reach {params.get('b')}!",
            'less_than': f"Which number is smaller? Count down and see which comes first!",
            'simple_addition': f"Try counting with your fingers! Start at {params.get('a')} and add {params.get('b')} more.",
            'simple_subtraction': f"Start with {params.get('a')} and take away {params.get('b')}. What's left?",
            'what_comes_after': f"What number comes right after {params.get('num')} when you count?",
            'what_comes_before': f"What number comes right before {params.get('num')} when you count?",
        }
        
        return hints.get(question_type, "Think carefully and try your best!")
    
    def get_feedback_message(self, is_correct, confidence, correct_answer):
        """
        Generate appropriate feedback message
        
        Args:
            is_correct: Whether answer was correct
            confidence: Confidence score
            correct_answer: The correct answer
            
        Returns:
            Dictionary with feedback message and styling
        """
        if is_correct:
            messages = [
                "Perfect! Great job!",
                "Excellent! You got it right!",
                "Amazing! Well done!",
                "Fantastic! Keep it up!"
            ]
            return {
                'message': random.choice(messages),
                'type': 'success',
                'color': '#4caf50'
            }
        elif confidence > 0:
            return {
                'message': f"So close! The answer was {correct_answer}. Try again!",
                'type': 'close',
                'color': '#ff9800'
            }
        else:
            return {
                'message': f"Not quite! The correct answer is {correct_answer}. Let's try another one!",
                'type': 'incorrect',
                'color': '#f44336'
            }