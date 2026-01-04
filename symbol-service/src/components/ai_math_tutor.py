#!/usr/bin/env python3
"""
AI Math Tutor (Text Mode)

Features:
- AI generates questions (same robust logic as Voice Tutor)
- Text-only interface (no voice output/input latency)
- User types answers
"""

import time
import random
import threading
import os
import sys
import re
import json
import platform
from typing import Dict, Optional
from queue import Queue
from concurrent.futures import ThreadPoolExecutor
from openai import OpenAI
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from config.tutor_config import StudentProfile
from prompts.math_question_prompts import (
    get_question_generation_prompt,
    get_system_prompt,
    get_fallback_question_config,
    get_uniqueness_prompt,
    get_correct_answer_feedback_prompt,
    get_wrong_answer_feedback_prompt,
    get_feedback_system_prompt,
    get_image_generation_prompt
)

# Load environment variables
load_dotenv()


class AIMathTutor:
    """AI Math Tutor - Text Only Version"""

    def __init__(self, grade: int = 1, performance_level: int = 1, sublevel: str = "Starter"):
        """Initialize"""
        self.input_mode = "typing"

        # Initialize OpenAI client
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        self.openai_client = OpenAI(api_key=api_key)

        # Student profile
        self.student_profile = StudentProfile(
            grade=grade,
            performance_level=performance_level,
            sublevel=sublevel
        )

        # Statistics
        self.stats = {
            'total_questions': 0,
            'correct_answers': 0,
            'wrong_answers': 0
        }

        # Track recent questions to avoid repetition
        self.recent_questions = []
        self.max_recent_questions = 10

        # Track used themes
        self.recent_themes = []
        self.max_recent_themes = 8

        # Image generation settings
        self.enable_images = True
        self.image_cache = {}
        self.image_cache_size = 20

        # Pre-generation queue settings
        self.question_queue = Queue(maxsize=10)
        self.queue_target_size = 5
        self.generation_executor = ThreadPoolExecutor(max_workers=4)
        self.queue_worker_thread = None
        self.queue_worker_running = False
        self.queue_check_interval = 0.2

    def setup_voice(self):
        """No voice setup needed"""
        pass

    def speak_with_display(self, text: str):
        """Just print text, no voice"""
        print(f"AI: {text}")

    def generate_ai_question(self) -> Dict:
        """
        Generate a unique, diverse math question using advanced AI.
        (Identical logic to Voice Tutor to maintain quality)
        """
        max_attempts = 5
        for attempt in range(max_attempts):
            try:
                base_prompt = get_question_generation_prompt(
                    grade=self.student_profile.grade,
                    performance_level=self.student_profile.performance_level,
                    sublevel=self.student_profile.sublevel
                )

                uniqueness_parts = []
                if self.recent_questions:
                    recent_expressions = [q['expression'] for q in self.recent_questions[-10:]]
                    recent_operations = [q.get('operation', '') for q in self.recent_questions[-5:]]
                    recent_numbers = []
                    for expr in recent_expressions[-5:]:
                        numbers = re.findall(r'\d+', expr)
                        recent_numbers.extend(numbers)

                    uniqueness_constraints = get_uniqueness_prompt(
                        recent_expressions=recent_expressions,
                        recent_operations=recent_operations,
                        recent_numbers=recent_numbers,
                        attempt=attempt
                    )
                    uniqueness_parts.append(uniqueness_constraints)

                if self.recent_themes:
                    theme_constraint = f"\n\nAVOID THEMES: {', '.join(self.recent_themes[-self.max_recent_themes:])}\n"
                    uniqueness_parts.append(theme_constraint)

                prompt = base_prompt + ''.join(uniqueness_parts) if uniqueness_parts else base_prompt
                system_prompt = get_system_prompt()

                response = self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=1.0,
                    max_tokens=200,
                    presence_penalty=0.6,
                    frequency_penalty=0.6
                )

                ai_content = response.choices[0].message.content.strip()
                if "```json" in ai_content:
                    ai_content = ai_content.split("```json")[1].split("```")[0].strip()
                elif "```" in ai_content:
                    ai_content = ai_content.split("```")[1].split("```")[0].strip()

                question_data = json.loads(ai_content)
                
                # Validation
                required = ['question_text', 'expression', 'answer', 'operation']
                if not all(field in question_data for field in required):
                    continue

                if isinstance(question_data['answer'], str):
                    question_data['answer'] = float(question_data['answer'])

                # Check duplicate
                if any(q['expression'] == question_data['expression'] for q in self.recent_questions):
                    if attempt < max_attempts - 1: continue

                # Success
                self.recent_questions.append(question_data)
                if len(self.recent_questions) > self.max_recent_questions:
                    self.recent_questions.pop(0)

                theme = self._extract_theme_from_question(question_data['question_text'])
                if theme:
                    self.recent_themes.append(theme)
                    if len(self.recent_themes) > self.max_recent_themes:
                        self.recent_themes.pop(0)

                return question_data

            except json.JSONDecodeError:
                if attempt < max_attempts - 1: time.sleep(1); continue
            except Exception as e:
                # Exponential backoff logic from Voice Tutor fix
                error_str = str(e).lower()
                wait_time = (attempt + 1) * 2
                if "rate limit" in error_str or "429" in error_str:
                     print(f"⏳ Rate limit hit. Waiting {wait_time}s...")
                     time.sleep(wait_time)
                else:
                     time.sleep(1)
                if attempt < max_attempts - 1: continue

        return self._generate_fallback_question()

    def _generate_fallback_question(self) -> Dict:
        # Simplified fallback
        return {
            'question_text': 'What is 1 plus 1?',
            'expression': '1 + 1',
            'answer': 2,
            'operation': '+'
        }

    # ... Include parallel generation and cache methods ...
    def _generate_complete_question_parallel(self) -> Dict:
        question_data = self.generate_ai_question()
        if self.enable_images:
            try:
                # Use synchronous call in thread for simplicity or reuse voice tutor method?
                # For clean separation, we reimplement simpler version.
                # Actually, reuse the generation executor.
                future = self.generation_executor.submit(self._generate_question_image, question_data)
                question_data['image_url'] = future.result(timeout=30)
            except:
                question_data['image_url'] = None
        return question_data

    def _queue_worker(self):
        while self.queue_worker_running:
            try:
                if self.question_queue.qsize() < self.queue_target_size:
                    data = self._generate_complete_question_parallel()
                    try: self.question_queue.put(data, block=False)
                    except: pass
                else:
                    time.sleep(self.queue_check_interval)
            except:
                time.sleep(self.queue_check_interval)

    def start_queue_worker(self):
        if not self.queue_worker_running:
            self.queue_worker_running = True
            self.queue_worker_thread = threading.Thread(target=self._queue_worker, daemon=True)
            self.queue_worker_thread.start()
            time.sleep(0.2)

    def stop_queue_worker(self):
        self.queue_worker_running = False
        if self.queue_worker_thread:
            self.queue_worker_thread.join(timeout=1)

    def get_next_question(self) -> Dict:
        try:
            return self.question_queue.get(block=False)
        except:
            return self._generate_complete_question_parallel()

    def _extract_theme_from_question(self, text: str) -> Optional[str]:
        # Simple extraction
        words = text.lower().split()
        themes = ['apples', 'candies', 'cars', 'toys', 'books']
        for t in themes:
            if t in words: return t.rstrip('s')
        return None

    def _get_image_cache_key(self, data: Dict) -> Optional[str]:
        theme = self._extract_theme_from_question(data['question_text'])
        if not theme: return None
        op = 'add' if '+' in data.get('expression','') else 'sub'
        return f"{theme}_{op}"

    def _generate_question_image(self, data: Dict) -> str:
        if not self.enable_images: return None
        try:
            cache_key = self._get_image_cache_key(data)
            if cache_key and cache_key in self.image_cache: return self.image_cache[cache_key]

            prompt = get_image_generation_prompt(data['question_text'], self.student_profile.grade)
            response = self.openai_client.images.generate(
                model="dall-e-3", prompt=prompt, size="1024x1024", quality="standard", n=1
            )
            url = response.data[0].url
            if cache_key: self.image_cache[cache_key] = url
            return url
        except Exception:
            return None

    def _generate_correct_feedback(self, answer, text):
        return "Correct!"

    def _generate_wrong_feedback(self, user, correct, text, expr):
        return f"Incorrect. The answer is {correct}."

    def get_user_input(self):
        return input().strip()

    def ask_question(self, data):
        print(f"{data['expression']} = ?")
        user_input = self.get_user_input()
        if user_input.lower() == 'quit': return 'quit'
        try:
            val = int(user_input)
            return val == data['answer']
        except:
            return False

    def run_session(self, num_questions=5):
        pass 
