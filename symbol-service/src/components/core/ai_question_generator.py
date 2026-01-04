"""
AI Question Generator Module

Generates curriculum-aligned math questions using OpenAI API.
Questions are tailored to student profile and curriculum specifications.
Generates questions on-demand without pre-generation delays.
"""

import json
import os
import re
import sys
from typing import Dict, List
from openai import OpenAI

# Add parent directory to path for imports
# Add parent directory to path for imports
# sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from src.components.core.curriculum_helper import CurriculumHelper
from src.prompts.ai_question_prompts import get_ai_question_generation_prompt


class AIQuestionGenerator:
    """Generate math questions using OpenAI based on curriculum specs on-demand."""

    MODEL = "gpt-3.5-turbo"
    TEMPERATURE = 0.7
    MAX_TOKENS = 200
    _client = None
    _recent_questions = []  # Track all recent questions to avoid duplicates
    _max_recent = 50  # Increased from 20 to be more aggressive about preventing duplicates
    _operation_sequence = {}  # Track operation sequence per profile for variety

    @staticmethod
    def _get_client():
        """Get or initialize OpenAI client lazily."""
        if AIQuestionGenerator._client is None:
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable is not set")
            AIQuestionGenerator._client = OpenAI(api_key=api_key)
        return AIQuestionGenerator._client

    @staticmethod
    def _get_profile_key(grade: int, level: int, sublevel: str) -> str:
        """Create a cache key from profile."""
        return f"{grade}_{level}_{sublevel}"

    @staticmethod
    def _get_next_operation(grade: int, level: int, sublevel: str, available_ops: list) -> str:
        """
        Determine which operation should be used for the next question.
        Cycles through available operations to ensure variety.

        Args:
            grade: Student grade
            level: Performance level
            sublevel: Sublevel
            available_ops: List of available operations from curriculum

        Returns:
            The operation to use for the next question
        """
        if len(available_ops) <= 1:
            return available_ops[0] if available_ops else 'addition'

        profile_key = AIQuestionGenerator._get_profile_key(grade, level, sublevel)

        # Get or initialize operation sequence for this profile
        if profile_key not in AIQuestionGenerator._operation_sequence:
            # Shuffle operations or start at random index to prevent same start on server restart
            import random
            AIQuestionGenerator._operation_sequence[profile_key] = {
                'operations': available_ops,
                'index': random.randint(0, len(available_ops) - 1)
            }

        seq = AIQuestionGenerator._operation_sequence[profile_key]
        current_op = seq['operations'][seq['index']]

        # Move to next operation for next time
        seq['index'] = (seq['index'] + 1) % len(seq['operations'])

        return current_op

    @staticmethod
    def generate_question(grade: int, level: int, sublevel: str) -> Dict:
        """
        Generate a curriculum-aligned question using AI on-demand.
        Generates one question at a time to avoid long startup delays.
        Tracks recent questions to avoid duplicates.

        Args:
            grade: Student grade (1, 2, or 3)
            level: Performance level (1, 2, or 3)
            sublevel: Sublevel (Starter, Explorer, Solver, Champion)

        Returns:
            Dictionary with 'question', 'expression', and 'answer' keys
        """
        profile_key = AIQuestionGenerator._get_profile_key(grade, level, sublevel)

        # Generate a single question on-demand
        spec = CurriculumHelper.get_spec(grade, level, sublevel)

        # Get the next operation in sequence for variety
        available_ops = spec.get('operations', ['addition'])
        next_operation = AIQuestionGenerator._get_next_operation(grade, level, sublevel, available_ops)

        curriculum_info = json.dumps(spec) if spec else "Basic arithmetic"
        prompt = get_ai_question_generation_prompt(
            grade, level, sublevel, curriculum_info, forced_operation=next_operation
        )

        max_retries = 3
        avoid_list = [q.get('expression', '') for q in AIQuestionGenerator._recent_questions[-3:]]
        
        for attempt in range(max_retries):
            # Regenerate/Update prompt with avoidance instructions
            current_prompt = prompt
            if attempt > 0 or avoid_list:
                 import random
                 current_prompt += f"\n\nVARIATION REQUEST {random.randint(1000, 9999)}: Ensure the numbers are different from: {', '.join(avoid_list)}. DO NOT REUSE these numbers."

            try:
                client = AIQuestionGenerator._get_client()
                response = client.chat.completions.create(
                    model=AIQuestionGenerator.MODEL,
                    messages=[{"role": "user", "content": current_prompt}],
                    temperature=AIQuestionGenerator.TEMPERATURE + (attempt * 0.1), # Increase creativity on retries
                    max_tokens=AIQuestionGenerator.MAX_TOKENS
                )

                response_text = response.choices[0].message.content.strip()
                question_data = json.loads(response_text)

                # Validate response format
                if AIQuestionGenerator._validate_response(question_data):
                    question_data['answer'] = int(question_data['answer'])

                    # Validate against curriculum specs
                    if not AIQuestionGenerator._validate_curriculum(question_data, spec):
                        print(f"⚠️ Invalid curriculum: {question_data}")
                        if attempt < max_retries - 1:
                            continue
                        else:
                            return AIQuestionGenerator.fallback_question()

                    # Check if question is unique (not in recent)
                    if not AIQuestionGenerator._is_duplicate(question_data):
                        AIQuestionGenerator._add_recent_question(question_data)
                        return question_data
                    
                    print(f"⚠️ Duplicate detected: {question_data['expression']}")
                    if attempt < max_retries - 1:
                        # Add this duplicate to avoid list for next retry
                        avoid_list.append(question_data.get('expression', ''))
                        continue
                    else:
                        # Use it anyway if we exhausted retries
                        AIQuestionGenerator._add_recent_question(question_data)
                        return question_data
                else:
                    if attempt < max_retries - 1:
                        continue
                    else:
                        return AIQuestionGenerator.fallback_question()

            except (json.JSONDecodeError, KeyError):
                if attempt < max_retries - 1:
                    continue
                else:
                    return AIQuestionGenerator.fallback_question()
            except Exception as e:
                print(f"⚠️ Generation error: {e}")
                if attempt < max_retries - 1:
                    continue
                else:
                    return AIQuestionGenerator.fallback_question()

        # Fallback if all else fails
        return AIQuestionGenerator.fallback_question()


    @staticmethod
    def _validate_response(question_data: Dict) -> bool:
        """Validate the AI response has required fields."""
        required_keys = ['question', 'expression', 'answer']
        return all(key in question_data for key in required_keys)

    @staticmethod
    def _validate_curriculum(question_data: Dict, spec: Dict) -> bool:
        """
        Validate that the generated question matches curriculum specifications.

        Args:
            question_data: Generated question dictionary
            spec: Curriculum specification from CurriculumHelper

        Returns:
            True if valid, False otherwise
        """
        if not spec:
            return True

        # Extract answer
        answer = question_data.get('answer')
        if answer is None:
            return False

        # Validate result is within curriculum range
        result_min = spec.get('result_min', 0)
        result_max = spec.get('result_max', 20)
        if not (result_min <= answer <= result_max):
            return False

        return True

    @staticmethod
    def _is_duplicate(question_data: Dict) -> bool:
        """
        Check if question is a duplicate or too similar to recent questions.
        Strict checking to ensure variety in operations AND context.

        Args:
            question_data: Question dictionary to check

        Returns:
            True if duplicate, False otherwise
        """
        expression = question_data.get('expression', '').strip()
        answer = question_data.get('answer')
        question_text = question_data.get('question', '').lower()
        pattern = AIQuestionGenerator._extract_pattern(expression)

        # Count how many recent questions have the same operation pattern
        same_pattern_count = 0
        same_context_count = 0

        # Define context keywords to detect similar scenarios
        context_keywords = {
            'box': ['box', 'boxes', 'carton'],
            'basket': ['basket', 'baskets'],
            'pack': ['pack', 'packs'],
            'group': ['group', 'groups'],
            'row': ['row', 'rows'],
            'shelf': ['shelf', 'shelves'],
        }

        def extract_context_type(text: str) -> str:
            """Extract the container/grouping type from question."""
            for context, keywords in context_keywords.items():
                for keyword in keywords:
                    if keyword in text:
                        return context
            return 'other'

        current_context = extract_context_type(question_text)

        for recent in AIQuestionGenerator._recent_questions:
            recent_expr = recent.get('expression', '').strip()
            recent_ans = recent.get('answer')
            recent_text = recent.get('question', '').lower()
            recent_pattern = AIQuestionGenerator._extract_pattern(recent_expr)
            recent_context = extract_context_type(recent_text)

            # Check if exact same expression - always a duplicate
            if recent_expr == expression:
                return True

            # Check if same answer with same operation pattern - too similar
            if answer is not None and answer == recent_ans and pattern == recent_pattern and pattern:
                return True

            # Count consecutive same operations
            if pattern == recent_pattern and pattern and len(pattern) == 1:
                same_pattern_count += 1

            # Count similar context (boxes, baskets, etc.) - should vary
            if current_context == recent_context and current_context != 'other':
                same_context_count += 1

        # Strict rules for variety
        # Don't allow more than 2 of the same operation in a row
        if same_pattern_count >= 2 and len(pattern) == 1:
            return True

        # Don't allow more than 1 of the same context type in last 5 questions
        if same_context_count >= 1:
            return True

        return False

    @staticmethod
    def _extract_pattern(expression: str) -> str:
        """
        Extract the operation pattern from an expression.
        E.g., "12 - 3 + 5" -> "-+", "6 × 3" -> "×"

        Args:
            expression: Math expression string

        Returns:
            Pattern string of operations (just the PRIMARY operation for single-op questions)
        """
        # Extract just the operations, ignoring numbers and formatting
        pattern = re.sub(r'[0-9\s\(\)□]', '', expression)

        # For penalty purposes, if there's only one operation, return just that one
        # This helps detect when we're repeating the same single operation too much
        if len(pattern) == 1:
            return pattern

        # For multi-operation patterns, return the simplified pattern
        return pattern

    @staticmethod
    def _add_recent_question(question_data: Dict):
        """
        Add question to recent questions list.

        Args:
            question_data: Question dictionary to add
        """
        AIQuestionGenerator._recent_questions.append(question_data)
        # Keep only the most recent questions
        if len(AIQuestionGenerator._recent_questions) > AIQuestionGenerator._max_recent:
            AIQuestionGenerator._recent_questions.pop(0)

    @staticmethod
    def fallback_question() -> Dict:
        """Return a fallback question if AI generation fails."""
        return {
            'question': 'Tom has 5 apples. He gets 3 more. How many apples does Tom have?',
            'expression': '5 + 3',
            'answer': 8
        }
