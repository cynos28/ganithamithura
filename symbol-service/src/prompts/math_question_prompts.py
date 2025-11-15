"""
Math Question Generation Prompts
Centralized prompts for AI-based question generation, hints, explanations, and recommendations
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from components.curriculum_helper import CurriculumHelper


def get_question_generation_prompt(grade: int, performance_level: int, sublevel: str) -> str:
    """
    Generate enhanced AI prompt for math question generation based on grade, performance level, and sublevel.

    Uses detailed curriculum specifications with operand ranges, result constraints, and operation types.

    Args:
        grade: Grade level (1, 2, or 3)
        performance_level: Performance level (1, 2, or 3)
        sublevel: Sublevel name (Starter, Explorer, Solver, or Champion)

    Returns:
        Formatted prompt string for AI question generation
    """

    # Define grade-specific contexts and themes
    grade_contexts = {
        1: ["toys", "fruits", "animals", "candies", "stickers", "blocks", "crayons"],
        2: ["books", "pencils", "marbles", "cookies", "flowers", "birds", "cars"],
        3: ["students", "apples", "coins", "cards", "pizzas", "chocolates", "stamps"]
    }

    # Get curriculum spec from CurriculumHelper (single source of truth)
    spec = CurriculumHelper.get_spec(grade, performance_level, sublevel)

    # Fallback to simple addition if no spec found
    if not spec:
        spec = {
            'operations': ['addition'],
            'operand_max': 10,
            'result_max': 20,
            'focus': 'Basic addition'
        }

    # Build curriculum spec for prompt (kept for reference)
    curriculum_spec = spec

    # Old embedded curriculum_specs (kept for backward compatibility but not used)
    curriculum_specs = {
        1: {
            1: {
                "Starter": {
                    "operations": ["addition"],
                    "operand_max": 5,
                    "result_max": 7,
                    "focus": "Small combinations totaling no higher than 7",
                    "examples": "2+3=5, 1+4=5, 3+2=5"
                },
                "Explorer": {
                    "operations": ["addition", "doubles", "near-doubles"],
                    "operand_max": 8,
                    "result_min": 5,
                    "result_max": 9,
                    "focus": "Doubles and near-doubles patterns (addends ≤8, results 5-9)",
                    "examples": "3+4=7, 4+4=8, 3+5=8"
                },
                "Solver": {
                    "operations": ["addition"],
                    "operand_max": 9,
                    "result_max": 11,
                    "focus": "Combining numbers reaching up to 11 (addends ≤9, results ≤11)",
                    "examples": "7+3=10, 6+5=11, 5+4=9"
                },
                "Champion": {
                    "operations": ["addition"],
                    "operand_max": 9,
                    "result_min": 10,
                    "result_max": 14,
                    "focus": "Building larger facts up to 14 with strategy paths (near-doubles, make 10)",
                    "examples": "8+6=14, 7+5=12, 9+5=14"
                }
            },
            2: {
                "Starter": {
                    "operations": ["addition", "missing_addend"],
                    "operand_max": 15,
                    "result_max": 15,
                    "focus": "One unknown in addition equations (□ + a = b, target ≤15)",
                    "examples": "□+4=9, □+3=7, 6+□=11"
                },
                "Explorer": {
                    "operations": ["addition"],
                    "operand_min": 5,
                    "operand_max": 9,
                    "result_min": 12,
                    "result_max": 15,
                    "focus": "Addition crossing 10 (5≤addends≤9, 12≤results≤15)",
                    "examples": "9+6=15, 8+7=15, 7+5=12"
                },
                "Solver": {
                    "operations": ["three_addend_addition"],
                    "operand_max": 9,
                    "result_max": 15,
                    "focus": "Three-addend problems with grouping (≤9 each, ≤15 total)",
                    "examples": "4+5+3=12, 3+6+2=11, 5+5+3=13"
                },
                "Champion": {
                    "operations": ["addition"],
                    "operand_min": 6,
                    "operand_max": 10,
                    "result_min": 10,
                    "result_max": 17,
                    "focus": "Larger combinations up to 17 (6-10 addends, 10-17 results)",
                    "examples": "9+8=17, 10+5=15, 8+9=17"
                }
            },
            3: {
                "Starter": {
                    "operations": ["addition", "missing_addend"],
                    "operand_min": 5,
                    "operand_max": 10,
                    "result_max": 18,
                    "focus": "Missing addend with higher targets (5≤addends≤10, ≤18)",
                    "examples": "□+8=16, □+7=15, 9+□=18"
                },
                "Explorer": {
                    "operations": ["addition", "doubles", "near-doubles"],
                    "operand_max": 10,
                    "operand_min": 8,
                    "result_max": 20,
                    "focus": "Two-addend with large numbers (≥8 addends, ≤20 results)",
                    "examples": "8+8=16, 8+9=17, 10+9=19"
                },
                "Solver": {
                    "operations": ["three_addend_addition"],
                    "operand_max": 9,
                    "result_max": 20,
                    "focus": "Three-addend approaching 20 (≤9 each, ≤20 total)",
                    "examples": "6+7+5=18, 7+6+4=17, 8+5+4=17"
                },
                "Champion": {
                    "operations": ["addition", "missing_addend"],
                    "result_target": 20,
                    "missing_max": 12,
                    "focus": "Target 20 with missing numbers (results=20, missing≤12)",
                    "examples": "□+9=20, 8+7+□=20, 10+□=20"
                }
            }
        },
        2: {
            1: {
                "Starter": {
                    "operations": ["addition", "subtraction"],
                    "operand_max": 20,
                    "result_max": 20,
                    "focus": "Single-step add/subtract (≤20 operands, ≤20 results)",
                    "examples": "6+8=14, 17-9=8, 15-7=8"
                },
                "Explorer": {
                    "operations": ["multiplication"],
                    "factors_max": 5,
                    "product_max": 30,
                    "focus": "Multiplication as repeated addition (factors≤5, products≤30)",
                    "examples": "3×4=12, 5×2=10, 4×5=20"
                },
                "Solver": {
                    "operations": ["addition", "subtraction", "multiplication"],
                    "operand_max": 30,
                    "result_max": 40,
                    "focus": "Mixed operations with comparisons (≤30 operands, ≤40 results)",
                    "examples": "6×3 > 18-4, 5×4 = 20"
                },
                "Champion": {
                    "operations": ["addition", "subtraction", "multiplication", "brackets"],
                    "operand_max": 20,
                    "result_max": 30,
                    "focus": "Two-step equations with BODMAS (operands≤20, results≤30)",
                    "examples": "(3×4)+8=20, 18-(2×3)=12"
                }
            },
            2: {
                "Starter": {
                    "operations": ["addition", "subtraction"],
                    "operand_max": 30,
                    "result_max": 50,
                    "focus": "Two-digit with regrouping (≤30, ≤50 results)",
                    "examples": "27+14=41, 45-19=26, 32+18=50"
                },
                "Explorer": {
                    "operations": ["multiplication"],
                    "factors_max": 10,
                    "product_max": 50,
                    "focus": "Multiplication tables 2-10 (factors≤10, products≤50)",
                    "examples": "6×5=30, 10×4=40, 7×6=42"
                },
                "Solver": {
                    "operations": ["addition", "subtraction", "multiplication"],
                    "operand_max": 30,
                    "result_max": 50,
                    "focus": "Comparing expressions (≤30 operands, ≤50 results)",
                    "examples": "24-9 > 4×4, 6×5 < 31"
                },
                "Champion": {
                    "operations": ["addition", "subtraction", "multiplication", "brackets"],
                    "operand_max": 50,
                    "result_max": 60,
                    "focus": "Multi-operation with BODMAS (operands≤50, results≤60)",
                    "examples": "(8×3)-10=14, (6×4)+12=36"
                }
            },
            3: {
                "Starter": {
                    "operations": ["addition", "subtraction"],
                    "operand_max": 70,
                    "result_max": 100,
                    "focus": "Two-digit with regrouping near 100 (≤70, ≤100 results)",
                    "examples": "64+27=91, 95-38=57, 70+23=93"
                },
                "Explorer": {
                    "operations": ["multiplication"],
                    "factors_max": 10,
                    "product_max": 100,
                    "focus": "Full multiplication mastery 2-10 (factors≤10, products≤100)",
                    "examples": "9×7=63, 8×9=72, 10×10=100"
                },
                "Solver": {
                    "operations": ["addition", "subtraction", "multiplication"],
                    "operand_max": 12,
                    "result_max": 100,
                    "focus": "Comparing multiplication and addition (≤12 operands)",
                    "examples": "6×9=54, 7×8 > 60"
                },
                "Champion": {
                    "operations": ["addition", "subtraction", "multiplication", "brackets"],
                    "operand_max": 20,
                    "result_max": 100,
                    "focus": "Multi-operation fluency with BODMAS (operands≤20)",
                    "examples": "(5×8)-14=26, (6×7)+12=54"
                }
            }
        },
        3: {
            1: {
                "Starter": {
                    "operations": ["addition", "subtraction"],
                    "operand_max": 50,
                    "result_max": 60,
                    "focus": "Multi-digit add/subtract with regrouping (≤50, ≤60)",
                    "examples": "34+27=61, 56-18=38, 45+12=57"
                },
                "Explorer": {
                    "operations": ["multiplication"],
                    "factors_min": 6,
                    "factors_max": 9,
                    "product_max": 81,
                    "focus": "Multiplication tables 6-9 (6≤factors≤9, ≤81)",
                    "examples": "6×7=42, 8×9=72, 7×8=56"
                },
                "Solver": {
                    "operations": ["addition", "subtraction", "multiplication"],
                    "operand_max": 50,
                    "result_max": 60,
                    "focus": "Comparison with computed results (≤50, ≤60)",
                    "examples": "3×9 > 28, 45-8=37"
                },
                "Champion": {
                    "operations": ["addition", "subtraction", "multiplication", "brackets"],
                    "operand_max": 30,
                    "result_max": 60,
                    "focus": "Multi-operation integration (operands≤30, ≤60)",
                    "examples": "(5×6)-10=20, (3×9)+12=39"
                }
            },
            2: {
                "Starter": {
                    "operations": ["addition", "subtraction"],
                    "operand_max": 70,
                    "result_max": 80,
                    "focus": "Add/subtract within 80 range (≤70, ≤80)",
                    "examples": "64+13=77, 75-19=56, 55+20=75"
                },
                "Explorer": {
                    "operations": ["addition", "multiplication"],
                    "factors_max": 10,
                    "product_max": 80,
                    "focus": "Multiplication with addition comparisons (factors≤10)",
                    "examples": "8×6 > 50, 9×7 < 70"
                },
                "Solver": {
                    "operations": ["addition", "subtraction", "multiplication", "brackets"],
                    "operand_max": 30,
                    "result_max": 80,
                    "focus": "Three-operation with BODMAS (≤30, ≤80)",
                    "examples": "(9×4)-16+8=28, (7×5)-10=25"
                },
                "Champion": {
                    "operations": ["addition", "subtraction", "multiplication"],
                    "operand_max": 15,
                    "result_max": 80,
                    "focus": "Estimation and multi-step (operands≤15)",
                    "examples": "(5×6)+8=38, (8×9)+5=77"
                }
            },
            3: {
                "Starter": {
                    "operations": ["addition", "subtraction"],
                    "operand_max": 90,
                    "result_max": 100,
                    "focus": "Add/subtract near 100 with regrouping (≤90, ≤100)",
                    "examples": "58+37=95, 94-28=66, 75+18=93"
                },
                "Explorer": {
                    "operations": ["multiplication"],
                    "multiplicand_max": 20,
                    "multiplier_max": 10,
                    "product_max": 100,
                    "focus": "Two-digit × one-digit (multiplicand≤20, multiplier≤10)",
                    "examples": "12×8=96, 9×9=81, 15×6=90"
                },
                "Solver": {
                    "operations": ["addition", "subtraction", "multiplication", "brackets"],
                    "operand_max": 20,
                    "result_max": 100,
                    "focus": "Mixed operations with BODMAS (operands≤20, ≤100)",
                    "examples": "(7×8)-24=32, 9×5+15=60"
                },
                "Champion": {
                    "operations": ["addition", "subtraction", "multiplication", "brackets"],
                    "operand_max": 20,
                    "result_approx": 100,
                    "focus": "Multi-step targeting ≈100 (operands≤20)",
                    "examples": "(6×9)+(8×6)=102, (9×8)+25=97"
                }
            }
        }
    }

    # Use the curriculum spec from CurriculumHelper (already retrieved above)

    contexts = grade_contexts.get(grade, grade_contexts[1])

    prompt = f"""You are an expert math educator creating an engaging, educational question for a Grade {grade} student.

