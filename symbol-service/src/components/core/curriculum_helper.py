"""
Curriculum Helper Module

Provides:
- Curriculum specifications for all grades/levels
- Question generation constraints
- Operand and result validation

Uses curriculum_spec.py as the source of truth for curriculum data.
"""

import os
import sys
from typing import Dict, Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from curriculum.curriculum_spec import get_curriculum_spec, CURRICULUM


class CurriculumHelper:
    """Helper class for curriculum specifications and constraints."""

    # Convert curriculum_spec format to legacy SPECS format for backward compatibility
    @staticmethod
    def _convert_spec_format(grade: int, level: int, sublevel: str) -> Dict:
        """
        Convert from curriculum_spec.py format to legacy format.

        Args:
            grade: 1, 2, or 3
            level: 1, 2, or 3
            sublevel: Starter, Explorer, Solver, or Champion

        Returns:
            Specification dictionary in legacy format
        """
        try:
            grade_key = f'GRADE_{grade:02d}'
            level_key = f'Level_{level}'

            spec = CURRICULUM.get(grade_key, {}).get(level_key, {}).get(sublevel, {})

            if not spec:
                return {}

            # Convert spec to legacy format with unexpected keys preserved for prompts
            converted = {
                'focus': spec.get('focus', ''),
                'what_is_taught': spec.get('what_is_taught', ''),
                'students_should_understand': spec.get('students_should_understand', []),
                'what_should_teach': spec.get('what_should_teach', ''),
                'operations': spec.get('operations', ['addition']),
                # Narrative Spec Passthrough
                'narrative_intro': spec.get('narrative_intro'),
                'story_1_guide': spec.get('story_1_guide'),
                'story_2_guide': spec.get('story_2_guide'),
                'conclusion_guide': spec.get('conclusion_guide'),
            }

            # Map operand fields
            converted['operand_min'] = spec.get('addends_min', spec.get('operand_min', 0))
            converted['operand_max'] = spec.get('addends_max', spec.get('operand_max', 10))

            # Map result fields
            converted['result_min'] = spec.get('result_min', 0)
            converted['result_max'] = spec.get('result_max', spec.get('product_max', 20))
            
            # Map legacy addends_max for backward compat in validations
            converted['addends_max'] = converted['operand_max']

            return converted
        except Exception as e:
            print(f"Error converting spec: {e}")
            return {}

    @staticmethod
    def get_spec(grade: int, level: int, sublevel: str) -> Dict:
        """
        Get curriculum specification for a student profile.
        Retrieves from curriculum_spec.py as source of truth.

        Args:
            grade: 1, 2, or 3
            level: 1, 2, or 3
            sublevel: Starter, Explorer, Solver, or Champion

        Returns:
            Curriculum specification dictionary
        """
        return CurriculumHelper._convert_spec_format(grade, level, sublevel)

    @staticmethod
    def validate_operands(value: int, spec: Dict) -> bool:
        """
        Validate if operand is within curriculum range.

        Args:
            value: Operand value
            spec: Curriculum specification

        Returns:
            True if valid, False otherwise
        """
        min_val = spec.get('operand_min', 0)
        max_val = spec.get('operand_max', 20)
        return min_val <= value <= max_val

    @staticmethod
    def validate_result(value: int, spec: Dict) -> bool:
        """
        Validate if result is within curriculum range.

        Args:
            value: Result value
            spec: Curriculum specification

        Returns:
            True if valid, False otherwise
        """
        min_val = spec.get('result_min', 0)
        max_val = spec.get('result_max', 20)
        return min_val <= value <= max_val
