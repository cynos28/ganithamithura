"""
Math Question Generation Prompts
Centralized prompts for AI-based question generation, hints, explanations, and recommendations
"""


def get_question_generation_prompt(grade: int, performance_level: int, sublevel: str) -> str:
    """
    Generate enhanced AI prompt for math question generation based on grade, performance level, and sublevel.

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

    # Define difficulty-specific approaches
    difficulty_guidance = {
        1: {
            "Starter": "Use single-digit numbers (1-10). Focus on basic addition and subtraction. Make it simple and concrete.",
            "Explorer": "Use numbers up to 20. Introduce simple patterns. Can include basic multiplication (2, 5, 10 tables).",
            "Solver": "Use numbers up to 30. Include two-step thinking. Mix operations strategically.",
            "Champion": "Use numbers up to 50. Create engaging word problems. Challenge logical thinking."
        },
        2: {
            "Starter": "Use numbers 1-20. Basic operations with clear patterns. Build confidence.",
            "Explorer": "Use numbers up to 50. Introduce multiplication and division. Create relatable scenarios.",
            "Solver": "Use numbers up to 100. Multi-step problems. Combine different operations.",
            "Champion": "Use numbers up to 200. Complex word problems. Real-world applications."
        },
        3: {
            "Starter": "Use numbers up to 50. Reinforce fundamentals with variety.",
            "Explorer": "Use numbers up to 100. Practical applications. Introduce fractions conceptually.",
            "Solver": "Use numbers up to 500. Complex scenarios. Multi-step reasoning required.",
            "Champion": "Use numbers up to 1000. Advanced word problems. Real-world mathematical thinking."
        }
    }

    contexts = grade_contexts.get(grade, grade_contexts[1])
    guidance = difficulty_guidance.get(performance_level, difficulty_guidance[1]).get(sublevel, "")

    prompt = f"""You are an expert math educator creating an engaging, educational question for a Grade {grade} student.

STUDENT PROFILE:
- Grade: {grade}
- Performance Level: {performance_level} (1=Beginning, 2=Intermediate, 3=Advanced)
- Sublevel: {sublevel}

DIFFICULTY GUIDANCE:
{guidance}

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


def get_image_generation_prompt(question_text: str, expression: str, grade: int) -> str:
    """
    Generate DALL-E prompt for creating question illustration.

    Args:
        question_text: The math question
        expression: Mathematical expression
        grade: Student's grade level

    Returns:
        DALL-E prompt for image generation
    """
    return f"""Create a simple, colorful, child-friendly illustration for this math question: "{question_text}"

Style requirements:
- Bright, cheerful colors
- Simple, clear cartoon style appropriate for Grade {grade} children
- Clean, uncluttered composition
- Show the objects/characters mentioned in the question
- Make it educational and engaging
- No text or numbers in the image
- Suitable for elementary school students"""


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