STUDENT PROFILE:
- Grade: {grade}
- Performance Level: {performance_level} (1=Beginning, 2=Intermediate, 3=Advanced)
- Sublevel: {sublevel}

CURRICULUM SPECIFICATIONS:
- Focus: {spec.get('focus', 'Building mathematical skills')}
- Operations: {', '.join(spec.get('operations', ['addition']))}
- Operand Range: {spec.get('operand_min', 0)} to {spec.get('operand_max', 20)}
- Result Range: {spec.get('result_min', 0)} to {spec.get('result_max', 20)}
- Examples: {spec.get('examples', 'N/A')}

REQUIREMENTS FOR THIS LEVEL:
{spec.get('focus', 'Create an age-appropriate mathematical question.')}

CREATIVE REQUIREMENTS:
1. Use relatable contexts: {', '.join(contexts[:4])} (or similar age-appropriate items)
2. Make the question engaging and relevant to a {grade}-grader's world
3. Use clear, simple language that's easy to understand when spoken aloud
4. Ensure the math is age-appropriate and builds confidence

VARIETY REQUIREMENTS:
1. Vary your approach - use different question formats:
   - Direct calculation: "What is 5 plus 3?"
   - Word problem: "Sarah has 5 apples. She gets 3 more. How many does she have?"
   - Scenario-based: "If you have 8 candies and give away 3, how many are left?"
