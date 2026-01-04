"""
AI Question Generation Prompts

Provides prompt templates for OpenAI to generate curriculum-aligned math questions.
Uses CurriculumHelper specifications to ensure grade and level-specific content.
"""

import json


def _convert_operations_to_names(operations: list) -> list:
    """
    Convert operation symbols from curriculum_spec.py to readable names.

    Args:
        operations: List of operations (e.g., ['+', '-', '×'])

    Returns:
        List of operation names (e.g., ['addition', 'subtraction', 'multiplication'])
    """
    symbol_to_name = {
        '+': 'addition',
        '-': 'subtraction',
        '×': 'multiplication',
        'x': 'multiplication',
        '*': 'multiplication',
        'unknown_addend': 'missing_addend',
        'brackets': 'brackets',
    }

    converted = []
    for op in operations:
        name = symbol_to_name.get(op, op)
        if name not in converted:
            converted.append(name)

    return converted if converted else ['addition']


def _get_grade_name(grade: int) -> str:
    """Get grade name for prompt."""
    grade_names = {1: "Grade 1", 2: "Grade 2", 3: "Grade 3"}
    return grade_names.get(grade, "Grade 1")


def get_ai_question_generation_prompt(grade: int, level: int, sublevel: str, curriculum_info: str, forced_operation: str = None) -> str:
    """
    Build the prompt for OpenAI to generate a math question.
    Uses curriculum specifications from CurriculumHelper to generate grade and level-specific questions.

    Args:
        grade: Student grade (1, 2, or 3)
        level: Performance level (1, 2, or 3)
        sublevel: Sublevel (Starter, Explorer, Solver, Champion)
        curriculum_info: JSON string with curriculum specifications from CurriculumHelper.get_spec()
        forced_operation: Optional operation to force (for variety in non-Champion levels)

    Returns:
        Formatted prompt string for OpenAI
    """
    # Parse curriculum spec from CurriculumHelper
    try:
        curriculum_spec = json.loads(curriculum_info)
    except (json.JSONDecodeError, TypeError):
        curriculum_spec = {}

    # Build detailed prompt based on curriculum spec
    detailed_prompt = _build_detailed_prompt(grade, level, sublevel, curriculum_spec, forced_operation)

    return detailed_prompt


def _build_detailed_prompt(grade: int, level: int, sublevel: str, spec: dict, forced_operation: str = None) -> str:
    """
    Build detailed prompt using curriculum specification details.

    Args:
        grade: Student grade (1, 2, or 3)
        level: Performance level (1, 2, or 3)
        sublevel: Student sublevel (Starter, Explorer, Solver, Champion)
        spec: Curriculum specification dictionary from CurriculumHelper
        forced_operation: Optional operation to force for variety (for non-Champion levels)

    Returns:
        Formatted prompt string for OpenAI
    """
    if not spec:
        return f"""Generate ONE simple math question for Grade {grade}, Level {level}, {sublevel} student.
RESPOND WITH ONLY THIS JSON (no other text):
{{"question": "2 plus 2", "expression": "2 + 2", "answer": 4}}"""

    # Extract key specifications
    operations = spec.get('operations', ['addition'])

    # Convert operation symbols to names if needed (from curriculum_spec.py)
    operations = _convert_operations_to_names(operations)

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

    # Build focused examples based on operations and focus
    examples = _build_examples_for_focus(grade, level, sublevel, simple_operations)

    # Determine operation strategy based on sublevel
    is_champion = sublevel == 'Champion'

    # Build operation instructions more explicitly
    if forced_operation and not is_champion:
        # For non-champion with forced operation: be VERY explicit
        operation_rule = f"MUST use the '{forced_operation}' operation ONLY. Create a question with exactly one {forced_operation} operation. Example: if {forced_operation}='multiplication' then use '5 × 3', if 'addition' use '12 + 8', if 'subtraction' use '20 - 7'."
    elif len(simple_operations) > 1:
        if is_champion:
            operation_rule = f"MUST use multiple operations in a SINGLE question. Mix and combine {', '.join(simple_operations)} (e.g., '(3 × 4) + 8 = 20'). NO single-operation questions."
        else:
            # For non-champion: explicitly list operations
            operation_rule = f"Generate question using EXACTLY ONE of these operations: {' OR '.join(simple_operations)}"
    else:
        operation_rule = f"Use only {simple_operations[0]} operation."

    return f"""CURRICULUM: Grade {grade}, Level {level}, {sublevel}
LEARNING FOCUS: {focus if focus else 'General math practice'}
Operands: {operand_min}-{operand_max}
Results: {result_min}-{result_max}
Allowed Operations: {', '.join(simple_operations)}

Generate ONE child-friendly math question aligned with the LEARNING FOCUS:

OPERATION REQUIREMENT (MANDATORY):
{operation_rule}

CRITICAL RULES:
1. MUST focus on: {focus if focus else 'varied math operations'}
2. Create a SHORT, FUN, relatable scenario for a {_get_grade_name(grade)} student
3. Use simple words children understand
4. Include relatable context (toys, animals, fruits, school, friends, space, magic, etc.)
5. Question format: KEEP IT SIMPLE but VARY structure (e.g., "There are...", "I see...", "If you have...", "Tom finds...")
6. Keep operands between {operand_min}-{operand_max}
7. Keep result between {result_min}-{result_max}
8. NO "What is", NO "Calculate", NO complex language
9. EXTREMELY IMPORTANT: VARY THE SENTENCE STRUCTURE
   - DO NOT always say "Person has X. Person gets Y."
   - Use: "There are 3 frogs. 2 more hop in."
   - Use: "I see 5 stars. Look, 4 more stars appear!"
   - Use: "If you have 6 cookies and bake 6 more..."
   - Use: "A box holds 10 crayons. 5 are red. How many are not red?"
   - NEVER repeat the previous question's structure.
10. DO NOT create similar questions - be extremely creative

SPECIFIC EXAMPLES for {_get_grade_name(grade)} {sublevel}:
{examples}

RESPOND WITH ONLY THIS JSON (no extra text):
{{"question": "creative child-friendly story", "expression": "A op B" or "A op B op C", "answer": number}}"""


