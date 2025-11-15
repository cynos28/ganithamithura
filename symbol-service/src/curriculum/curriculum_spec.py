"""
Curriculum Specification for Math Tutor

Defines learning progressions for Grades 1-3 with detailed constraints
for each level and sublevel (Starter, Explorer, Solver, Champion).

Each specification includes:
- Operand ranges
- Result/product ranges
- Operation types allowed
- Examples
- BODMAS rule application
"""

CURRICULUM = {
    'GRADE_01': {
        'name': 'Grade 1 - Single Digit Addition',
        'Level_1': {
            'Starter': {
                'description': 'Basic single-step addition with small numbers',
                'operations': ['+'],
                'addends_max': 5,
                'result_max': 7,
                'result_min': 0,
                'examples': ['2 + 3 = 5', '1 + 4 = 5'],
                'focus': 'Small combinations, reinforcing basic facts'
            },
            'Explorer': {
                'description': 'Addition patterns - doubles and near-doubles',
                'operations': ['+'],
                'addends_max': 8,
                'result_max': 9,
                'result_min': 5,
                'examples': ['3 + 4 = 7', '4 + 4 = 8'],
                'focus': 'Doubles, near-doubles, pattern recognition'
            },
            'Solver': {
                'description': 'Addition combining numbers up to 11',
                'operations': ['+'],
                'addends_max': 9,
                'result_max': 11,
                'result_min': 5,
                'examples': ['7 + 3 = 10', '6 + 5 = 11'],
                'focus': 'Building larger facts, number combinations'
            },
            'Champion': {
                'description': 'Addition building up to 14 with strategy paths',
                'operations': ['+'],
                'addends_max': 9,
                'result_max': 14,
                'result_min': 10,
                'examples': ['8 + 6 = 14', '7 + 5 = 12'],
                'focus': 'Near-doubles, make 10 strategies'
            }
        },
        'Level_2': {
            'Starter': {
                'description': 'One unknown in addition equations',
                'operations': ['+', 'unknown_addend'],
                'operand_max': 15,
                'result_max': 15,
                'examples': ['□ + 4 = 9'],
                'focus': 'Missing addend problems, number sense'
            },
            'Explorer': {
                'description': 'Addition crossing 10 with larger addends',
                'operations': ['+'],
                'addends_min': 5,
                'addends_max': 9,
                'result_max': 15,
                'result_min': 12,
                'examples': ['9 + 6 = 15'],
                'focus': 'Crossing 10, decade boundaries'
            },
            'Solver': {
                'description': 'Three-addend problems with grouping',
                'operations': ['+', '+'],  # Three addends
                'addends_max': 9,
                'result_max': 15,
                'examples': ['4 + 5 + 3 = 12'],
                'focus': 'Grouping, combination reasoning'
            },
            'Champion': {
                'description': 'Larger combinations reaching 17',
                'operations': ['+'],
                'addends_max': 10,
                'addends_min': 6,
                'result_max': 17,
                'result_min': 10,
                'examples': ['9 + 8 = 17', '10 + 5 = 15'],
                'focus': 'Larger facts, maintaining difficulty'
            }
        },
        'Level_3': {
            'Starter': {
                'description': 'Missing addend with higher targets',
                'operations': ['+', 'unknown_addend'],
                'addends_min': 5,
                'addends_max': 10,
                'result_max': 18,
                'examples': ['□ + 8 = 16'],
                'focus': 'Backward reasoning, higher totals'
            },
            'Explorer': {
                'description': 'Two-addend combinations with larger numbers',
                'operations': ['+'],
                'addends_max': 10,
                'addends_min': 8,
                'result_max': 20,
                'examples': ['8 + 8 = 16', '8 + 9 = 17'],
                'focus': 'Doubles, near-doubles at higher range'
            },
            'Solver': {
                'description': 'Three-number addition approaching 20',
                'operations': ['+', '+'],
                'addends_max': 9,
                'result_max': 20,
                'examples': ['6 + 7 + 5 = 18'],
                'focus': 'Grouping to 10, multiple addends'
            },
            'Champion': {
                'description': 'Target 20 with missing numbers',
                'operations': ['+', 'unknown_addend'],
                'result_target': 20,
                'missing_max': 12,
                'examples': ['□ + 9 = 20', '8 + 7 + □ = 20'],
                'focus': 'Backward reasoning, target completion'
            }
        }
    },
    'GRADE_02': {
        'name': 'Grade 2 - Multi-digit and Multiplication Intro',
        'Level_1': {
            'Starter': {
                'description': 'Single-step addition and subtraction (0-20)',
                'operations': ['+', '-'],
                'operand_max': 20,
                'result_max': 20,
                'examples': ['6 + 8 = 14', '17 − 9 = 8'],
                'focus': 'Inverse operations, linking add/subtract'
            },
            'Explorer': {
                'description': 'Multiplication as repeated addition',
                'operations': ['×'],
                'factors_max': 5,
                'product_max': 30,
                'examples': ['3 × 4 = 12', '5 × 2 = 10'],
                'focus': 'Equal groups, conceptual understanding'
            },
            'Solver': {
                'description': 'Mixed operations with comparison symbols',
                'operations': ['+', '-', '×', '>', '<', '='],
                'operand_max': 30,
                'result_max': 40,
                'examples': ['6 × 3 > 18 − 4'],
                'focus': 'Relational reasoning, mixed operations'
            },
            'Champion': {
                'description': 'Two-step equations combining operations',
                'operations': ['+', '-', '×'],
                'operand_max': 20,
                'result_max': 30,
                'examples': ['(3 × 4) + 8 = 20', '18 − (2 × 3) = 12'],
                'focus': 'BODMAS application, operation sequencing'
            }
        },
        'Level_2': {
            'Starter': {
                'description': 'Two-digit addition/subtraction with regrouping',
                'operations': ['+', '-'],
                'operand_max': 30,
                'result_max': 50,
                'examples': ['27 + 14 = 41', '45 − 19 = 26'],
                'focus': 'Place value, carrying and borrowing'
            },
            'Explorer': {
                'description': 'Multiplication tables 2-10',
                'operations': ['×'],
                'factors_max': 10,
                'product_max': 50,
                'examples': ['6 × 5 = 30', '10 × 4 = 40'],
                'focus': 'Memorization, commutative pairs'
            },
            'Solver': {
                'description': 'Comparing two expressions with symbols',
                'operations': ['+', '-', '×', '>', '<', '='],
                'operand_max': 30,
                'result_max': 50,
                'examples': ['24 − 9 > 4 × 4'],
                'focus': 'Magnitude understanding, relational reasoning'
            },
            'Champion': {
                'description': 'Mixed multi-operation equations',
                'operations': ['+', '-', '×'],
                'operand_max': 50,
                'result_max': 60,
                'examples': ['(8 × 3) − 10 = 14', '(6 × 4) + 12 = 36'],
                'focus': 'Operation sequencing, logical linking'
            }
        },
        'Level_3': {
            'Starter': {
                'description': 'Two-digit addition/subtraction with regrouping',
                'operations': ['+', '-'],
                'operand_max': 70,
                'result_max': 100,
                'examples': ['64 + 27 = 91', '95 − 38 = 57'],
                'focus': 'Place-value accuracy, tens crossing'
            },
            'Explorer': {
                'description': 'Multiplication table mastery (2-10)',
                'operations': ['×'],
                'factors_max': 10,
                'product_max': 100,
                'examples': ['9 × 7 = 63', '8 × 9 = 72'],
                'focus': 'Full table fluency, up to 100'
            },
            'Solver': {
                'description': 'Comparing multiplication and addition',
                'operations': ['+', '×', '>', '<', '='],
                'operand_max': 12,
                'result_max': 100,
                'examples': ['6 × 9 = 54', '7 × 8 > 60'],
                'focus': 'Arithmetic and relational reasoning'
            },
            'Champion': {
                'description': 'Multi-operation fluency with BODMAS',
                'operations': ['+', '-', '×'],
                'operand_max': 20,
                'result_max': 100,
                'examples': ['(5 × 8) − 14 = 26', '(6 × 7) + 12 = 54'],
                'focus': 'Order of operations, balanced range'
            }
        }
    },
    'GRADE_03': {
        'name': 'Grade 3 - Extended Multi-digit and Complex Operations',
        'Level_1': {
            'Starter': {
                'description': 'Multi-digit addition/subtraction with regrouping',
                'operations': ['+', '-'],
                'operand_max': 50,
                'result_max': 60,
                'examples': ['34 + 27 = 61', '56 − 18 = 38'],
                'focus': 'Tens and ones movement, regrouping'
            },
            'Explorer': {
                'description': 'Multiplication tables 6-9',
                'operations': ['×'],
                'factors_max': 9,
                'factors_min': 6,
                'product_max': 81,
                'examples': ['6 × 7 = 42', '8 × 9 = 72'],
                'focus': 'Weak area identification, fluency'
            },
            'Solver': {
                'description': 'Comparison symbols with computed results',
                'operations': ['+', '-', '×', '>', '<', '='],
                'operand_max': 50,
                'result_max': 60,
                'examples': ['3 × 9 > 28', '45 − 8 = 37'],
                'focus': 'Computed comparison, symbol application'
            },
            'Champion': {
                'description': 'Multi-operation integration in equations',
                'operations': ['+', '-', '×'],
                'operand_max': 30,
                'result_max': 60,
                'examples': ['(5 × 6) − 10 = 20', '(3 × 9) + 12 = 39'],
                'focus': 'Structured reasoning, operation integration'
            }
        },
        'Level_2': {
            'Starter': {
                'description': 'Addition and subtraction within 80',
                'operations': ['+', '-'],
                'operand_max': 70,
                'result_max': 80,
                'examples': ['64 + 13 = 77', '75 − 19 = 56'],
                'focus': 'Extended range, regrouping fluency'
            },
            'Explorer': {
                'description': 'Multiplication and addition in comparisons',
                'operations': ['+', '×', '>', '<', '='],
                'factors_max': 10,
                'product_max': 80,
                'examples': ['8 × 6 > 50', '9 × 7 < 70'],
                'focus': 'Multi-operation understanding'
            },
            'Solver': {
                'description': 'Three-operation equations with order',
                'operations': ['+', '-', '×'],
                'operand_max': 30,
                'result_max': 80,
                'examples': ['(9 × 4) − 16 + 8 = 28'],
                'focus': 'BODMAS compliance, partial result tracking'
            },
            'Champion': {
                'description': 'Estimation and multi-step verification',
                'operations': ['+', '-', '×'],
                'operand_max': 15,
                'result_max': 80,
                'examples': ['(5 × 6) + 8 = 38'],
                'focus': 'Prediction, estimation, verification'
            }
        },
        'Level_3': {
            'Starter': {
                'description': 'Addition/subtraction near 100 with regrouping',
                'operations': ['+', '-'],
                'operand_max': 90,
                'result_max': 100,
                'examples': ['58 + 37 = 95', '94 − 28 = 66'],
                'focus': 'Multi-place regrouping, 100 boundary'
            },
            'Explorer': {
                'description': 'Two-digit × one-digit multiplication',
                'operations': ['×'],
                'multiplicand_max': 20,
                'multiplier_max': 10,
                'product_max': 100,
                'examples': ['12 × 8 = 96', '9 × 9 = 81'],
                'focus': 'Extended tables, multiplicand extension'
            },
            'Solver': {
                'description': 'Mixed operations determining final result',
                'operations': ['+', '-', '×'],
                'operand_max': 20,
                'result_max': 100,
                'examples': ['(7 × 8) − 24 = 32', '9 × 5 + 15 = 60'],
                'focus': 'All operations integration, BODMAS'
            },
            'Champion': {
                'description': 'Multi-step equations targeting 100',
                'operations': ['+', '-', '×'],
                'operand_max': 20,
                'result_approx': 100,
                'examples': ['(6 × 9) + (8 × 6) = 102', '(9 × 8) + 25 = 97'],
                'focus': 'Complex reasoning, 100 target approximation'
            }
        }
    }
}