2. Use different number combinations each time
3. Mix operation types when appropriate for the level
4. Make each question feel fresh and unique

OUTPUT FORMAT (JSON only):
{{
  "question_text": "Clear, spoken question (e.g., 'What is 5 plus 3?' or 'Sarah has 5 apples and gets 3 more. How many apples does Sarah have now?')",
  "expression": "Mathematical notation (e.g., '5 + 3')",
  "answer": numeric_value (integer or decimal),
  "operation": "+|-|*|/|word_problem"
}}

EXAMPLES:

Grade 1, Level 1, Starter:
{{"question_text": "What is 3 plus 2?", "expression": "3 + 2", "answer": 5, "operation": "+"}}
{{"question_text": "You have 7 crayons. You use 4 of them. How many crayons do you have left?", "expression": "7 - 4", "answer": 3, "operation": "word_problem"}}

Grade 2, Level 2, Explorer:
{{"question_text": "What is 6 times 4?", "expression": "6 × 4", "answer": 24, "operation": "*"}}
{{"question_text": "A box has 35 marbles. You share them equally among 5 friends. How many marbles does each friend get?", "expression": "35 ÷ 5", "answer": 7, "operation": "word_problem"}}

Grade 3, Level 3, Champion:
{{"question_text": "A shop has 144 chocolates. They sell 89 chocolates on Monday. How many chocolates are left?", "expression": "144 - 89", "answer": 55, "operation": "word_problem"}}
{{"question_text": "What is 25 times 8?", "expression": "25 × 8", "answer": 200, "operation": "*"}}

