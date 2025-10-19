#!/usr/bin/env python3
"""
AI Voice Math Tutor - Voice Output with Letter-by-Letter Display

Features:
- AI speaks questions aloud
- Text displays letter-by-letter synchronized with speech
- User types answers (no voice input needed)
- Simple math practice
"""

import pyttsx3
import time
import random
import threading
import os
import sys
import re
import json
import subprocess
import platform
from typing import Dict
from openai import OpenAI
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from config.tutor_config import TutorConfig, StudentProfile
from prompts.math_question_prompts import (
    get_question_generation_prompt,
    get_system_prompt,
    get_fallback_question_config,
    get_uniqueness_prompt,
    get_correct_answer_feedback_prompt,
    get_wrong_answer_feedback_prompt,
    get_feedback_system_prompt
)

# Load environment variables
load_dotenv()


class AIVoiceMathTutor:
    """AI Math Tutor with voice output and synchronized text display"""

    def __init__(self, grade: int = 1, performance_level: int = 1, sublevel: str = "Starter"):
        """Initialize the AI Voice Math Tutor

        Args:
            grade: Grade level (1, 2, or 3)
            performance_level: Performance level (1, 2, or 3)
            sublevel: Sublevel name (Starter, Explorer, Solver, or Champion)
        """
        print("🚀 Initializing AI Voice Math Tutor...")

        # Initialize OpenAI client
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        self.openai_client = OpenAI(api_key=api_key)

        # Initialize text-to-speech engine
        self.engine = pyttsx3.init()
        self.setup_voice()

        # Create student profile with validated settings
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

        print(f"✅ AI Voice Math Tutor ready! {self.student_profile}\n")

    def setup_voice(self):
        """Setup text-to-speech voice"""
        try:
            voices = self.engine.getProperty('voices')

            # Try to find a good voice
            selected_voice = None
            for voice in voices:
                if any(name in voice.name.lower() for name in ['eddie', 'alex', 'victoria', 'karen']):
                    selected_voice = voice
                    break

            if selected_voice:
                self.engine.setProperty('voice', selected_voice.id)
                print(f"🔊 Voice: {selected_voice.name}")
            else:
                if voices:
                    self.engine.setProperty('voice', voices[0].id)
                    print(f"🔊 Voice: {voices[0].name}")

            # Speech settings
            self.engine.setProperty('rate', 140)  # Speed
            self.engine.setProperty('volume', 1.0)  # Volume

        except Exception as e:
            print(f"⚠️ Voice setup warning: {e}")
            print("Using default voice")

    def speak_with_display(self, text: str):
        """
        Speak text while displaying letter-by-letter synchronized with speech.

        Args:
            text: Text to speak and display
        """
        print("\n🔊 ", end="", flush=True)

        # Check if we're on macOS to use 'say' command (more reliable)
        if platform.system() == 'Darwin':
            try:
                # Calculate char delay for sync
                # Speech rate 140 WPM = ~2.3 words/sec, ~5 chars/word = ~11.5 chars/sec
                char_delay = 0.087  # ~11.5 chars per second

                # Start speech in background using macOS 'say' command
                speech_process = subprocess.Popen(
                    ['say', '-r', '140', text],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )

                # Small delay for speech to start
                time.sleep(0.1)

                # Display text letter by letter
                for char in text:
                    print(char, end="", flush=True)
                    time.sleep(char_delay)

                # Wait for speech to complete
                speech_process.wait(timeout=10)

            except Exception as e:
                print(f"\n⚠️ macOS say error: {e}")
                # Fallback to pyttsx3
                self._speak_with_pyttsx3(text)
        else:
            # Use pyttsx3 for non-macOS systems
            self._speak_with_pyttsx3(text)

        print()  # New line

    def _speak_with_pyttsx3(self, text: str):
        """Fallback speech method using pyttsx3"""
        try:
            # Calculate char delay
            rate = self.engine.getProperty('rate')
            chars_per_second = (rate * 5) / 60
            char_delay = 1.0 / chars_per_second if chars_per_second > 0 else 0.08

            # Run speech in thread
            speech_done = threading.Event()

            def speak():
                try:
                    self.engine.say(text)
                    self.engine.runAndWait()
                finally:
                    speech_done.set()

            speech_thread = threading.Thread(target=speak, daemon=True)
            speech_thread.start()

            # Small delay for speech to start
            time.sleep(0.15)

            # Display text letter by letter
            for char in text:
                print(char, end="", flush=True)
                time.sleep(char_delay)

            # Wait for speech to complete
            speech_thread.join(timeout=10)

        except Exception as e:
            print(f"\n⚠️ Speech error: {e}")

    def generate_ai_question(self) -> Dict:
        """
        Generate a unique, diverse math question using advanced AI.
        Ensures questions are always different with multiple retry attempts.
        """
        max_attempts = 5  # Try up to 5 times to get a unique question

        for attempt in range(max_attempts):
            try:
                # Get base prompt from external prompt file
                base_prompt = get_question_generation_prompt(
                    grade=self.student_profile.grade,
                    performance_level=self.student_profile.performance_level,
                    sublevel=self.student_profile.sublevel
                )

                # Build comprehensive uniqueness constraints
                if self.recent_questions:
                    # Extract all recent question details
                    recent_expressions = [q['expression'] for q in self.recent_questions[-10:]]
                    recent_operations = [q.get('operation', '') for q in self.recent_questions[-5:]]
                    recent_numbers = []

                    # Extract numbers from recent expressions
                    for expr in recent_expressions[-5:]:
                        numbers = re.findall(r'\d+', expr)
                        recent_numbers.extend(numbers)

                    # Get uniqueness prompt from prompts folder
                    uniqueness_constraints = get_uniqueness_prompt(
                        recent_expressions=recent_expressions,
                        recent_operations=recent_operations,
                        recent_numbers=recent_numbers,
                        attempt=attempt
                    )

                    prompt = base_prompt + uniqueness_constraints
                else:
                    prompt = base_prompt

                # Get system prompt from prompts folder
                system_prompt = get_system_prompt()

                # Call OpenAI API with higher temperature for variety
                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=1.0,  # Maximum creativity
                    max_tokens=200,
                    presence_penalty=0.6,  # Discourage repetition
                    frequency_penalty=0.6   # Encourage variety
                )

                # Parse AI response
                ai_content = response.choices[0].message.content.strip()

                # Extract JSON from response (handle markdown code blocks)
                if "```json" in ai_content:
                    ai_content = ai_content.split("```json")[1].split("```")[0].strip()
                elif "```" in ai_content:
                    ai_content = ai_content.split("```")[1].split("```")[0].strip()

                question_data = json.loads(ai_content)

                # Validate required fields
                required_fields = ['question_text', 'expression', 'answer', 'operation']
                if not all(field in question_data for field in required_fields):
                    raise ValueError(f"Missing required fields. Got: {question_data.keys()}")

                # Ensure answer is numeric
                if isinstance(question_data['answer'], str):
                    question_data['answer'] = float(question_data['answer'])

                # Check if this question is truly unique
                expression = question_data['expression']
                is_duplicate = any(q['expression'] == expression for q in self.recent_questions)

                if is_duplicate and attempt < max_attempts - 1:
                    print(f"🔄 Duplicate detected on attempt {attempt + 1}, retrying...")
                    continue  # Try again

                # Success! Add to recent questions
                self.recent_questions.append(question_data)
                if len(self.recent_questions) > self.max_recent_questions:
                    self.recent_questions.pop(0)

                if attempt > 0:
                    print(f"✅ Unique question generated on attempt {attempt + 1}")

                return question_data

            except json.JSONDecodeError as e:
                print(f"⚠️ JSON parsing error on attempt {attempt + 1}: {e}")
                if attempt < max_attempts - 1:
                    continue  # Try again
            except Exception as e:
                print(f"⚠️ AI generation error on attempt {attempt + 1}: {e}")
                if attempt < max_attempts - 1:
                    continue  # Try again

        # All attempts failed, use fallback
        print("📝 All AI attempts exhausted, using fallback question generation")
        return self._generate_fallback_question()

    def _generate_fallback_question(self) -> Dict:
        """Fallback question generator (traditional method)"""
        # Get fallback config from external config file
        config = get_fallback_question_config(
            grade=self.student_profile.grade,
            performance_level=self.student_profile.performance_level,
            sublevel=self.student_profile.sublevel
        )

        min_val, max_val = config['range']
        operations = config['operations']

        # Try to generate unique question (max 10 attempts)
        max_attempts = 10
        question_data = None

        for attempt in range(max_attempts):
            operation = random.choice(operations)

            if operation == '+':
                a = random.randint(min_val, max_val)
                b = random.randint(min_val, max_val)
                answer = a + b
                question_text = f"What is {a} plus {b}?"
                expression = f"{a} + {b}"

            elif operation == '-':
                a = random.randint(min_val + 5, max_val)
                b = random.randint(min_val, a)
                answer = a - b
                question_text = f"What is {a} minus {b}?"
                expression = f"{a} - {b}"

            elif operation == '*':
                a = random.randint(2, 12)
                b = random.randint(2, 12)
                answer = a * b
                question_text = f"What is {a} times {b}?"
                expression = f"{a} × {b}"

            elif operation == '/':
                b = random.randint(2, 10)
                answer = random.randint(2, 10)
                a = b * answer
                question_text = f"What is {a} divided by {b}?"
                expression = f"{a} ÷ {b}"
            else:
                continue

            # Check if this question is unique
            is_duplicate = any(q['expression'] == expression for q in self.recent_questions)
            if not is_duplicate or attempt == max_attempts - 1:
                question_data = {
                    'question_text': question_text,
                    'expression': expression,
                    'answer': answer,
                    'operation': operation
                }

                # Add to recent questions
                self.recent_questions.append(question_data)
                if len(self.recent_questions) > self.max_recent_questions:
                    self.recent_questions.pop(0)

                return question_data

        # Fallback if all attempts failed
        return question_data if question_data else {
            'question_text': 'What is 1 plus 1?',
            'expression': '1 + 1',
            'answer': 2,
            'operation': '+'
        }

    def generate_question(self) -> Dict:
        """Generate a math question (uses AI by default, falls back if needed)"""
        return self.generate_ai_question()

    def _generate_correct_feedback(self, answer: float, question_text: str) -> str:
        """
        Generate AI-powered feedback for correct answers.

        Args:
            answer: The correct answer
            question_text: The question that was answered

        Returns:
            Feedback text
        """
        try:
            system_prompt = get_feedback_system_prompt()
            user_prompt = get_correct_answer_feedback_prompt(
                answer=answer,
                question_text=question_text,
                grade=self.student_profile.grade
            )

            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.9,  # High variety in responses
                max_tokens=50
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"⚠️ Feedback generation error: {e}")
            # Fallback to simple responses
            fallback_responses = [
                f"Excellent! {answer} is correct!",
                f"Perfect!",
                f"Great job!",
                f"You got it!",
                f"Amazing work!"
            ]
            return random.choice(fallback_responses)

    def _generate_wrong_feedback(self, user_answer: int, correct_answer: float,
                                 question_text: str, expression: str) -> str:
        """
        Generate AI-powered feedback for incorrect answers.

        Args:
            user_answer: Student's incorrect answer
            correct_answer: The correct answer
            question_text: The question that was answered
            expression: Mathematical expression

        Returns:
            Feedback text
        """
        try:
            system_prompt = get_feedback_system_prompt()
            user_prompt = get_wrong_answer_feedback_prompt(
                user_answer=user_answer,
                correct_answer=correct_answer,
                question_text=question_text,
                expression=expression,
                grade=self.student_profile.grade
            )

            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=100
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"⚠️ Feedback generation error: {e}")
            # Fallback to simple response
            return f"Not quite. The correct answer is {correct_answer}. Keep trying!"

    def ask_question(self, question_data: Dict):
        """
        Ask question with voice and display.

        Returns:
            True if correct, False if wrong, 'quit' to exit
        """
        print("\n" + "=" * 70)
        print(f"❓ Question #{self.stats['total_questions'] + 1}")
        print("=" * 70)

        # Show expression
        print(f"\n📝 {question_data['expression']} = ?")
        time.sleep(0.3)

        # Speak and display question
        self.speak_with_display(question_data['question_text'])

        time.sleep(0.5)

        # Get answer
        try:
            print("\n💡 Your answer: ", end="", flush=True)
            user_input = input().strip()

            # Check quit
            if user_input.lower() in ['quit', 'exit', 'q']:
                return 'quit'

            # Parse answer
            try:
                user_answer = int(user_input)
            except ValueError:
                response = "Please enter a number."
                self.speak_with_display(response)
                return False

            # Check correctness
            correct_answer = question_data['answer']

            if user_answer == correct_answer:
                # Correct! - Generate AI feedback
                time.sleep(0.3)
                response = self._generate_correct_feedback(correct_answer, question_data['question_text'])
                self.speak_with_display(response)
                return True
            else:
                # Wrong - Generate AI feedback
                time.sleep(0.3)
                response = self._generate_wrong_feedback(
                    user_answer,
                    correct_answer,
                    question_data['question_text'],
                    question_data['expression']
                )
                self.speak_with_display(response)
                return False

        except KeyboardInterrupt:
            return 'quit'
        except Exception as e:
            print(f"\n❌ Error: {e}")
            return False

    def show_stats(self):
        """Display statistics"""
        total = self.stats['total_questions']
        correct = self.stats['correct_answers']
        wrong = self.stats['wrong_answers']

        if total > 0:
            accuracy = (correct / total) * 100

            print("\n" + "=" * 70)
            print("📊 YOUR PROGRESS")
            print("=" * 70)
            print(f"   Total Questions:  {total}")
            print(f"   Correct Answers:  {correct} ✓")
            print(f"   Wrong Answers:    {wrong} ✗")
            print(f"   Accuracy:         {accuracy:.1f}%")
            print("=" * 70)

            # Speak stats
            stats_msg = f"You answered {total} questions. You got {correct} correct. That is {accuracy:.0f} percent!"
            time.sleep(0.5)
            self.speak_with_display(stats_msg)

            # Encouragement
            time.sleep(0.3)
            if accuracy >= 90:
                encouragement = "Outstanding! You are a math champion!"
            elif accuracy >= 75:
                encouragement = "Excellent work! Keep it up!"
            elif accuracy >= 60:
                encouragement = "Good job! You are improving!"
            else:
                encouragement = "Keep practicing! You will get better!"

            self.speak_with_display(encouragement)

    def run_session(self, num_questions: int = 10):
        """
        Run tutoring session.

        Args:
            num_questions: Number of questions (0 = infinite)
        """
        print("\n" + "=" * 70)
        print("🎓 AI VOICE MATH TUTOR")
        print("   Voice with Synchronized Letter-by-Letter Display")
        print("=" * 70)

        # Welcome
        welcome = "Hello! I am your AI math tutor. Let's practice math together!"
        self.speak_with_display(welcome)

        time.sleep(0.8)

        instructions = "I will speak questions. You type your answer. Type quit to exit."
        self.speak_with_display(instructions)

        print("\n📋 Instructions:")
        print("   ✅ Watch and listen as questions appear letter by letter")
        print("   ✅ Type your numeric answer")
        print("   ✅ Press Enter to submit")
        print("   ✅ Type 'quit' to exit anytime")
        print("\n" + "-" * 70)

        time.sleep(1.5)

        try:
            question_count = 0

            while True:
                # Check limit
                if num_questions > 0 and question_count >= num_questions:
                    completion = f"Congratulations! You completed all {num_questions} questions!"
                    self.speak_with_display(completion)
                    break

                # Generate question
                question_data = self.generate_question()
                self.stats['total_questions'] += 1
                question_count += 1

                # Ask question
                result = self.ask_question(question_data)

                if result == 'quit':
                    goodbye = "Thank you for practicing! See you next time!"
                    self.speak_with_display(goodbye)
                    break
                elif result:
                    self.stats['correct_answers'] += 1
                else:
                    self.stats['wrong_answers'] += 1

                time.sleep(1)

        except KeyboardInterrupt:
            print("\n\n👋 Session interrupted")
            goodbye = "Goodbye! Great job practicing!"
            self.speak_with_display(goodbye)

        finally:
            # Final stats
            if self.stats['total_questions'] > 0:
                time.sleep(0.8)
                print("\n" + "=" * 70)
                print("📊 FINAL RESULTS")
                print("=" * 70)
                self.show_stats()


