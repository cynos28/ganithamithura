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
                'result_max': 5,
                'result_min': 0,
                'examples': ['2 + 3 = 5', '1 + 4 = 5'],
                'focus': 'Introduce addition as joining two small groups.',
                'what_is_taught': 'Students learn that addition begins by combining two separate groups to form a bigger group. They observe that joining always increases the total quantity.',
                'students_should_understand': [
                    'Addition means joining',
                    'Joining makes the group bigger',
                    'The plus (+) symbol represents joining'
                ],
                'what_should_teach': 'Explain addition as joining two small groups. Use very simple language and examples up to 5. Focus only on meaning, not calculation. Do not ask questions.'
            },
            'Explorer': {
                'description': 'Addition patterns - doubles and near-doubles',
                'operations': ['+'],
                'addends_max': 8,
                'result_max': 9,
                'result_min': 5,
                'examples': ['3 + 4 = 7', '4 + 4 = 8'],
                'focus': 'Recognize simple addition patterns.',
                'what_is_taught': 'Students learn about doubles and near-doubles, where similar number combinations repeat predictable patterns.',
                'students_should_understand': [
                    'Some additions repeat patterns',
                    'Doubles and near-doubles make addition easier'
                ],
                'what_should_teach': 'Explain doubles and near-doubles in addition. Use examples with totals below 9. Keep explanations short and friendly.'
            },
            'Solver': {
                'description': 'Addition combining numbers up to 11',
                'operations': ['+'],
                'addends_max': 9,
                'result_max': 11,
                'result_min': 5,
                'examples': ['7 + 3 = 10', '6 + 5 = 11'],
                'focus': 'Build totals near 10.',
                'what_is_taught': 'Students learn how numbers combine to reach 10 or slightly above, introducing early number flexibility.',
                'students_should_understand': [
                    '10 is an important reference number',
                    'Numbers can be grouped to reach 10'
                ],
                'what_should_teach': 'Explain how numbers can be added to make 10 first. Use examples up to 11. Do not include tasks or questions.'
            },
            'Champion': {
                'description': 'Addition building up to 14 with strategy paths',
                'operations': ['+'],
                'addends_max': 9,
                'result_max': 14,
                'result_min': 10,
                'examples': ['8 + 6 = 14', '7 + 5 = 12'],
                'focus': 'Flexible thinking in addition.',
                'what_is_taught': 'Students learn that the same total can be made in multiple ways using near-doubles and make 10 ideas.',
                'students_should_understand': [
                    'Addition is flexible',
                    'There is more than one way to reach a total'
                ],
                'what_should_teach': 'Explain flexible ways to make the same total. Use examples up to 14. Emphasize understanding over speed.'
            }
        },
        'Level_2': {
            'Starter': {
                'description': 'One unknown in addition equations',
                'operations': ['+', 'unknown_addend'],
                'operand_max': 15,
                'result_max': 15,
                'examples': ['□ + 4 = 9'],
                'focus': 'Introduce missing addends.',
                'what_is_taught': 'Students learn that addition can have an unknown part and that the missing number completes the total.',
                'students_should_understand': [
                    'Addition shows parts and a whole',
                    'A missing number can be found by reasoning'
                ],
                'what_should_teach': 'Explain missing-addend addition. Use examples like box plus number equals total. Focus on understanding parts and whole.'
            },
            'Explorer': {
                'description': 'Addition crossing 10 with larger addends',
                'operations': ['+'],
                'addends_min': 5,
                'addends_max': 9,
                'result_max': 15,
                'result_min': 12,
                'examples': ['9 + 6 = 15'],
                'focus': 'Crossing 10 with addition.',
                'what_is_taught': 'Students learn how addition moves past 10 into larger numbers and recognize when a sum crosses a decade boundary.',
                'students_should_understand': [
                    'Some additions go past 10',
                    'Crossing 10 changes number size'
                ],
                'what_should_teach': 'Explain what happens when addition crosses 10. Use examples with 8 or 9 as addends.'
            },
            'Solver': {
                'description': 'Three-addend problems with grouping',
                'operations': ['+', '+'],  # Three addends
                'addends_max': 9,
                'result_max': 15,
                'examples': ['4 + 5 + 3 = 12'],
                'focus': 'Three-number addition.',
                'what_is_taught': 'Students learn how three numbers can be combined by grouping them mentally.',
                'students_should_understand': [
                    'Numbers can be grouped in addition',
                    'Order does not change the total'
                ],
                'what_should_teach': 'Explain how three numbers can be added together. Focus on grouping numbers. Do not give exercises.'
            },
            'Champion': {
                'description': 'Larger combinations reaching 17',
                'operations': ['+'],
                'addends_max': 10,
                'addends_min': 6,
                'result_max': 17,
                'result_min': 10,
                'examples': ['9 + 8 = 17', '10 + 5 = 15'],
                'focus': 'Fluency with larger sums.',
                'what_is_taught': 'Students strengthen confidence with larger addition facts and prepare for higher reasoning.',
                'students_should_understand': [
                    'Larger numbers follow the same rules',
                    'Addition concepts stay consistent'
                ],
                'what_should_teach': 'Explain addition with larger numbers up to 17. Focus on confidence and understanding.'
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
                'focus': 'Missing addends with higher totals.',
                'what_is_taught': 'Students revisit missing numbers but with totals approaching 18.',
                'students_should_understand': [
                    'Missing numbers can be larger',
                    'Reasoning replaces counting'
                ],
                'what_should_teach': 'Explain missing-addend addition with larger totals. Use simple explanations.'
            },
            'Explorer': {
                'description': 'Two-addend combinations with larger numbers',
                'operations': ['+'],
                'addends_max': 10,
                'addends_min': 8,
                'result_max': 20,
                'examples': ['8 + 8 = 16', '8 + 9 = 17'],
                'focus': 'Upper-range addition patterns.',
                'what_is_taught': 'Students recognize doubles and near-doubles with higher numbers.',
                'students_should_understand': [
                    'Patterns still apply to bigger numbers'
                ],
                'what_should_teach': 'Explain higher-number doubles and near-doubles. Use examples near 20.'
            },
            'Solver': {
                'description': 'Three-number addition approaching 20',
                'operations': ['+', '+'],
                'addends_max': 9,
                'result_max': 20,
                'examples': ['6 + 7 + 5 = 18'],
                'focus': 'Three-number addition near 20.',
                'what_is_taught': 'Students learn to group numbers to approach 20.',
                'students_should_understand': [
                    'Grouping helps manage larger totals'
                ],
                'what_should_teach': 'Explain how three numbers can make totals near 20. Focus on grouping ideas.'
            },
            'Champion': {
                'description': 'Target 20 with missing numbers',
                'operations': ['+', 'unknown_addend'],
                'result_target': 20,
                'missing_max': 12,
                'examples': ['□ + 9 = 20', '8 + 7 + □ = 20'],
                'focus': 'Target-20 reasoning.',
                'what_is_taught': 'Students learn how different combinations reach exactly 20, including missing values.',
                'students_should_understand': [
                    '20 can be made in many ways',
                    'Reasoning works backwards from a target'
                ],
                'what_should_teach': 'Explain how to make 20 using different number combinations. Include missing-number explanations.'
            }
        }
    },
    'GRADE_02': {
        'name': 'Grade 2 - Multi-digit and Multiplication Intro',
        'Level_1': {
            'Starter': {
                'description': 'Basic single-step addition and subtraction (0-20)',
                'operations': ['+', '-'],
                'operand_max': 20,
                'result_max': 20,
                'examples': ['6 + 8 = 14', '17 − 9 = 8'],
                'focus': 'Addition and subtraction meaning.',
                'what_is_taught': 'Students learn addition increases and subtraction decreases quantities.',
                'students_should_understand': [
                    '(+) Adds and (-) removes'
                ],
                'what_should_teach': 'Explain how addition and subtraction change numbers.'
            },
            'Explorer': {
                'description': 'Multiplication as repeated addition',
                'operations': ['×','+', '-'],
                'factors_max': 5,
                'product_max': 30,
                'examples': ['3 × 4 = 12', '5 - 2 = 3', '4 + 4 = 8'],
                'focus': 'Comparing quantities.',
                'what_is_taught': 'Students learn greater than and less than symbols.',
                'students_should_understand': [
                    '> means greater',
                    '< means less'
                ],
                'what_should_teach': 'Explain greater than and less than with examples.'
            },
            'Solver': {
                'description': 'Mixed operations with comparison symbols',
                'operations': ['+', '-', '×', '>', '<', '='],
                'operand_max': 30,
                'result_max': 40,
                'examples': ['6 × 3 > 18 − 4'],
                'focus': 'Multiplication meaning.',
                'what_is_taught': 'Students learn multiplication as equal groups.',
                'students_should_understand': [
                    '× means repeated addition'
                ],
                'what_should_teach': 'Explain multiplication as equal groups.'
            },
            'Champion': {
                'description': 'Two-step equations combining operations',
                'operations': ['+', '-', '×','>', '<', '='],
                'operand_max': 20,
                'result_max': 30,
                'examples': ['(3 × 4) + 8 = 20', '18 − (2 × 3) = 12'],
                'focus': 'Choosing the correct symbol.',
                'what_is_taught': 'Students decide which symbol fits a situation.',
                'students_should_understand': [
                    'Each symbol has a role'
                ],
                'what_should_teach': 'Explain how to choose the correct math symbol.'
            }
        },
        'Level_2': {
            'Starter': {
                'description': 'Two-digit addition/subtraction with regrouping',
                'operations': ['+', '-'],
                'operand_max': 30,
                'result_max': 50,
                'examples': ['27 + 14 = 41', '45 − 19 = 26'],
                'focus': 'Larger addition and subtraction.',
                'what_is_taught': 'Students apply + and − to bigger numbers.',
                'students_should_understand': [
                    'Same rules apply to larger numbers'
                ],
                'what_should_teach': 'Explain addition and subtraction with larger numbers.'
            },
            'Explorer': {
                'description': 'Multiplication tables 2-10',
                'operations': ['×','+', '-'],
                'factors_max': 10,
                'product_max': 50,
                'examples': ['6 × 5 = 30', '10 × 4 = 40'],
                'focus': 'Multiplication fluency.',
                'what_is_taught': 'Students strengthen understanding of × with tables.',
                'students_should_understand': [
                    'Multiplication patterns repeat'
                ],
                'what_should_teach': 'Explain multiplication patterns.'
            },
            'Solver': {
                'description': 'Comparing two expressions with symbols',
                'operations': ['+', '-', '×', '>', '<', '='],
                'operand_max': 30,
                'result_max': 50,
                'examples': ['24 − 9 > 4 × 4'],
                'focus': 'Comparing expressions.',
                'what_is_taught': 'Students compare results of operations.',
                'students_should_understand': [
                    'Comparisons describe size'
                ],
                'what_should_teach': 'Explain how to compare two results.'
            },
            'Champion': {
                'description': 'Mixed multi-operation equations',
                'operations': ['+', '-', '×'],
                'operand_max': 50,
                'result_max': 60,
                'examples': ['(8 × 3) − 10 = 14', '(6 × 4) + 12 = 36'],
                'focus': 'Mixed symbol reasoning.',
                'what_is_taught': 'Students interpret expressions with multiple symbols.',
                'students_should_understand': [
                    'Symbol order matters'
                ],
                'what_should_teach': 'Explain how different symbols work together.'
            }
        },
        'Level_3': {
            'Starter': {
                'description': 'Two-digit addition/subtraction with regrouping',
                'operations': ['+', '-'],
                'operand_max': 70,
                'result_max': 100,
                'examples': ['64 + 27 = 91', '95 − 38 = 57'],
                'focus': 'Two digit operations.',
                'what_is_taught': 'Students work with larger values conceptually.',
                'students_should_understand': [
                    'Place value matters'
                ],
                'what_should_teach': 'Explain working with larger numbers.'
            },
            'Explorer': {
                'description': 'Multiplication table mastery (2-10)',
                'operations': ['×','+', '-'],
                'factors_max': 10,
                'product_max': 100,
                'examples': ['9 × 7 = 63', '8 × 9 = 72'],
                'focus': 'Multiplication mastery.',
                'what_is_taught': 'Students solidify × understanding.',
                'students_should_understand': [
                    'Multiplication scales numbers'
                ],
                'what_should_teach': 'Explain multiplication as scaling.'
            },
            'Solver': {
                'description': 'Comparing multiplication and addition',
                'operations': ['+', '×', '>', '<', '='],
                'operand_max': 12,
                'result_max': 100,
                'examples': ['6 × 9 = 54', '7 × 8 > 60'],
                'focus': 'Comparison with operations.',
                'what_is_taught': 'Students compare computed results.',
                'students_should_understand': [
                    'Symbols guide reasoning'
                ],
                'what_should_teach': 'Explain comparing results.'
            },
            'Champion': {
                'description': 'Multi-operation fluency with BODMAS',
                'operations': ['+', '-', '×'],
                'operand_max': 20,
                'result_max': 100,
                'examples': ['(5 × 8) − 14 = 26', '(6 × 7) + 12 = 54'],
                'focus': 'Full symbol interpretation.',
                'what_is_taught': 'Students reason across all symbols.',
                'students_should_understand': [
                    'Symbols describe relationships'
                ],
                'what_should_teach': 'Explain interpreting expressions with many symbols.'
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
                'focus': 'Addition and subtraction together.',
                'what_is_taught': 'Students learn number increases and decreases.',
                'students_should_understand': [
                    'Symbols can combine'
                ],
                'what_should_teach': 'Explain addition and subtraction together.'
            },
            'Explorer': {
                'description': 'Multiplication tables 6-9',
                'operations': ['×','+', '-'],
                'factors_max': 9,
                'factors_min': 6,
                'product_max': 81,
                'examples': ['6 × 7 = 42', '8 × 9 = 72'],
                'focus': 'Multiplication depth.',
                'what_is_taught': 'Students understand grouping and scaling.',
                'students_should_understand': [
                    'Groups must be equal'
                ],
                'what_should_teach': 'Explain multiplication grouping.'
            },
            'Solver': {
                'description': 'Comparison symbols with computed results',
                'operations': ['+', '-', '×', '>', '<', '='],
                'operand_max': 50,
                'result_max': 60,
                'examples': ['3 × 9 > 28', '45 − 8 = 37'],
                'focus': 'Division meaning.',
                'what_is_taught': 'Students learn division as equal sharing.',
                'students_should_understand': [
                    'Division splits evenly'
                ],
                'what_should_teach': 'Explain division as sharing.'
            },
            'Champion': {
                'description': 'Multi-operation integration in equations',
                'operations': ['+', '-', '×'],
                'operand_max': 30,
                'result_max': 60,
                'examples': ['(5 × 6) − 10 = 20', '(3 × 9) + 12 = 39'],
                'focus': 'Comparison symbols.',
                'what_is_taught': 'Students compare results.',
                'students_should_understand': [
                    '> and < compare size'
                ],
                'what_should_teach': 'Explain comparison symbols.'
            }
        },
        'Level_2': {
            'Starter': {
                'description': 'Addition and subtraction within 80',
                'operations': ['+', '-'],
                'operand_max': 70,
                'result_max': 80,
                'examples': ['64 + 13 = 77', '75 − 19 = 56'],
                'focus': 'Multi-step number change.',
                'what_is_taught': 'Students interpret chained operations.',
                'students_should_understand': [
                    'Steps affect totals'
                ],
                'what_should_teach': 'Explain multi-step number changes.'
            },
            'Explorer': {
                'description': 'Multiplication and addition in comparisons',
                'operations': ['+', '×', '>', '<', '='],
                'factors_max': 10,
                'product_max': 80,
                'examples': ['8 × 6 > 50', '9 × 7 < 70'],
                'focus': 'Multiplication and division relationship.',
                'what_is_taught': 'Students see × and ÷ as opposites.',
                'students_should_understand': [
                    'Division reverses multiplication'
                ],
                'what_should_teach': 'Explain the relationship between multiplication and division.'
            },
            'Solver': {
                'description': 'Three-operation equations with order',
                'operations': ['+', '-', '×'],
                'operand_max': 30,
                'result_max': 80,
                'examples': ['(9 × 4) − 16 + 8 = 28'],
                'focus': 'Comparing expressions.',
                'what_is_taught': 'Students compare multi-operation results.',
                'students_should_understand': [
                    'Structure matters'
                ],
                'what_should_teach': 'Explain comparing expressions.'
            },
            'Champion': {
                'description': 'Estimation and multi-step verification',
                'operations': ['+', '-', '×'],
                'operand_max': 15,
                'result_max': 80,
                'examples': ['(5 × 6) + 8 = 38'],
                'focus': 'Reasoning before calculation.',
                'what_is_taught': 'Students interpret symbol meaning first.',
                'students_should_understand': [
                    'Understanding comes before rules'
                ],
                'what_should_teach': 'Explain interpreting expressions before calculating.'
            }
        },
        'Level_3': {
            'Starter': {
                'description': 'Addition/subtraction near 100 with regrouping',
                'operations': ['+', '-'],
                'operand_max': 90,
                'result_max': 100,
                'examples': ['58 + 37 = 95', '94 − 28 = 66'],
                'focus': 'Larger-number reasoning.',
                'what_is_taught': 'Students reason with numbers near 100.',
                'students_should_understand': [
                    'Same symbol rules apply'
                ],
                'what_should_teach': 'Explain working with larger values.'
            },
            'Explorer': {
                'description': 'Two-digit × one-digit multiplication',
                'operations': ['×','+', '-'],
                'multiplicand_max': 20,
                'multiplier_max': 10,
                'product_max': 100,
                'examples': ['12 × 8 = 96', '9 × 9 = 81'],
                'focus': 'Advanced multiplication.',
                'what_is_taught': 'Students strengthen scaling understanding.',
                'students_should_understand': [
                    'Multiplication grows quantities quickly'
                ],
                'what_should_teach': 'Explain advanced multiplication.'
            },
            'Solver': {
                'description': 'Mixed operations determining final result',
                'operations': ['+', '-', '×'],
                'operand_max': 20,
                'result_max': 100,
                'examples': ['(7 × 8) − 24 = 32', '9 × 5 + 15 = 60'],
                'focus': 'Mixed operations.',
                'what_is_taught': 'Students interpret multiple symbols together.',
                'students_should_understand': [
                    'Symbols interact logically'
                ],
                'what_should_teach': 'Explain how multiple symbols interact.'
            },
            'Champion': {
                'description': 'Multi-step equations targeting 100',
                'operations': ['+', '-', '×'],
                'operand_max': 20,
                'result_approx': 100,
                'examples': ['(6 × 9) + (8 × 6) = 102', '(9 × 8) + 25 = 97'],
                'focus': 'Symbol mastery.',
                'what_is_taught': 'Students consolidate understanding of all symbols.',
                'students_should_understand': [
                    'Symbol meaning guides reasoning'
                ],
                'what_should_teach': 'Explain how all math symbols work together.'
            }
        }
    },
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