NOW GENERATE ONE UNIQUE, CREATIVE QUESTION for Grade {grade}, Performance Level {performance_level}, {sublevel} sublevel:"""

    return prompt


def get_system_prompt() -> str:
    """
    Get the enhanced system prompt for AI question generation.

    Returns:
        System prompt string
    """
    return """You are an expert elementary math educator with 20 years of experience creating engaging, educational content for young learners.

YOUR MISSION:
Create questions that make math fun, relatable, and accessible while building student confidence and skills.

CORE PRINCIPLES:
1. ENGAGEMENT: Use real-world contexts that children can relate to and visualize
2. CLARITY: Write questions that are easy to understand when spoken aloud
3. VARIETY: Every question should feel fresh - vary contexts, numbers, and formats
4. CREATIVITY: Think beyond "What is X + Y?" - tell mini-stories when appropriate
5. APPROPRIATENESS: Match the cognitive level and interests of the grade level

QUALITY STANDARDS:
✓ Questions should spark curiosity and interest
✓ Language should be conversational and friendly
✓ Numbers should be realistic for the scenario
✓ Word problems should have logical, believable contexts
✓ Avoid repetitive patterns or formulaic questions

DIVERSITY REQUIREMENTS:
- Rotate between direct calculation and word problems
- Use different contexts (food, toys, nature, school, etc.)
- Vary question structure and phrasing
- Include both concrete (objects) and abstract (pure numbers) questions
- Mix simple and slightly challenging formats within the level