def get_curriculum_spec(grade: str, level: int, sublevel: str) -> dict:
    """
    Get curriculum specification for a student profile.

    Args:
        grade: 'GRADE_01', 'GRADE_02', or 'GRADE_03'
        level: 1, 2, or 3
        sublevel: 'Starter', 'Explorer', 'Solver', or 'Champion'

    Returns:
        Dictionary with curriculum specification and constraints
    """
    try:
        grade_key = f'GRADE_{grade.zfill(2)}'
        level_key = f'Level_{level}'

        spec = CURRICULUM.get(grade_key, {}).get(level_key, {}).get(sublevel, {})

        if spec:
            return spec
        else:
            raise ValueError(f"Invalid curriculum spec: {grade}/{level}/{sublevel}")

    except Exception as e:
        print(f"Error fetching curriculum: {e}")
        return {}

def get_bodmas_rules() -> dict:
    """
    Get BODMAS (order of operations) rules.

    Returns:
        Dictionary defining operation order and rules
    """
    return {
        'order': ['Brackets', 'Orders (Powers)', 'Division', 'Multiplication', 'Addition', 'Subtraction'],
        'acronym': 'BODMAS',
        'description': 'Order of operations to follow when solving equations',
        'rules': {
            'Brackets': 'Solve expressions inside brackets first',
            'Orders': 'Apply powers and roots',
            'Division': 'Division and multiplication are equal priority (left to right)',
            'Multiplication': 'Multiplication and division are equal priority (left to right)',
            'Addition': 'Addition and subtraction are equal priority (left to right)',
            'Subtraction': 'Subtraction follows addition with same priority'
        }
    }

if __name__ == "__main__":
    # Test curriculum retrieval
    print("Testing Curriculum Specification")
    print("=" * 50)

    # Example: Grade 1, Level 2, Starter
    spec = get_curriculum_spec('01', 2, 'Starter')
    print(f"\nGrade 1, Level 2, Starter:")
    print(f"Description: {spec.get('description')}")
    print(f"Operand Max: {spec.get('result_max')}")
    print(f"Examples: {spec.get('examples')}")

    # Example: Grade 3, Level 3, Champion
    spec = get_curriculum_spec('03', 3, 'Champion')
    print(f"\nGrade 3, Level 3, Champion:")
    print(f"Description: {spec.get('description')}")
    print(f"Examples: {spec.get('examples')}")

    # BODMAS rules
    bodmas = get_bodmas_rules()
    print(f"\nBODMAS Order: {' → '.join(bodmas['order'])}")