def main():
    """Main function"""
    print("🚀 Starting AI Voice Math Tutor...\n")

    try:
        # Get grade level
        print("📚 Enter Grade Level (1, 2, or 3) [default: 1]: ", end="")
        try:
            grade = int(input().strip())
            if grade < 1 or grade > 3:
                print("⚠️ Invalid grade, using default: 1")
                grade = 1
        except:
            grade = 1

        # Get performance level
        print("\n📊 Choose Performance Level (1, 2, or 3) [default: 1]: ", end="")
        try:
            performance_level = int(input().strip())
            if performance_level < 1 or performance_level > 3:
                print("⚠️ Invalid performance level, using default: 1")
                performance_level = 1
        except:
            performance_level = 1

        # Get sublevel
        print("\n🎯 Choose Sublevel:")
        print("   1. Starter   - Basic foundational concepts")
        print("   2. Explorer  - Developing skills")
        print("   3. Solver    - Competent problem solving")
        print("   4. Champion  - Advanced challenges")
        print("\nEnter 1-4 [default: 1]: ", end="")
        sublevel_options = ["Starter", "Explorer", "Solver", "Champion"]
        try:
            sublevel_choice = int(input().strip())
            if sublevel_choice < 1 or sublevel_choice > 4:
                print("⚠️ Invalid sublevel, using default: Starter")
                sublevel = "Starter"
            else:
                sublevel = sublevel_options[sublevel_choice - 1]
        except:
            sublevel = "Starter"

        # Validate inputs using TutorConfig
        grade = TutorConfig.validate_grade(grade)
        performance_level = TutorConfig.validate_performance_level(performance_level)
        sublevel = TutorConfig.validate_sublevel(sublevel)

        print(f"\n✅ {TutorConfig.get_config_summary(grade, performance_level, sublevel)}")
        time.sleep(0.5)

        # Create tutor with grade, performance level, and sublevel
        tutor = AIVoiceMathTutor(grade=grade, performance_level=performance_level, sublevel=sublevel)

        # Number of questions
        print("\n📝 How many questions? [0 = infinite, default: 10]: ", end="")
        try:
            num_questions = int(input().strip())
        except:
            num_questions = 10

        print(f"✅ {num_questions if num_questions > 0 else 'Infinite'} questions")
        time.sleep(0.5)

        # Run session
        tutor.run_session(num_questions)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Install required packages:")
        print("   pip install pyttsx3 openai python-dotenv")
        print("\n💡 Set up .env file with:")
        print("   OPENAI_API_KEY=your-api-key-here")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