OUTPUT REQUIREMENT:
Respond with ONLY valid JSON. No markdown, no extra text. Pure JSON only.

JSON Structure:
{
  "question_text": "The complete question as spoken (clear, engaging, age-appropriate)",
  "expression": "Math notation (e.g., '5 + 3' or '24 ÷ 6')",
  "answer": numeric_answer,
  "operation": "+|-|*|/|word_problem"
}"""


def get_fallback_question_config(grade: int, performance_level: int, sublevel: str) -> dict:
    """
    Get fallback question configuration based on grade, performance level, and sublevel.
    Used when AI generation fails.

    Args:
        grade: Grade level (1, 2, or 3)
        performance_level: Performance level (1, 2, or 3)
        sublevel: Sublevel name (Starter, Explorer, Solver, or Champion)

    Returns:
        Configuration dictionary with range and operations
    """

    # Base configuration by grade
    grade_configs = {
        1: {'range': (1, 10), 'operations': ['+', '-']},
        2: {'range': (1, 20), 'operations': ['+', '-', '*']},
        3: {'range': (1, 50), 'operations': ['+', '-', '*', '/']}
    }

    base_config = grade_configs.get(grade, grade_configs[1])

    # Adjust based on performance level
    min_val, max_val = base_config['range']

    if performance_level == 1:
        # Easier range
        max_val = max_val // 2
    elif performance_level == 3:
        # Harder range
        max_val = int(max_val * 1.5)

    # Adjust based on sublevel
    if sublevel == "Starter":
        max_val = min(max_val, 10)
        operations = ['+', '-']
    elif sublevel == "Explorer":
        operations = base_config['operations']
    elif sublevel == "Solver":
        operations = base_config['operations']
    elif sublevel == "Champion":
        operations = base_config['operations']
        max_val = int(max_val * 1.2)
    else:
        operations = ['+', '-']

    return {
        'range': (min_val, max_val),
        'operations': operations
    }


def get_uniqueness_prompt(recent_expressions: list, recent_operations: list, recent_numbers: list, attempt: int) -> str:
    """
    Generate uniqueness constraints prompt for question generation.

    Args:
        recent_expressions: List of recent question expressions
        recent_operations: List of recent operations used
        recent_numbers: List of recently used numbers
        attempt: Current attempt number

    Returns:
        Uniqueness constraint prompt string
    """
    return f"""

CRITICAL UNIQUENESS REQUIREMENTS:
1. DO NOT use these exact expressions: {', '.join(recent_expressions)}
2. Recent operations used: {', '.join(set(recent_operations))}
3. Recent numbers used: {', '.join(recent_numbers)}

