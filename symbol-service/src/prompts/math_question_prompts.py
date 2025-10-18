"""
Math Question Generation Prompts
Centralized prompts for AI-based question generation
"""


def get_question_generation_prompt(grade: int, performance_level: int, sublevel: str) -> str:
    """
    Generate AI prompt for math question generation based on grade, performance level, and sublevel.

    Args:
        grade: Grade level (1, 2, or 3)
        performance_level: Performance level (1, 2, or 3)
        sublevel: Sublevel name (Starter, Explorer, Solver, or Champion)

    Returns:
        Formatted prompt string for AI question generation
    """

    prompt = f"""Generate ONE math question appropriate for Grade {grade} student at Performance Level {performance_level}, {sublevel} sublevel.

Grade Levels: 1, 2, or 3
Performance Levels: 1, 2, or 3

Sublevel Guidelines:
- Starter: Basic foundational concepts, simple calculations
- Explorer: Developing skills, moderate complexity
- Solver: Competent problem solving, multi-step problems
- Champion: Advanced challenges, complex reasoning

Requirements:
1. Question must be appropriate for Grade {grade} curriculum
2. Difficulty matches Performance Level {performance_level} and {sublevel} sublevel
3. Return response in JSON format with these exact fields:
   - "question_text": The question to speak (e.g., "What is 5 plus 3?")
   - "expression": Mathematical notation (e.g., "5 + 3")
   - "answer": Numeric answer only (integer or decimal)
   - "operation": Operation type ("+", "-", "*", "/", or "word_problem")

Example for Grade 2, Performance Level 2, Explorer:
{{"question_text": "What is 24 divided by 6?", "expression": "24 ÷ 6", "answer": 4, "operation": "/"}}

Generate question now:"""

    return prompt


def get_system_prompt() -> str:
    """
    Get the system prompt for the AI math tutor.

    Returns:
        System prompt string
    """
    return "You are a math tutor creating grade-appropriate questions. Always respond with valid JSON only."


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
