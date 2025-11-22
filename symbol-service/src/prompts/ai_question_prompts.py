"""
AI Question Generation Prompts

Provides prompt templates for OpenAI to generate curriculum-aligned math questions.
"""


def get_ai_question_generation_prompt(grade: int, sublevel: str, curriculum_info: str) -> str:
    """
    Build the prompt for OpenAI to generate a math question.

    Args:
        grade: Student grade (1, 2, or 3)
        sublevel: Sublevel (Starter, Explorer, Solver, Champion)
        curriculum_info: JSON string with curriculum specifications

    Returns:
        Formatted prompt string for OpenAI
    """
    grade_guidelines = _get_grade_guidelines(grade)

    return f"""Generate ONE math question for Grade {grade} {sublevel} student.

{grade_guidelines}

Constraints: {curriculum_info}

RESPOND WITH ONLY THIS JSON (no other text):
{{"question": "simple question like '5 plus 3'", "expression": "5 + 3", "answer": 8}}

Rules:
- Question: short, no "what is" prefix
- Expression: math notation
- Answer: single number only
- Keep numbers grade-appropriate
- One question only"""


def _get_grade_guidelines(grade: int) -> str:
    """Get grade-specific guidelines."""
    guidelines = {
        1: """Grade 1 Guidelines:
- Use numbers 0-20 only
- Focus on addition with small numbers (e.g., 2+3, 5+4, 1+1)
- Questions should be very simple and direct
- No multiplication or division""",
        2: """Grade 2 Guidelines:
- Use numbers 0-50
- Mix of addition and subtraction (e.g., 15+8, 23-7)
- Can include basic multiplication as repeated addition
- Keep questions simple and direct""",
        3: """Grade 3 Guidelines:
- Use numbers up to 100
- Mix of addition, subtraction, multiplication
- Can include division concepts
- Questions can be slightly more complex"""
    }
    return guidelines.get(grade, guidelines[1])