MUST GENERATE A COMPLETELY DIFFERENT QUESTION:
- Use DIFFERENT numbers (not {', '.join(set(recent_numbers[:10]))})
- Vary the operation type if possible
- Create a unique mathematical scenario
- Ensure maximum variety and creativity

This is attempt #{attempt + 1} - make it VERY different from previous questions!"""


def get_hint_system_prompt() -> str:
    """
    Get the system prompt for AI hint generation.

    Returns:
        System prompt string for hints
    """
    return "You are a helpful math tutor providing hints to students."


def get_hint_generation_prompt(question_text: str, expression: str, answer: float,
                               hint_level: int, grade: int) -> str:
    """
    Generate prompt for AI hint generation.

    Args:
        question_text: The question text
        expression: Mathematical expression
        answer: The correct answer
        hint_level: Level of hint (1=subtle, 2=moderate, 3=direct)
        grade: Student's grade level

    Returns:
        Formatted prompt for hint generation
    """
    hint_strategies = {
        1: "Give a very subtle hint that helps the student think about the problem without revealing the answer or method.",
        2: "Give a moderate hint that suggests the approach to solve the problem, but doesn't give the answer.",
        3: "Give a direct hint that shows the method step-by-step, but still lets the student calculate the final answer."
    }

    strategy = hint_strategies.get(hint_level, hint_strategies[1])

    return f"""For the math question: "{question_text}"
Expression: {expression}
Answer: {answer}

{strategy}

Keep the hint to 1-2 sentences maximum. Make it encouraging and grade-appropriate for Grade {grade}."""


def get_explanation_system_prompt() -> str:
    """
    Get the system prompt for AI explanation generation.

    Returns:
        System prompt string for explanations
    """
    return "You are a patient, encouraging math tutor explaining concepts to young students."


def get_explanation_generation_prompt(question_text: str, expression: str,
                                     correct_answer: float, user_answer: int,
                                     grade: int) -> str:
    """
    Generate prompt for AI explanation of incorrect answers.

    Args:
        question_text: The question text
        expression: Mathematical expression
        correct_answer: The correct answer
        user_answer: Student's incorrect answer
        grade: Student's grade level

    Returns:
        Formatted prompt for explanation generation
    """
    return f"""A Grade {grade} student answered a math question incorrectly.

Question: {question_text}
Expression: {expression}
Correct Answer: {correct_answer}
Student's Answer: {user_answer}

Provide a brief, encouraging explanation (2-3 sentences) that:
1. Explains WHY the correct answer is {correct_answer}
2. Gently shows where the student might have made a mistake
3. Encourages them to keep trying

Keep it simple and age-appropriate for Grade {grade}."""


def get_recommendation_system_prompt() -> str:
    """
    Get the system prompt for AI recommendation generation.

    Returns:
        System prompt string for recommendations
    """
    return "You are an expert math education advisor providing personalized learning recommendations."


def get_recommendation_generation_prompt(total_questions: int, correct: int,
                                        accuracy: float, avg_time: float,
                                        grade: int, performance_level: int,
                                        sublevel: str, hints_used: int,
                                        difficulty_adjustments: int) -> str:
    """
    Generate prompt for AI personalized recommendation.

    Args:
        total_questions: Total questions attempted
        correct: Number of correct answers
        accuracy: Accuracy percentage
        avg_time: Average time per question
        grade: Student's grade level
        performance_level: Current performance level
        sublevel: Current sublevel
        hints_used: Number of hints used
        difficulty_adjustments: Number of difficulty changes

    Returns:
        Formatted prompt for recommendation generation
    """
    return f"""Analyze this Grade {grade} student's math practice session and provide a brief recommendation:

Session Stats:
- Total Questions: {total_questions}
- Correct: {correct}
- Accuracy: {accuracy:.1f}%
- Average Time: {avg_time:.1f} seconds
- Current Level: {performance_level}
- Sublevel: {sublevel}
- Hints Used: {hints_used}
- Difficulty Adjustments: {difficulty_adjustments}

Provide 1-2 specific, actionable recommendations to help the student improve. Be encouraging and age-appropriate."""


