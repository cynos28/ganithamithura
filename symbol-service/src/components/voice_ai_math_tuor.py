#!/usr/bin/env python3
"""
Simple Voice Math Tutor with Speech Recognition.

Features:
- Speech recognition using Google API
- Text-to-speech using macOS 'say' command or text-only fallback
- Curriculum-aligned questions for Grades 1-3
- Interactive student profile setup

Inherits from BaseMathTutor for shared functionality.
"""

import speech_recognition as sr
import os
import sys
import random
import re
import time
import subprocess
import threading
from typing import Optional, Dict
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from base_math_tutor import BaseMathTutor
from curriculum_helper import CurriculumHelper
from prompts.math_question_prompts import get_question_generation_prompt

# Load environment variables
load_dotenv()


class SimpleVoiceMathTutor(BaseMathTutor):
    """Simple voice-based math tutor with speech recognition."""

    def __init__(self, grade: int, level: int, sublevel: str):
        """
        Initialize Simple Voice Math Tutor.

        Args:
            grade: 1, 2, or 3
            level: 1, 2, or 3
            sublevel: Starter, Explorer, Solver, or Champion
        """
        super().__init__(grade, level, sublevel)

        self.recognizer = sr.Recognizer()
        self.voice_method = 'text_only'
        self.selected_voice = None
        self.microphone = None

        # Setup systems
        self.setup_voice()
        self.setup_microphone()

        # Display profile
        self.display_profile()

    def setup_voice(self):
        """Setup voice system using macOS 'say' command or text-only."""
        print("🔊 Setting up voice system...")

        try:
            # Check if 'say' command exists
            result = subprocess.run(['which', 'say'],
                                  capture_output=True,
                                  timeout=2,
                                  text=True)
            if result.returncode != 0:
                raise Exception("'say' command not found")

            self.voice_method = 'macos_say'
            print("✅ Using macOS 'say' command for voice")

            # Get available voices
            try:
                result = subprocess.run(['say', '-v', '?'],
                                      capture_output=True,
                                      text=True,
                                      timeout=5)
                voices = result.stdout.strip().split('\n')
                print(f"🔊 Found {len(voices)} macOS voices")

                # Select preferred voice
                preferred_names = ['samantha', 'alex', 'allison', 'ava', 'karen', 'susan', 'victoria']
                for voice_line in voices:
                    voice_name = voice_line.split()[0] if voice_line else ""
                    if any(name in voice_name.lower() for name in preferred_names):
                        self.selected_voice = voice_name
                        print(f"✅ Selected voice: {voice_name}")
                        break

                if not self.selected_voice:
                    print("✅ Using system default voice")

            except subprocess.TimeoutExpired:
                print("⚠️ Voice list retrieval timed out - using system default")
            except Exception as e:
                print(f"⚠️ Could not get voice list: {e} - using system default")

        except Exception as e:
            print(f"⚠️ macOS 'say' not available: {e}")
            self.voice_method = 'text_only'
            print("📖 Using text-only mode")

    def speak(self, text: str):
        """Speak text using the best available method."""
        print(f"🔊 AI: {text}")

        if self.voice_method == 'macos_say':
            try:
                cmd = ['say']
                if self.selected_voice:
                    cmd.extend(['-v', self.selected_voice])
                cmd.extend(['-r', '120'])  # Slow speech rate
                cmd.append(text)

                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                try:
                    process.wait(timeout=15)
                    print("✅ Speech completed")
                except subprocess.TimeoutExpired:
                    print("⚠️ Speech timeout - moving forward")
                    process.terminate()

            except Exception as e:
                print(f"⚠️ Speech error: {e}")
                print(f"📖 PLEASE READ: {text.upper()}")
                time.sleep(1)
        else:
            # Text-only mode
            print(f"📖 PLEASE READ: {text.upper()}")
            time.sleep(1)

    def setup_microphone(self):
        """Setup microphone with optimal settings."""
        print("🎤 Setting up microphone...")

        try:
            # List available microphones
            mic_list = sr.Microphone.list_microphone_names()
            best_mic = None

            # Prefer built-in MacBook microphone
            for i, name in enumerate(mic_list):
                if "MacBook" in name and "Microphone" in name:
                    best_mic = i
                    break

            if best_mic is not None:
                self.microphone = sr.Microphone(device_index=best_mic)
                print(f"✅ Using: {mic_list[best_mic]}")
            else:
                self.microphone = sr.Microphone()
                print("✅ Using default microphone")

            # Configure recognizer
            self.recognizer.energy_threshold = 300
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.pause_threshold = 1.0

            # Calibrate microphone
            print("📊 Calibrating microphone (stay quiet for 3 seconds)...")
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=3)

            print(f"✅ Calibrated! Energy: {self.recognizer.energy_threshold:.1f}")

        except Exception as e:
            print(f"⚠️ Microphone setup error: {e}")
            self.microphone = sr.Microphone()

    def listen_for_answer(self, timeout: int = 15) -> Optional[str]:
        """Listen for user's answer."""
        try:
            print("🎤 Listening for your answer... (speak clearly)")

            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=8)

            print("🔄 Processing your speech...")

            try:
                # Add timeout to Google API call to prevent hanging
                result = [None]
                error = [None]

                def recognize():
                    try:
                        result[0] = self.recognizer.recognize_google(audio, language='en-US')
                    except Exception as e:
                        error[0] = e

                thread = threading.Thread(target=recognize, daemon=True)
                thread.start()
                thread.join(timeout=10)  # 10 second timeout for Google API

                if error[0]:
                    if isinstance(error[0], sr.UnknownValueError):
                        print("❓ Could not understand - please try again")
                    else:
                        print(f"⚠️ Recognition error: {error[0]}")
                    return None

                if result[0] is None:
                    print("⏰ Recognition took too long - please try again")
                    return None

                text = result[0]
                print(f"✅ You said: '{text}'")
                return text.strip()

            except sr.UnknownValueError:
                print("❓ Could not understand - please try again")
                return None

        except sr.WaitTimeoutError:
            print("⏰ No speech detected - please speak louder")
            return None
        except Exception as e:
            print(f"❌ Listening error: {e}")
            return None

    def extract_number(self, speech: str) -> Optional[int]:
        """Extract number from speech with phonetic matching."""
        if not speech:
            return None

        speech_lower = speech.lower().strip()
        print(f"🔍 Analyzing: '{speech_lower}'")

        # Comprehensive number mapping
        number_words = {
            'zero': 0, 'oh': 0,
            'one': 1, 'won': 1, 'wan': 1,
            'two': 2, 'to': 2, 'too': 2, 'tu': 2,
            'three': 3, 'tree': 3, 'free': 3,
            'four': 4, 'for': 4, 'fore': 4, 'floor': 4,
            'five': 5, 'hive': 5, 'dive': 5,
            'six': 6, 'sex': 6, 'sicks': 6, 'sick': 6,
            'seven': 7, 'heaven': 7,
            'eight': 8, 'ate': 8, 'weight': 8, 'gate': 8,
            'nine': 9, 'wine': 9, 'nein': 9, 'mine': 9,
            'ten': 10, 'pen': 10, 'hen': 10,
            'eleven': 11, 'twelve': 12, 'thirteen': 13,
            'fourteen': 14, 'fifteen': 15, 'sixteen': 16,
            'seventeen': 17, 'eighteen': 18, 'nineteen': 19,
            'twenty': 20, 'thirty': 30, 'forty': 40, 'fifty': 50
        }

        # Direct word match
        for word, value in number_words.items():
            if word in speech_lower:
                print(f"✅ Found '{word}' = {value}")
                return value

        # Digit search
        digit_match = re.search(r'\b(\d+)\b', speech)
        if digit_match:
            number = int(digit_match.group(1))
            print(f"✅ Found digit: {number}")
            return number

        print(f"❌ No number found in '{speech_lower}'")
        return None

    def generate_question(self) -> Dict:
        """Generate curriculum-aligned question."""
        spec = CurriculumHelper.get_spec(
            self.student_profile.grade,
            self.student_profile.level,
            self.student_profile.sublevel
        )

        if not spec:
            # Fallback to simple addition
            return {'question': '1 plus 1', 'expression': '1 + 1', 'answer': 2, 'operation': '+'}

        operations = spec.get('operations', ['addition'])
        operation = random.choice(operations)

        # Handle different operation types
        if operation == 'addition':
            return self._generate_addition(spec)
        elif operation == 'three_addend':
            return self._generate_three_addend(spec)
        elif operation == 'subtraction':
            return self._generate_subtraction(spec)
        elif operation == 'multiplication':
            return self._generate_multiplication(spec)
        elif operation == 'missing_addend':
            return self._generate_missing_addend(spec)
        else:
            # Fallback to addition
            return self._generate_addition(spec)

    def _generate_addition(self, spec: Dict) -> Dict:
        """Generate two-addend addition question."""
        operand_min = spec.get('operand_min', 0)
        operand_max = spec.get('operand_max', 10)
        result_max = spec.get('result_max', 20)

        a = random.randint(operand_min, operand_max)
        b = random.randint(operand_min, operand_max)
        while a + b > result_max:
            b = random.randint(operand_min, operand_max)

        answer = a + b
        return {
            'question': f"{a} plus {b}",
            'expression': f"{a} + {b}",
            'answer': answer,
            'operation': '+'
        }

    def _generate_three_addend(self, spec: Dict) -> Dict:
        """Generate three-addend addition question."""
        operand_min = spec.get('operand_min', 1)
        operand_max = spec.get('operand_max', 10)
        result_max = spec.get('result_max', 20)

        a = random.randint(operand_min, operand_max)
        b = random.randint(operand_min, operand_max)
        c = random.randint(operand_min, operand_max)
        while a + b + c > result_max:
            c = random.randint(operand_min, operand_max)

        answer = a + b + c
        return {
            'question': f"{a} plus {b} plus {c}",
            'expression': f"{a} + {b} + {c}",
            'answer': answer,
            'operation': '+'
        }

    def _generate_subtraction(self, spec: Dict) -> Dict:
        """Generate subtraction question."""
        operand_max = spec.get('operand_max', 20)
        result_max = spec.get('result_max', 20)

        b = random.randint(0, min(operand_max // 2, 10))
        a = random.randint(b, operand_max)
        while a - b > result_max:
            a = random.randint(b, operand_max)

        answer = a - b
        return {
            'question': f"{a} minus {b}",
            'expression': f"{a} - {b}",
            'answer': answer,
            'operation': '-'
        }

    def _generate_multiplication(self, spec: Dict) -> Dict:
        """Generate multiplication question."""
        factors_min = spec.get('factors_min', 2)
        factors_max = spec.get('factors_max', 10)
        product_max = spec.get('product_max', 100)

        a = random.randint(factors_min, factors_max)
        b = random.randint(factors_min, factors_max)
        while a * b > product_max:
            b = random.randint(factors_min, factors_max)

        answer = a * b
        return {
            'question': f"{a} times {b}",
            'expression': f"{a} × {b}",
            'answer': answer,
            'operation': '×'
        }

    def _generate_missing_addend(self, spec: Dict) -> Dict:
        """Generate missing addend question (□ + a = b)."""
        operand_min = spec.get('operand_min', 0)
        operand_max = spec.get('operand_max', 10)
        result_max = spec.get('result_max', 20)

        b = random.randint(5, result_max)
        a = random.randint(operand_min, min(operand_max, b))
        unknown = b - a

        return {
            'question': f"blank plus {a} equals {b}",
            'expression': f"□ + {a} = {b}",
            'answer': unknown,
            'operation': 'missing_addend'
        }

    def ask_question(self, question_data: Dict) -> bool:
        """Ask a question and get the answer."""
        max_attempts = 3

        for attempt in range(max_attempts):
            if attempt == 0:
                question_text = f"What is {question_data['question']}?"
                print(f"\n❓ Question #{self.stats['total_questions']}: {question_text}")
                print(f"   📝 {question_data['expression']} = ?")
                self.speak(question_text)
            else:
                retry_text = f"Try again. What is {question_data['question']}?"
                print(f"\n🔄 Attempt {attempt + 1}: {retry_text}")
                self.speak(retry_text)

            user_speech = self.listen_for_answer()

            if user_speech is None:
                if attempt < max_attempts - 1:
                    self.speak("I didn't hear you. Let me ask again.")
                    continue
                else:
                    correct_msg = f"The answer is {question_data['answer']}."
                    self.speak(correct_msg)
                    return False

            # Check for quit
            if any(word in user_speech.lower() for word in ['quit', 'exit', 'stop']):
                return "quit"

            user_answer = self.extract_number(user_speech)
            correct_answer = question_data['answer']

            if user_answer is None:
                if attempt < max_attempts - 1:
                    self.speak("Please say just the number.")
                    continue
                else:
                    self.speak(f"The answer is {correct_answer}. Let's try another question.")
                    return False

            # Check if correct
            if user_answer == correct_answer:
                responses = [
                    f"Excellent! {correct_answer} is correct!",
                    f"Perfect! The answer is {correct_answer}!",
                    f"Great job! {correct_answer} is right!",
                    f"Well done! {correct_answer} is the answer!"
                ]
                self.speak(random.choice(responses))
                return True
            else:
                if attempt < max_attempts - 1:
                    self.speak(f"Not quite. You said {user_answer}. Try again.")
                else:
                    self.speak(f"The correct answer is {correct_answer}. You said {user_answer}.")
                    return False

        return False

    def run_session(self):
        """Main tutoring session."""
        print("\n" + "="*60)
        print("🎓 SIMPLE VOICE MATH TUTOR")
        print("   Curriculum-Based • Speech Recognition")
        print("="*60)

        self.speak("Hello! I'm your math tutor.")
        self.speak("I'll ask simple math questions. Say just the number answer.")

        time.sleep(2)

        try:
            while True:
                question_data = self.generate_question()
                self.stats['total_questions'] += 1

                result = self.ask_question(question_data)

                if result == "quit":
                    self.speak("Goodbye! Great job practicing math!")
                    break
                elif result:
                    self.stats['correct_answers'] += 1
                else:
                    self.stats['wrong_answers'] += 1

                # Show progress every 5 questions
                if self.stats['total_questions'] % 5 == 0:
                    self.show_stats()

                time.sleep(1)

        except KeyboardInterrupt:
            print("\n👋 Session ended by user")
            self.speak("Goodbye!")

        finally:
            if self.stats['total_questions'] > 0:
                print("\n" + "="*50)
                print("📊 FINAL RESULTS")
                print("="*50)
                self.show_stats()


def main():
    """Main function - Start tutor with interactive profile."""
    print("\n🚀 Starting Curriculum-Based Voice Math Tutor...\n")

    try:
        # Get student profile interactively
        grade, level, sublevel = BaseMathTutor.get_student_profile_interactive()

        print(f"\n🔄 Initializing tutor for Grade {grade}, Level {level}, {sublevel}...\n")

        # Create and run tutor
        tutor = SimpleVoiceMathTutor(grade, level, sublevel)
        tutor.run_session()

    except KeyboardInterrupt:
        print("\n👋 Setup cancelled by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Ensure: pip install speechrecognition python-dotenv pyaudio")


if __name__ == "__main__":
    main()
