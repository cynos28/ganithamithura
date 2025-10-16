
import random
import logging

logger = logging.getLogger(__name__)


class ProblemGenerationService:    
    PROBLEM_TYPES = [
        {
            'type': 'sequence_after',
            'template': 'What comes after {num}?',
            'generator': lambda: random.randint(0, 8),
            'answer_func': lambda x: x + 1
        },
        {
            'type': 'sequence_before',
            'template': 'What comes before {num}?',
            'generator': lambda: random.randint(1, 9),
            'answer_func': lambda x: x - 1
        },
        {
            'type': 'addition_simple',
            'template': '{a} + {b} = ?',
            'generator': lambda: (random.randint(0, 5), random.randint(0, 4)),
            'answer_func': lambda x: x[0] + x[1]
        },
        {
            'type': 'subtraction_simple',
            'template': '{a} - {b} = ?',
            'generator': lambda: (random.randint(2, 9), random.randint(0, 2)),
            'answer_func': lambda x: x[0] - x[1]
        }
    ]
    
    def generate_problem(self, max_retries=10):
        """
        Generate a random math problem
        
        Args:
            max_retries: Maximum retries if answer is out of range
            
        Returns:
            Dictionary with question, answer, and type
        """
        for _ in range(max_retries):
            try:
                problem_type = random.choice(self.PROBLEM_TYPES)
                
                if problem_type['type'].startswith('sequence'):
                    num = problem_type['generator']()
                    question = problem_type['template'].format(num=num)
                    answer = problem_type['answer_func'](num)
                else:
                    a, b = problem_type['generator']()
                    question = problem_type['template'].format(a=a, b=b)
                    answer = problem_type['answer_func']((a, b))
                
                # Ensure answer is within valid range (0-9)
                if 0 <= answer <= 9:
                    return {
                        'question': question,
                        'answer': answer,
                        'type': problem_type['type'],
                        'success': True
                    }
                    
            except Exception as e:
                logger.error(f"Problem generation error: {e}")
                continue
        
        # Fallback to a simple problem if retries exhausted
        return {
            'question': 'What comes after 3?',
            'answer': 4,
            'type': 'sequence_after',
            'success': True
        }