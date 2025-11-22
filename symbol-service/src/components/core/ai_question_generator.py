"""
AI Question Generator Module

Generates curriculum-aligned math questions using OpenAI API.
Questions are tailored to student profile and curriculum specifications.
"""

import json
import os
import sys
from typing import Dict
from openai import OpenAI

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from components.core.curriculum_helper import CurriculumHelper
from prompts.ai_question_prompts import get_ai_question_generation_prompt


class AIQuestionGenerator:
    """Generate math questions using OpenAI based on curriculum specs."""

    MODEL = "gpt-3.5-turbo"
    TEMPERATURE = 0.7
    MAX_TOKENS = 200
    _client = None
    _recent_questions = []
    _max_recent = 10

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
    def generate_question(grade: int, level: int, sublevel: str) -> Dict:
        """
        Generate a curriculum-aligned question using AI.
        Prevents duplicate questions from being generated.

        Args:
            grade: Student grade (1, 2, or 3)
            level: Performance level (1, 2, or 3)
            sublevel: Sublevel (Starter, Explorer, Solver, Champion)

        Returns:
            Dictionary with 'question', 'expression', and 'answer' keys
        """
        # Get curriculum spec for student profile (grade, level, sublevel)
        spec = CurriculumHelper.get_spec(grade, level, sublevel)
        curriculum_info = json.dumps(spec) if spec else "Basic arithmetic"

        # Get prompt from prompts module with all profile info
        prompt = get_ai_question_generation_prompt(grade, level, sublevel, curriculum_info)

        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                client = AIQuestionGenerator._get_client()
                response = client.chat.completions.create(
                    model=AIQuestionGenerator.MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=AIQuestionGenerator.TEMPERATURE,
                    max_tokens=AIQuestionGenerator.MAX_TOKENS
                )

                response_text = response.choices[0].message.content.strip()
                question_data = json.loads(response_text)

                # Validate response
                if AIQuestionGenerator._validate_response(question_data):
                    question_data['answer'] = int(question_data['answer'])

                    # Check if question is duplicate
                    if not AIQuestionGenerator._is_duplicate(question_data):
                        AIQuestionGenerator._add_recent_question(question_data)
                        return question_data
                    else:
                        if attempt < max_attempts - 1:
                            print("⚠️ Duplicate question, regenerating...")
                            continue
                else:
                    print("⚠️ Invalid response format from AI")
                    return AIQuestionGenerator.fallback_question()

            except json.JSONDecodeError:
                print("⚠️ Could not parse AI response")
                return AIQuestionGenerator.fallback_question()
            except Exception as e:
                print(f"⚠️ AI generation error: {e}")
                return AIQuestionGenerator.fallback_question()

        # If we exhausted attempts, return fallback
        return AIQuestionGenerator.fallback_question()

    @staticmethod
    def _validate_response(question_data: Dict) -> bool:
        """Validate the AI response has required fields."""
        required_keys = ['question', 'expression', 'answer']
        return all(key in question_data for key in required_keys)

    @staticmethod
    def _is_duplicate(question_data: Dict) -> bool:
        """
        Check if question is a duplicate of recent questions.

        Args:
            question_data: Question dictionary to check

        Returns:
            True if duplicate, False otherwise
        """
        expression = question_data.get('expression', '').strip()
        for recent in AIQuestionGenerator._recent_questions:
            if recent.get('expression', '').strip() == expression:
                return True
        return False

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
            'question': '2 plus 2',
            'expression': '2 + 2',
            'answer': 4
        }
