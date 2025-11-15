"""
Curriculum-Based Question Generator

Generates math questions aligned with Grade/Level/Sublevel specifications.
Ensures generated questions comply with operand ranges and result constraints.
"""

import random
import re
from typing import Dict, List, Optional
from .curriculum_spec import get_curriculum_spec, CURRICULUM

class CurriculumQuestionGenerator:
    """Generate math questions based on curriculum specifications."""

    def __init__(self, grade: str, level: int, sublevel: str):
        """
        Initialize with student profile.

        Args:
            grade: '01', '02', or '03'
            level: 1, 2, or 3
            sublevel: 'Starter', 'Explorer', 'Solver', or 'Champion'
        """
        self.grade = grade
        self.level = level
        self.sublevel = sublevel
        self.spec = get_curriculum_spec(grade, level, sublevel)

        if not self.spec:
            raise ValueError(f"Invalid profile: Grade {grade}, Level {level}, {sublevel}")

        self.recent_questions = []
        self.max_recent = 10

    def generate_question(self) -> Dict:
        """
        Generate a question based on curriculum spec.

        Returns:
            Dictionary with question, expression, answer, and metadata
        """
        operations = self.spec.get('operations', ['+'])
        operation = random.choice(operations)

        # Handle different operation types
        if operation == '+':
            return self._generate_addition()
        elif operation == '-':
            return self._generate_subtraction()
        elif operation == '×':
            return self._generate_multiplication()
        elif operation == 'unknown_addend':
            return self._generate_unknown_addend()
        else:
            return self._generate_addition()

    def _generate_addition(self) -> Dict:
        """Generate addition question within spec constraints."""
        spec = self.spec

        # Handle single or multiple addends
        if 'addends_max' in spec:
            addends_max = spec.get('addends_max', 10)
            addends_min = spec.get('addends_min', 0)
            result_max = spec.get('result_max', 20)
            result_min = spec.get('result_min', 0)

            # Check if three addends (by operation count)
            if spec.get('operations', []).count('+') >= 2:
                return self._generate_three_addend(addends_max, result_max)

            # Two addends
            a = random.randint(addends_min, addends_max)
            b = random.randint(addends_min, addends_max)

            # Ensure result is within limits
            while a + b > result_max or a + b < result_min:
                a = random.randint(addends_min, addends_max)
                b = random.randint(addends_min, addends_max)

            answer = a + b
            return {
                'question': f"{a} plus {b}",
                'expression': f"{a} + {b}",
                'answer': answer,
                'operation': '+',
                'operands': [a, b],
                'grade': self.grade,
                'level': self.level,
                'sublevel': self.sublevel
            }

        return {}

    def _generate_subtraction(self) -> Dict:
        """Generate subtraction question within spec constraints."""
        spec = self.spec
        operand_max = spec.get('operand_max', 20)
        result_max = spec.get('result_max', 20)

        # Subtraction: a - b = c, where c is answer
        b = random.randint(0, min(operand_max // 2, 10))
        a = random.randint(b, operand_max)

        answer = a - b
        while answer > result_max:
            a = random.randint(b, operand_max)
            answer = a - b

        return {
            'question': f"{a} minus {b}",
            'expression': f"{a} − {b}",
            'answer': answer,
            'operation': '-',
            'operands': [a, b],
            'grade': self.grade,
            'level': self.level,
            'sublevel': self.sublevel
        }

    def _generate_multiplication(self) -> Dict:
        """Generate multiplication question within spec constraints."""
        spec = self.spec

        if 'multiplicand_max' in spec:
            # Two-digit × one-digit
            multiplicand = random.randint(10, spec.get('multiplicand_max', 20))
            multiplier = random.randint(2, spec.get('multiplier_max', 10))
        else:
            # Single digit × single digit
            factors_max = spec.get('factors_max', 10)
            factors_min = spec.get('factors_min', 2)
            multiplicand = random.randint(factors_min, factors_max)
            multiplier = random.randint(factors_min, factors_max)

        answer = multiplicand * multiplier
        product_max = spec.get('product_max', 100)

        # Ensure within range
        while answer > product_max:
            if 'multiplicand_max' in spec:
                multiplicand = random.randint(10, spec.get('multiplicand_max', 20))
            else:
                multiplicand = random.randint(spec.get('factors_min', 2), spec.get('factors_max', 10))
            answer = multiplicand * multiplier

        return {
            'question': f"{multiplicand} times {multiplier}",
            'expression': f"{multiplicand} × {multiplier}",
            'answer': answer,
            'operation': '×',
            'operands': [multiplicand, multiplier],
            'grade': self.grade,
            'level': self.level,
            'sublevel': self.sublevel
        }

    def _generate_three_addend(self, addends_max: int, result_max: int) -> Dict:
        """Generate three-addend addition question."""
        a = random.randint(2, addends_max)
        b = random.randint(2, addends_max)
        c = random.randint(1, addends_max)

        total = a + b + c
        while total > result_max:
            c = random.randint(1, addends_max)
            total = a + b + c

        return {
            'question': f"{a} plus {b} plus {c}",
            'expression': f"{a} + {b} + {c}",
            'answer': total,
            'operation': '+',
            'operands': [a, b, c],
            'grade': self.grade,
            'level': self.level,
            'sublevel': self.sublevel
        }

    def _generate_unknown_addend(self) -> Dict:
        """Generate missing addend question (□ + a = b)."""
        spec = self.spec
        result_max = spec.get('result_max', 20)
        addends_min = spec.get('addends_min', 0)
        addends_max = spec.get('addends_max', 10)

        # b = target answer
        b = random.randint(5, result_max)

        # a = known addend
        a = random.randint(addends_min, min(addends_max, b))

        # unknown = b - a
        unknown = b - a

        return {
            'question': f"□ plus {a} equals {b}",
            'expression': f"□ + {a} = {b}",
            'answer': unknown,
            'operation': 'unknown_addend',
            'known_operand': a,
            'target': b,
            'grade': self.grade,
            'level': self.level,
            'sublevel': self.sublevel
        }

    def validate_question(self, question: Dict) -> bool:
        """
        Validate question against curriculum spec.

        Args:
            question: Generated question dictionary

        Returns:
            True if valid, False otherwise
        """
        spec = self.spec
        answer = question.get('answer', 0)
        operands = question.get('operands', [])

        # Check result limits
        result_max = spec.get('result_max')
        result_min = spec.get('result_min', 0)

        if result_max and answer > result_max:
            return False

        if answer < result_min:
            return False

        # Check operand limits
        if operands:
            addends_max = spec.get('addends_max')
            if addends_max and any(op > addends_max for op in operands):
                return False

        return True

    def get_spec_info(self) -> Dict:
        """
        Get curriculum spec information for this profile.

        Returns:
            Dictionary with spec details
        """
        return {
            'grade': self.grade,
            'level': self.level,
            'sublevel': self.sublevel,
            'description': self.spec.get('description'),
            'operations': self.spec.get('operations', []),
            'examples': self.spec.get('examples', []),
            'focus': self.spec.get('focus', '')
        }

if __name__ == "__main__":
    # Test question generation
    print("Testing Curriculum-Based Question Generation")
    print("=" * 60)

    # Test Grade 1, Level 1, Starter
    gen = CurriculumQuestionGenerator('01', 1, 'Starter')
    print(f"\nGrade 1, Level 1, Starter")
    print(f"Focus: {gen.get_spec_info()['focus']}")

    for i in range(3):
        q = gen.generate_question()
        print(f"  Q{i+1}: {q['expression']} = {q['answer']}")

    # Test Grade 2, Level 2, Explorer
    gen = CurriculumQuestionGenerator('02', 2, 'Explorer')
    print(f"\nGrade 2, Level 2, Explorer")
    print(f"Focus: {gen.get_spec_info()['focus']}")

    for i in range(3):
        q = gen.generate_question()
        print(f"  Q{i+1}: {q['expression']} = {q['answer']}")

    # Test Grade 3, Level 3, Champion
    gen = CurriculumQuestionGenerator('03', 3, 'Champion')
    print(f"\nGrade 3, Level 3, Champion")
    print(f"Focus: {gen.get_spec_info()['focus']}")

    for i in range(3):
        q = gen.generate_question()
        print(f"  Q{i+1}: {q['expression']} = {q['answer']}")

    print("\n" + "=" * 60)
