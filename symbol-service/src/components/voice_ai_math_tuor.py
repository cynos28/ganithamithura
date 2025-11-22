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
import time
import subprocess
import threading
from typing import Optional, Dict
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.base_math_tutor import BaseMathTutor
from core.ai_question_generator import AIQuestionGenerator
from core.number_extractor import NumberExtractor
from config.voice_microphone_config import VoiceConfig, MicrophoneConfig

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

        # Detect the best available voice method
        self.voice_method = VoiceConfig.detect_voice_method()

        if self.voice_method == 'macos_say':
            print("✅ Using macOS 'say' command for voice")

            # Get available voices
            try:
                voices = VoiceConfig.get_available_voices()
                print(f"🔊 Found {len(voices)} macOS voices")

                # Select preferred voice
                self.selected_voice = VoiceConfig.select_preferred_voice(voices)

                if self.selected_voice:
                    print(f"✅ Selected voice: {self.selected_voice}")
                else:
                    print("✅ Using system default voice")

            except subprocess.TimeoutExpired:
                print("⚠️ Voice list retrieval timed out - using system default")
            except Exception as e:
                print(f"⚠️ Could not get voice list: {e} - using system default")
        else:
            print("📖 Using text-only mode")

    def speak(self, text: str):
        """Speak text using the best available method."""
        print(f"🔊 AI: {text}")

        if self.voice_method == 'macos_say':
            try:
                cmd = ['say']
                if self.selected_voice:
                    cmd.extend(['-v', self.selected_voice])
                cmd.extend(['-r', str(VoiceConfig.SPEECH_RATE)])
                cmd.append(text)

                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                try:
                    process.wait(timeout=VoiceConfig.SPEAK_TIMEOUT)
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

            # Select the best microphone device
            best_mic = MicrophoneConfig.select_microphone_device(mic_list)

            if best_mic is not None:
                self.microphone = sr.Microphone(device_index=best_mic)
                print(f"✅ Using: {mic_list[best_mic]}")
            else:
                self.microphone = sr.Microphone()
                print("✅ Using default microphone")

            # Configure recognizer with settings from config
            settings = MicrophoneConfig.get_recognizer_settings()
            self.recognizer.energy_threshold = settings['energy_threshold']
            self.recognizer.dynamic_energy_threshold = settings['dynamic_energy_threshold']
            self.recognizer.pause_threshold = settings['pause_threshold']

            # Calibrate microphone
            print(f"📊 Calibrating microphone (stay quiet for {MicrophoneConfig.CALIBRATION_DURATION} seconds)...")
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=MicrophoneConfig.CALIBRATION_DURATION)

            print(f"✅ Calibrated! Energy: {self.recognizer.energy_threshold:.1f}")

        except Exception as e:
            print(f"⚠️ Microphone setup error: {e}")
            self.microphone = sr.Microphone()

    def listen_for_answer(self, timeout: int = None) -> Optional[str]:
        """Listen for user's answer."""
        if timeout is None:
            timeout = MicrophoneConfig.LISTEN_TIMEOUT

        try:
            print("🎤 Listening for your answer... (speak clearly)")

            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=MicrophoneConfig.LISTEN_AMBIENT_DURATION)
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=MicrophoneConfig.PHRASE_TIME_LIMIT)

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
                thread.join(timeout=MicrophoneConfig.GOOGLE_API_TIMEOUT)

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
        """Extract number from speech using NumberExtractor."""
        return NumberExtractor.extract(speech)


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
                # Generate AI question based on student profile
                question_data = AIQuestionGenerator.generate_question(
                    self.student_profile.grade,
                    self.student_profile.level,
                    self.student_profile.sublevel
                )
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
