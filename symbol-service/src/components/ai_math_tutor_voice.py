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
from typing import Dict, Optional


class AIVoiceMathTutor:
    """AI Math Tutor with voice output and synchronized text display"""

    def __init__(self):
        """Initialize the AI Voice Math Tutor"""
        print("🚀 Initializing AI Voice Math Tutor...")

        # Initialize text-to-speech engine
        self.engine = pyttsx3.init()
        self.setup_voice()

        # Statistics
        self.stats = {
            'total_questions': 0,
            'correct_answers': 0,
            'wrong_answers': 0
        }

        # Difficulty levels
        self.difficulty_levels = {
            'easy': {'range': (1, 10), 'operations': ['+', '-']},
            'medium': {'range': (1, 20), 'operations': ['+', '-', '*']},
            'hard': {'range': (1, 50), 'operations': ['+', '-', '*', '/']}
        }
        self.current_difficulty = 'easy'

        print("✅ AI Voice Math Tutor ready!\n")

    def setup_voice(self):
        """Setup text-to-speech voice"""
        try:
            voices = self.engine.getProperty('voices')

            # Try to find a good voice
            selected_voice = None
            for voice in voices:
                if any(name in voice.name.lower() for name in ['samantha', 'alex', 'victoria', 'karen']):
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
        import subprocess
        import platform

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

    def generate_question(self) -> Dict:
        """Generate a math question"""
        config = self.difficulty_levels[self.current_difficulty]
        min_val, max_val = config['range']
        operations = config['operations']

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

        return {
            'question_text': question_text,
            'expression': expression,
            'answer': answer,
            'operation': operation
        }

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
                # Correct!
                responses = [
                    f"Excellent! {correct_answer} is correct!",
                    f"Perfect! The answer is {correct_answer}!",
                    f"Great job! {correct_answer} is right!",
                    f"Well done! The answer is {correct_answer}!",
                    f"Amazing! You got it! The answer is {correct_answer}!"
                ]
                response = random.choice(responses)
                time.sleep(0.3)
                self.speak_with_display(response)
                return True
            else:
                # Wrong
                response = f"Not quite. You answered {user_answer}. The correct answer is {correct_answer}."
                time.sleep(0.3)
                self.speak_with_display(response)

                # Give hint
                hint = self.generate_hint(question_data)
                if hint:
                    time.sleep(0.5)
                    self.speak_with_display(hint)

                return False

        except KeyboardInterrupt:
            return 'quit'
        except Exception as e:
            print(f"\n❌ Error: {e}")
            return False

    def generate_hint(self, question_data: Dict) -> Optional[str]:
        """Generate helpful hint"""
        operation = question_data['operation']
        answer = question_data['answer']

        hints = {
            '+': f"Remember, addition combines numbers. The answer is {answer}.",
            '-': f"Subtraction means taking away. The answer is {answer}.",
            '*': f"Multiplication is repeated addition. The answer is {answer}.",
            '/': f"Division splits into equal parts. The answer is {answer}."
        }

        return hints.get(operation)

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

                # Show progress every 5 questions
                if self.stats['total_questions'] % 5 == 0:
                    time.sleep(0.8)
                    self.show_stats()

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
        # Create tutor
        tutor = AIVoiceMathTutor()

        # Choose difficulty
        print("\n📊 Choose difficulty:")
        print("   1. Easy   (1-10, + and -)")
        print("   2. Medium (1-20, +, -, ×)")
        print("   3. Hard   (1-50, +, -, ×, ÷)")

        choice = input("\nEnter 1, 2, or 3 [default: 1]: ").strip()

        if choice == '2':
            tutor.current_difficulty = 'medium'
            print("✅ Difficulty: Medium")
        elif choice == '3':
            tutor.current_difficulty = 'hard'
            print("✅ Difficulty: Hard")
        else:
            tutor.current_difficulty = 'easy'
            print("✅ Difficulty: Easy")

        time.sleep(0.5)

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
        print("\n💡 Install required package:")
        print("   pip install pyttsx3")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
