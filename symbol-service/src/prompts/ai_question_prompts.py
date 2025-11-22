"""
AI Question Generation Prompts

Provides prompt templates for OpenAI to generate curriculum-aligned math questions.
Uses CurriculumHelper specifications to ensure grade and level-specific content.
"""

import json


def _get_grade_name(grade: int) -> str:
    """Get grade name for prompt."""
    grade_names = {1: "Grade 1", 2: "Grade 2", 3: "Grade 3"}
    return grade_names.get(grade, "Grade 1")


def get_ai_question_generation_prompt(grade: int, level: int, sublevel: str, curriculum_info: str) -> str:
    """
    Build the prompt for OpenAI to generate a math question.
    Uses curriculum specifications from CurriculumHelper to generate grade and level-specific questions.

    Args:
        grade: Student grade (1, 2, or 3)
        level: Performance level (1, 2, or 3)
        sublevel: Sublevel (Starter, Explorer, Solver, Champion)
        curriculum_info: JSON string with curriculum specifications from CurriculumHelper.get_spec()

    Returns:
        Formatted prompt string for OpenAI
    """
    # Parse curriculum spec from CurriculumHelper
    try:
        curriculum_spec = json.loads(curriculum_info)
    except (json.JSONDecodeError, TypeError):
        curriculum_spec = {}

    # Build detailed prompt based on curriculum spec
    detailed_prompt = _build_detailed_prompt(grade, level, sublevel, curriculum_spec)

    return detailed_prompt


def _build_detailed_prompt(grade: int, level: int, sublevel: str, spec: dict) -> str:
    """
    Build detailed prompt using curriculum specification details.

    Args:
        grade: Student grade (1, 2, or 3)
        level: Performance level (1, 2, or 3)
        sublevel: Student sublevel (Starter, Explorer, Solver, Champion)
        spec: Curriculum specification dictionary from CurriculumHelper

    Returns:
        Formatted prompt string for OpenAI
    """
    if not spec:
        return f"""Generate ONE simple math question for Grade {grade}, Level {level}, {sublevel} student.
RESPOND WITH ONLY THIS JSON (no other text):
{{"question": "2 plus 2", "expression": "2 + 2", "answer": 4}}"""

    # Extract key specifications
    operations = spec.get('operations', ['addition'])
    operand_min = spec.get('operand_min', 0)
    operand_max = spec.get('operand_max', 10)
    result_min = spec.get('result_min', 0)
    result_max = spec.get('result_max', 20)
    focus = spec.get('focus', '')

    # Get example based on operations
    example = _get_example_for_operations(operations, operand_min, operand_max)

    # Build operation-specific instructions
    operation_instructions = _get_operation_instructions(operations, operand_min, operand_max, result_max)

    # Remove 'brackets' from operations and use simpler operations only
    simple_operations = [op for op in operations if op != 'brackets']
    if not simple_operations:
        simple_operations = ['addition']

    return f"""CURRICULUM: Grade {grade}, Level {level}, {sublevel}
Operands: {operand_min}-{operand_max}
Results: {result_min}-{result_max}
Allowed operations: {', '.join(simple_operations)}

Generate ONE child-friendly math question:

RULES:
1. Create a SHORT, FUN, relatable scenario for a {_get_grade_name(grade)} student
2. Use simple words children understand
3. Include a relatable context (toys, animals, fruits, friends, etc.)
4. Question format: "[Scenario] How many [item]?"
5. Keep operands between {operand_min}-{operand_max}
6. Keep result between {result_min}-{result_max}
7. Use ONLY these operations: {', '.join(simple_operations)}
8. NO "What is", NO "Calculate", NO complex language

Examples for Grade {grade}:
- "Sarah has 8 apples. She gets 5 more. How many apples does she have?"
- "There are 12 toys. 4 toys are red. How many are not red?"
- "Each box has 6 candies. Tom has 3 boxes. How many candies total?"

RESPOND WITH ONLY THIS JSON (no extra text):
{{"question": "child-friendly story with math", "expression": "A op B", "answer": number}}"""


def _get_example_for_operations(operations: list, operand_min: int, operand_max: int) -> str:
    """
    Get an example question based on allowed operations.

    Args:
        operations: List of allowed operations
        operand_min: Minimum operand value
        operand_max: Maximum operand value

    Returns:
        JSON example string
    """
    # Filter out 'brackets' as we don't support complex expressions
    simple_ops = [op for op in operations if op != 'brackets']
    op = simple_ops[0] if simple_ops else 'addition'

    if op == 'addition':
        a = max(operand_min, min(10, operand_max))
        b = max(operand_min, min(8, operand_max))
        return f'{{"question": "Maya has {a} toys. Her friend gives her {b} more. How many toys does Maya have now?", "expression": "{a} + {b}", "answer": {a + b}}}'
    elif op == 'subtraction':
        a = max(operand_min, min(15, operand_max))
        b = max(operand_min, min(7, operand_max))
        return f'{{"question": "There are {a} birds on a tree. {b} birds fly away. How many birds are left?", "expression": "{a} - {b}", "answer": {a - b}}}'
    elif op == 'multiplication':
        a = max(operand_min, min(8, operand_max))
        b = max(operand_min, min(6, operand_max))
        return f'{{"question": "Each basket has {a} apples. There are {b} baskets. How many apples in total?", "expression": "{a} × {b}", "answer": {a * b}}}'
    elif op == 'three_addend':
        a = max(operand_min, min(5, operand_max))
        b = max(operand_min, min(4, operand_max))
        c = max(operand_min, min(3, operand_max))
        return f'{{"question": "John has {a} red balls, {b} blue balls, and {c} yellow balls. How many balls does John have?", "expression": "{a} + {b} + {c}", "answer": {a + b + c}}}'
    elif op == 'missing_addend':
        answer = max(operand_min, min(10, operand_max))
        a = max(operand_min, min(6, operand_max))
        unknown = max(0, answer - a)
        return f'{{"question": "Sarah has some candies. She gets {a} more candies and now has {answer} total. How many candies did she have at first?", "expression": "□ + {a} = {answer}", "answer": {unknown}}}'
    else:
        return f'{{"question": "Tom has 2 apples. He gets 2 more. How many apples does Tom have?", "expression": "2 + 2", "answer": 4}}'


def _get_operation_instructions(operations: list, operand_min: int, operand_max: int, result_max: int) -> str:
    """
    Get operation-specific instructions based on curriculum.

    Args:
        operations: List of allowed operations
        operand_min: Minimum operand value
        operand_max: Maximum operand value
        result_max: Maximum result value

    Returns:
        Formatted instructions string
    """
    instructions = []

    for op in operations:
        if op == 'addition':
            instructions.append(f"Addition (a + b): Use operands between {operand_min}-{operand_max}, result ≤ {result_max}")
        elif op == 'subtraction':
            instructions.append(f"Subtraction (a - b): Use operands between {operand_min}-{operand_max}, result ≥ 0")
        elif op == 'multiplication':
            factors_max = operand_max
            product_max = result_max
            instructions.append(f"Multiplication (a × b): Use factors up to {factors_max}, product ≤ {product_max}")
        elif op == 'three_addend':
            instructions.append(f"Three addends (a + b + c): Use operands {operand_min}-{operand_max}, result ≤ {result_max}")
        elif op == 'missing_addend':
            instructions.append(f"Missing addend (□ + a = b): Generate with total ≤ {result_max}")

    return "\n".join(f"- {instr}" for instr in instructions) if instructions else "- Basic arithmetic"
