"""
Curriculum Helper Module

Provides:
- Curriculum specifications for all grades/levels
- Question generation constraints
- Operand and result validation

Used by all tutors to ensure curriculum alignment.
"""

from typing import Dict, Optional


class CurriculumHelper:
    """Helper class for curriculum specifications and constraints."""

    # Curriculum specifications for all grades and levels
    SPECS = {
        1: {  # Grade 1
            1: {  # Level 1
                "Starter": {
                    "operations": ["addition"],
                    "operand_max": 5,
                    "result_max": 7,
                    "focus": "Small combinations totaling no higher than 7"
                },
                "Explorer": {
                    "operations": ["addition", "doubles"],
                    "operand_max": 8,
                    "result_min": 5,
                    "result_max": 9,
                    "focus": "Doubles and near-doubles patterns"
                },
                "Solver": {
                    "operations": ["addition"],
                    "operand_max": 9,
                    "result_max": 11,
                    "focus": "Combining numbers reaching up to 11"
                },
                "Champion": {
                    "operations": ["addition"],
                    "operand_max": 9,
                    "result_min": 10,
                    "result_max": 14,
                    "focus": "Building larger facts up to 14"
                }
            },
            2: {  # Level 2
                "Starter": {
                    "operations": ["addition", "missing_addend"],
                    "operand_max": 15,
                    "result_max": 15,
                    "focus": "One unknown in addition equations"
                },
                "Explorer": {
                    "operations": ["addition"],
                    "operand_min": 5,
                    "operand_max": 9,
                    "result_min": 12,
                    "result_max": 15,
                    "focus": "Addition crossing 10"
                },
                "Solver": {
                    "operations": ["three_addend"],
                    "operand_max": 9,
                    "result_max": 15,
                    "focus": "Three-addend problems with grouping"
                },
                "Champion": {
                    "operations": ["addition"],
                    "operand_min": 6,
                    "operand_max": 10,
                    "result_min": 10,
                    "result_max": 17,
                    "focus": "Larger combinations up to 17"
                }
            },
            3: {  # Level 3
                "Starter": {
                    "operations": ["addition", "missing_addend"],
                    "operand_min": 5,
                    "operand_max": 10,
                    "result_max": 18,
                    "focus": "Missing addend with higher targets"
                },
                "Explorer": {
                    "operations": ["addition", "doubles"],
                    "operand_max": 10,
                    "operand_min": 8,
                    "result_max": 20,
                    "focus": "Two-addend with large numbers"
                },
                "Solver": {
                    "operations": ["three_addend"],
                    "operand_max": 9,
                    "result_max": 20,
                    "focus": "Three-addend approaching 20"
                },
                "Champion": {
                    "operations": ["addition", "missing_addend"],
                    "result_target": 20,
                    "focus": "Target 20 with missing numbers"
                }
            }
        },
        2: {  # Grade 2
            1: {  # Level 1
                "Starter": {
                    "operations": ["addition", "subtraction"],
                    "operand_max": 20,
                    "result_max": 20,
                    "focus": "Single-step add/subtract (≤20)"
                },
                "Explorer": {
                    "operations": ["multiplication"],
                    "factors_max": 5,
                    "product_max": 30,
                    "focus": "Multiplication as repeated addition"
                },
                "Solver": {
                    "operations": ["addition", "subtraction", "multiplication"],
                    "operand_max": 30,
                    "result_max": 40,
                    "focus": "Mixed operations with comparisons"
                },
                "Champion": {
                    "operations": ["addition", "subtraction", "multiplication", "brackets"],
                    "operand_max": 20,
                    "result_max": 30,
                    "focus": "Two-step equations with BODMAS"
                }
            },
            2: {  # Level 2
                "Starter": {
                    "operations": ["addition", "subtraction"],
                    "operand_max": 30,
                    "result_max": 50,
                    "focus": "Two-digit with regrouping"
                },
                "Explorer": {
                    "operations": ["multiplication"],
                    "factors_max": 10,
                    "product_max": 50,
                    "focus": "Multiplication tables 2-10"
                },
                "Solver": {
                    "operations": ["addition", "subtraction", "multiplication"],
                    "operand_max": 30,
                    "result_max": 50,
                    "focus": "Comparing expressions"
                },
                "Champion": {
                    "operations": ["addition", "subtraction", "multiplication", "brackets"],
                    "operand_max": 50,
                    "result_max": 60,
                    "focus": "Multi-operation with BODMAS"
                }
            },
            3: {  # Level 3
                "Starter": {
                    "operations": ["addition", "subtraction"],
                    "operand_max": 70,
                    "result_max": 100,
                    "focus": "Two-digit with regrouping near 100"
                },
                "Explorer": {
                    "operations": ["multiplication"],
                    "factors_max": 10,
                    "product_max": 100,
                    "focus": "Full multiplication mastery 2-10"
                },
                "Solver": {
                    "operations": ["addition", "subtraction", "multiplication"],
                    "operand_max": 12,
                    "result_max": 100,
                    "focus": "Comparing multiplication and addition"
                },
                "Champion": {
                    "operations": ["addition", "subtraction", "multiplication", "brackets"],
                    "operand_max": 20,
                    "result_max": 100,
                    "focus": "Multi-operation fluency with BODMAS"
                }
            }
        },
        3: {  # Grade 3
            1: {  # Level 1
                "Starter": {
                    "operations": ["addition", "subtraction"],
                    "operand_max": 50,
                    "result_max": 60,
                    "focus": "Multi-digit add/subtract with regrouping"
                },
                "Explorer": {
                    "operations": ["multiplication"],
                    "factors_min": 6,
                    "factors_max": 9,
                    "product_max": 81,
                    "focus": "Multiplication tables 6-9"
                },
                "Solver": {
                    "operations": ["addition", "subtraction", "multiplication"],
                    "operand_max": 50,
                    "result_max": 60,
                    "focus": "Comparison with computed results"
                },
                "Champion": {
                    "operations": ["addition", "subtraction", "multiplication", "brackets"],
                    "operand_max": 30,
                    "result_max": 60,
                    "focus": "Multi-operation integration"
                }
            },
            2: {  # Level 2
                "Starter": {
                    "operations": ["addition", "subtraction"],
                    "operand_max": 70,
                    "result_max": 80,
                    "focus": "Add/subtract within 80 range"
                },
                "Explorer": {
                    "operations": ["addition", "multiplication"],
                    "factors_max": 10,
                    "product_max": 80,
                    "focus": "Multiplication with addition comparisons"
                },
                "Solver": {
                    "operations": ["addition", "subtraction", "multiplication", "brackets"],
                    "operand_max": 30,
                    "result_max": 80,
                    "focus": "Three-operation with BODMAS"
                },
                "Champion": {
                    "operations": ["addition", "subtraction", "multiplication"],
                    "operand_max": 15,
                    "result_max": 80,
                    "focus": "Estimation and multi-step"
                }
            },
            3: {  # Level 3
                "Starter": {
                    "operations": ["addition", "subtraction"],
                    "operand_max": 90,
                    "result_max": 100,
                    "focus": "Add/subtract near 100 with regrouping"
                },
                "Explorer": {
                    "operations": ["multiplication"],
                    "multiplicand_max": 20,
                    "multiplier_max": 10,
                    "product_max": 100,
                    "focus": "Two-digit × one-digit"
                },
                "Solver": {
                    "operations": ["addition", "subtraction", "multiplication", "brackets"],
                    "operand_max": 20,
                    "result_max": 100,
                    "focus": "Mixed operations with BODMAS"
                },
                "Champion": {
                    "operations": ["addition", "subtraction", "multiplication", "brackets"],
                    "operand_max": 20,
                    "result_approx": 100,
                    "focus": "Multi-step targeting ≈100"
                }
            }
        }
    }

    @staticmethod
    def get_spec(grade: int, level: int, sublevel: str) -> Dict:
        """
        Get curriculum specification for a student profile.

        Args:
            grade: 1, 2, or 3
            level: 1, 2, or 3
            sublevel: Starter, Explorer, Solver, or Champion

        Returns:
            Curriculum specification dictionary
        """
        return CurriculumHelper.SPECS.get(grade, {}).get(level, {}).get(sublevel, {})

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