def get_image_generation_prompt(question_text: str, grade: int) -> str:
    """
    Generate DALL-E 3 prompt for clean illustrations using visual-only descriptions.
    Focuses on the SCENE and OBJECTS only, completely avoiding any mention of quantities.

    Args:
        question_text: The math question text
        grade: Student's grade level

    Returns:
        DALL-E prompt for image generation
    """
    import re

    # Extract only the scenario/subject from the question
    # Remove numbers, math operations, and question marks
    visual_description = question_text
    visual_description = re.sub(r'\b\d+\b', '', visual_description)  # Remove numbers
    visual_description = re.sub(r'[?!.]$', '', visual_description)  # Remove punctuation
    visual_description = re.sub(r'\b(what is|how many|calculate|find|solve|answer)\b', '', visual_description, flags=re.IGNORECASE)
    visual_description = re.sub(r'\s+', ' ', visual_description).strip()

    # Clean up common math keywords
    visual_description = re.sub(r'\b(plus|minus|times|divided|multiply|divide|add|subtract|sum|total|left|removed|added|groups)\b', '', visual_description, flags=re.IGNORECASE)
    visual_description = re.sub(r'\s+', ' ', visual_description).strip()

    return f"""Illustration in the style of children's picture books like Pete the Cat or The Very Hungry Caterpillar.

Scene: {visual_description}

Art style guidelines:
- Colorful, playful children's book illustration style
- Soft, rounded cartoon shapes
- Bright, cheerful colors - suitable for Grade {grade} children
- Focus on objects and characters, not complexity
- Warm and inviting aesthetic

CRITICAL CONTENT RESTRICTIONS:
Do not include any: numbers, digits, math symbols, letters, words, text, labels, or written content anywhere. Create only a visual picture without any writing or symbols."""


def get_correct_answer_feedback_prompt(answer: float, question_text: str, grade: int) -> str:
    """
    Generate prompt for AI feedback on correct answers.

    Args:
        answer: The correct answer
        question_text: The question that was answered
        grade: Student's grade level

    Returns:
        Formatted prompt for generating positive feedback
    """
    return f"""Generate enthusiastic, varied praise for a Grade {grade} student who correctly answered a math question.

Question: {question_text}
Correct Answer: {answer}

Requirements:
1. Be genuinely enthusiastic and encouraging
2. Vary your response - don't always say the same thing
3. Keep it brief (1 sentence)
4. Age-appropriate for Grade {grade}
5. Sometimes mention the answer, sometimes don't
6. Mix between:
   - Simple praise: "Excellent!", "Perfect!", "Great job!"
   - Answer-specific: "Yes! {answer} is correct!"
   - Encouraging: "You're doing amazing!", "Keep up the great work!"
   - Skill-focused: "You really know your math!", "Nice calculation!"

Generate ONE unique, encouraging response now:"""


def get_wrong_answer_feedback_prompt(user_answer: int, correct_answer: float,
                                     question_text: str, expression: str, grade: int) -> str:
    """
    Generate prompt for AI feedback on incorrect answers.

    Args:
        user_answer: Student's incorrect answer
        correct_answer: The correct answer
        question_text: The question that was answered
        expression: Mathematical expression
        grade: Student's grade level

    Returns:
        Formatted prompt for generating helpful, encouraging feedback
    """
    return f"""Generate encouraging, helpful feedback for a Grade {grade} student who answered incorrectly.

Question: {question_text}
Expression: {expression}
Student's Answer: {user_answer}
Correct Answer: {correct_answer}

Requirements:
1. Be kind and encouraging - never discouraging
2. Briefly explain the correct answer
3. Help them understand where they might have made a mistake
4. Keep it simple and age-appropriate for Grade {grade}
5. End with encouragement to keep trying
6. 2-3 sentences maximum

Generate helpful, kind feedback now:"""


def get_feedback_system_prompt() -> str:
    """
    Get system prompt for feedback generation.

    Returns:
        System prompt for feedback
    """
    return "You are a kind, encouraging elementary math tutor providing supportive feedback to young students."