def _build_examples_for_focus(grade: int, level: int, sublevel: str, operations: list) -> str:
    """
    Build curriculum-specific examples based on grade, level, and focus.

    Args:
        grade: Student grade (1, 2, or 3)
        level: Performance level (1, 2, or 3)
        sublevel: Student sublevel
        operations: List of allowed operations

    Returns:
        Formatted examples string
    """
    # Examples for different grades and sublevels
    if grade == 1:
        if sublevel == 'Starter':
            return '''- "I see 3 blue birds. 2 red birds fly in. How many birds are there now?" (3 + 2 = 5)
- "There are 4 cookies on a plate. Mom puts 1 more cookie. How many cookies altogether?" (4 + 1 = 5)
- "If you find 2 shells and your friend finds 2 shells, how many shells do you have together?" (2 + 2 = 4)'''
        elif sublevel == 'Explorer':
            return '''- "There are 5 stars in the sky. Look! 5 more stars appear. How many stars do you see?" (5 + 5 = 10)
- "A cat has 4 legs. A dog has 4 legs. How many legs do they have together?" (4 + 4 = 8)'''
        elif sublevel == 'Solver':
            return '''- "You have 7 stickers. You win 4 more in a game. How many stickers do you have now?" (7 + 4 = 11)
- "There are 6 ducks in the pond. 4 more ducks jump in. How many ducks are swimming?" (6 + 4 = 10)'''
        elif sublevel == 'Champion':
            return '- "Zara collects 8 pencils. Ben gives her 6 more. How many pencils does Zara have?" (8 + 6 = 14)'

    elif grade == 2:
        if sublevel == 'Starter':
            return '- "Alex has 12 marbles. He gives 5 to his friend. How many marbles does Alex have left?" (12 - 5 = 7)\n- "There are 6 flowers. Each flower has 3 petals. How many petals total?" (6 × 3 = 18)'
        elif sublevel == 'Explorer':
            return '- "Sam has 4 groups of 6 stickers. How many stickers total?" (4 × 6 = 24)'
        elif sublevel == 'Solver':
            return '- "Tom has 15 toys. He gives away 6 and buys 4 more. How many does he have?" (15 - 6 + 4 = 13)\n- "There are 3 boxes. Each box has 5 pencils. How many pencils total?" (3 × 5 = 15)'
        elif sublevel == 'Champion':
            return '- "Lisa has 20 candies. She eats 8 and gets 12 more. How many does she have?" (20 - 8 + 12 = 24)\n- "(3 × 4) + 8 = 20"'

    elif grade == 3:
        if sublevel == 'Starter':
            return '- "Jordan has 35 stickers. He gives 18 to a friend. How many does he have left?" (35 - 18 = 17)\n- "There are 7 groups of 8 apples. How many apples total?" (7 × 8 = 56)'
        elif sublevel == 'Explorer':
            return '- "Mia has 15 toy cars. She gets 12 more. How many does she have?" (15 + 12 = 27)\n- "Each student has 9 crayons. There are 8 students. How many crayons total?" (9 × 8 = 72)'
        elif sublevel == 'Solver':
            return '''- "Noah had 20 candies. He ate 5 and then got 8 more. How many candies does he have?" (20 - 5 + 8 = 23)
- "Each student planted 6 trees. There are 3 students. How many trees total?" (6 × 3 = 18)
- "There were 30 pencils. Tom lost 12. How many are left?" (30 - 12 = 18)
- "(6 × 3) + 7 = 25"
- "(15 - 4) + (2 × 3) = 17"
- "A store had 25 books. They sold 8 and got 5 new ones. How many books now?" (25 - 8 + 5 = 22)
- "Emma made 4 groups of 9 cookies. How many cookies?" (4 × 9 = 36)'''
        elif sublevel == 'Champion':
            return '- "Lily has 50 stickers. She gives away 15 and then buys 2 packs of 12. How many stickers does she have?" (50 - 15 + (2 × 12) = 59)\n- "(8 × 7) - 16 + 5 = 37"\n- "Two students have 12 marbles each. Another student has 8. How many marbles total?" ((2 × 12) + 8 = 32)'

    # Default fallback
    return '- "Sarah has 5 items. She gets 3 more. How many total?" (5 + 3 = 8)'


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
