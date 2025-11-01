#!/usr/bin/env python3
"""
Simple Voice Math Tutor (TTS-Free Version)
Focus on excellent speech recognition and math learning
Alternative: Uses system 'say' command for macOS or text-only mode
"""

import speech_recognition as sr
import openai
import os
import sys
import json
import random
import re
import time
import subprocess
from typing import Optional, Dict, List, Tuple
from dotenv import load_dotenv
from difflib import SequenceMatcher
import unicodedata
import string

# Load environment variables
load_dotenv()

class ImprovedNumberDetector:
    """Ultra-comprehensive number detection - catches ALL variations"""

    def __init__(self):
        """Initialize with all possible number word variations"""
        # EXHAUSTIVE mapping of every possible way to say each number
        self.all_number_variations = {
            # 0
            0: ['zero', 'oh', 'o', 'zero', 'ziro', 'zeros'],
            # 1
            1: ['one', 'won', 'wan', 'wun', 'uh', 'un', 'awn'],
            # 2
            2: ['two', 'to', 'too', 'tu', 'tew', 'tuh', 'toe', 'twu'],
            # 3
            3: ['three', 'tree', 'free', 'tre', 'thre', 'fri', 'thee'],
            # 4
            4: ['four', 'for', 'fo', 'faw', 'fir', 'fore', 'foe', 'foor'],
            # 5
            5: ['five', 'hive', 'dive', 'fiv', 'faiv', 'hiv', 'fyve', 'fibe'],
            # 6
            6: ['six', 'sex', 'sicks', 'sik', 'siks', 'sics', 'sikz', 'sickz'],
            # 7
            7: ['seven', 'sev', 'sevin', 'sevn', 'seben', 'sevven'],
            # 8
            8: ['eight', 'ate', 'ait', 'eyt', 'ayt', 'ight', 'eighty', 'eiht', 'ate', 'et'],
            # 9
            9: ['nine', 'wine', 'mine', 'nain', 'nin', 'nuy', 'nain', 'nayn', 'nyne'],
            # 10
            10: ['ten', 'pen', 'hen', 'tin', 'tun', 'tenn', 'tan'],
            # 11-19
            11: ['eleven', 'leven', 'levun'],
            12: ['twelve', 'twelv', 'twelf'],
            13: ['thirteen', 'therteen', 'thirteen'],
            14: ['fourteen', 'forteen'],
            15: ['fifteen', 'fiveteen'],
            16: ['sixteen', 'sixteen'],
            17: ['seventeen', 'seventeen'],
            18: ['eighteen', 'eighteen', 'eightteen'],
            19: ['nineteen', 'nineeen'],
            # 20, 30, 40, 50, 60, 70, 80, 90
            20: ['twenty', 'tweny', 'twenty'],
            30: ['thirty', 'thurty', 'dirty'],
            40: ['forty', 'fourty', 'forti'],
            50: ['fifty', 'fity', 'fifty'],
            60: ['sixty', 'sixy'],
            70: ['seventy', 'sevnty'],
            80: ['eighty', 'ighty', 'eightty'],
            90: ['ninety', 'nety', 'ninity'],
        }

    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        text = text.lower().strip()
        text = re.sub(r'\s+', ' ', text)
        text = text.translate(str.maketrans('', '', string.punctuation))
        return text

    def extract_digits(self, speech: str) -> Optional[int]:
        """Extract explicit digits from speech"""
        match = re.search(r'\b(\d+)\b', speech)
        if match:
            return int(match.group(1))
        return None

    def similarity_ratio(self, s1: str, s2: str) -> float:
        """Calculate similarity between two strings"""
        return SequenceMatcher(None, s1, s2).ratio()

    def debug_find_numbers(self, speech: str) -> List[Dict]:
        """Debug helper - show all detected numbers and their methods"""
        if not speech:
            return []

        speech_clean = self.clean_text(speech)
        results = []

        # Check explicit digits
        digit = self.extract_digits(speech)
        if digit is not None:
            results.append({'number': digit, 'method': 'explicit_digit', 'confidence': 1.0})

        # Check exact word matches
        speech_words = speech_clean.split()
        for word in speech_words:
            for number, variations in self.all_number_variations.items():
                if word in variations:
                    results.append({'number': number, 'method': 'exact_word', 'match': word, 'confidence': 1.0})

        return results

    def detect_with_confidence(self, speech: str, expected_range: Optional[Tuple[int, int]] = None) -> Dict:
        """
        Comprehensive number detection that catches ALL variations

        Detection methods (in order of priority):
        1. Explicit digits (8 → 8)
        2. Exact word match (eight → 8, ate → 8)
        3. Substring match (contains "eight")
        4. Fuzzy match (phonetically similar)
        5. Character similarity (highest match)
        """
        if not speech:
            return {'number': None, 'confidence': 0.0, 'method': 'none', 'is_valid': False}

        speech_clean = self.clean_text(speech)
        candidates = []

        # METHOD 1: Extract explicit digits first (highest priority)
        digit = self.extract_digits(speech)
        if digit is not None:
            candidates.append((digit, 1.0, 'explicit_digit'))

        # METHOD 2: Exact word matching - check each word
        speech_words = speech_clean.split()
        for word in speech_words:
            for number, variations in self.all_number_variations.items():
                if word in variations:
                    candidates.append((number, 1.0, 'exact_word'))

        # METHOD 3: Substring matching - word contains number word
        for word in speech_words:
            for number, variations in self.all_number_variations.items():
                for variation in variations:
                    if len(variation) >= 3 and variation in word:
                        candidates.append((number, 0.95, 'substring'))
                    elif variation in word and len(variation) >= 2:
                        candidates.append((number, 0.90, 'substring'))

        # METHOD 4: Fuzzy matching - similar sounding words
        for word in speech_words:
            for number, variations in self.all_number_variations.items():
                for variation in variations:
                    similarity = self.similarity_ratio(word, variation)
                    # Accept matches above 65% similarity
                    if similarity >= 0.65:
                        confidence = min(0.95, similarity * 0.95)
                        candidates.append((number, confidence, 'fuzzy_match'))

        # METHOD 5: Character-level matching as last resort
        # For very short or distorted speech, match by character overlap
        for word in speech_words:
            if len(word) >= 2:
                for number, variations in self.all_number_variations.items():
                    for variation in variations:
                        if len(variation) >= 2:
                            # Calculate character overlap
                            overlap = sum(1 for c in word if c in variation)
                            if overlap >= len(word) / 2:  # At least 50% char overlap
                                confidence = (overlap / max(len(word), len(variation))) * 0.85
                                candidates.append((number, confidence, 'char_overlap'))

        if not candidates:
            return {'number': None, 'confidence': 0.0, 'method': 'none', 'is_valid': False}

        # Deduplicate: keep the highest confidence score for each number
        best_candidates = {}
        for number, confidence, method in candidates:
            key = number
            if key not in best_candidates or confidence > best_candidates[key][1]:
                best_candidates[key] = (number, confidence, method)

        candidates = list(best_candidates.values())

        # Filter by expected range if provided
        if expected_range:
            min_val, max_val = expected_range
            range_candidates = [c for c in candidates if min_val <= c[0] <= max_val]
            if range_candidates:
                candidates = range_candidates

        # Sort by confidence (highest first)
        candidates.sort(key=lambda x: x[1], reverse=True)

        if not candidates:
            return {'number': None, 'confidence': 0.0, 'method': 'none', 'is_valid': False}

        number, confidence, method = candidates[0]

        # Check if valid range
        is_valid = True
        if expected_range:
            min_val, max_val = expected_range
            is_valid = min_val <= number <= max_val

        return {
            'number': number,
            'confidence': confidence,
            'method': method,
            'is_valid': is_valid,
            'alternatives': [{'number': c[0], 'confidence': c[1], 'method': c[2]} for c in candidates[1:4]]
        }


class SimpleVoiceMathTutor:
    def __init__(self, openai_api_key: str):
        """Initialize the Simple Voice Math Tutor"""
        self.openai_client = openai.OpenAI(api_key=openai_api_key)
        self.recognizer = sr.Recognizer()

        # Initialize improved number detector
        self.number_detector = ImprovedNumberDetector()

        # Check for system TTS alternatives
        self.setup_voice_system()

        # Setup microphone
        self.setup_microphone()
        
        # Statistics
        self.stats = {
            'total_questions': 0,
            'correct_answers': 0,
            'wrong_answers': 0,
            'questions_history': []
        }
        
        # Simple difficulty
        self.difficulty_levels = {
            'easy': {'range': (0, 5), 'operations': ['+', '-']},
            'medium': {'range': (0, 10), 'operations': ['+', '-']},
            'hard': {'range': (0, 15), 'operations': ['+', '-', '*']}
        }
        self.current_difficulty = 'easy'
        self.current_question = None
    
    def setup_voice_system(self):
        """Setup voice system using macOS 'say' command or text-only"""
        print("🔊 Setting up voice system...")
        
        # Try macOS 'say' command (much more reliable)
        try:
            # Test if 'say' command works
            result = subprocess.run(['say', 'test'], 
                                  capture_output=True, 
                                  timeout=3, 
                                  check=True)
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
                
                # Look for female voices
                self.selected_voice = None
                for voice_line in voices:
                    voice_name = voice_line.split()[0] if voice_line else ""
                    if any(name in voice_name.lower() for name in ['samantha', 'alex', 'allison', 'ava', 'karen', 'susan', 'victoria']):
                        self.selected_voice = voice_name
                        print(f"✅ Selected female voice: {voice_name}")
                        break
                
                if not self.selected_voice:
                    # Default to Samantha if available, otherwise use system default
                    if any('samantha' in voice.lower() for voice in voices):
                        self.selected_voice = 'Samantha'
                    print(f"✅ Using voice: {self.selected_voice or 'system default'}")
                        
            except Exception as e:
                print(f"⚠️ Could not get voice list: {e}")
                self.selected_voice = 'Samantha'  # Default
                
        except Exception as e:
            print(f"⚠️ macOS 'say' command not available: {e}")
            self.voice_method = 'text_only'
            print("📖 Using text-only mode")
    
    def speak(self, text: str):
        """Speak text using the best available method"""
        print(f"🔊 AI: {text}")
        
        if self.voice_method == 'macos_say':
            try:
                # Use macOS 'say' command with slower speech
                cmd = ['say']
                if self.selected_voice:
                    cmd.extend(['-v', self.selected_voice])
                cmd.extend(['-r', '120'])  # Slow speech rate
                cmd.append(text)
                
                # Run the say command
                subprocess.run(cmd, timeout=10, check=True)
                print("✅ Speech completed")
                
            except subprocess.TimeoutExpired:
                print("⚠️ Speech timeout")
            except Exception as e:
                print(f"⚠️ Speech error: {e}")
        
        elif self.voice_method == 'text_only':
            # Text-only mode with emphasis
            print(f"📖 PLEASE READ: {text.upper()}")
            time.sleep(2)  # Give time to read
    
    def setup_microphone(self):
        """Setup microphone with optimal settings"""
        print("🎤 Setting up microphone...")
        
        try:
            # List microphones
            mic_list = sr.Microphone.list_microphone_names()
            print("Available microphones:")
            for index, name in enumerate(mic_list):
                print(f"  {index}: {name}")
            
            # Smart selection: prefer MacBook Air Microphone
            best_mic = None
            for i, name in enumerate(mic_list):
                if "MacBook Air Microphone" in name:
                    best_mic = i
                    break
                elif "MacBook" in name and "Microphone" in name:
                    best_mic = i
            
            if best_mic is not None:
                self.microphone = sr.Microphone(device_index=best_mic)
                print(f"✅ Using: {mic_list[best_mic]}")
            else:
                self.microphone = sr.Microphone()
                print("✅ Using default microphone")
            
            # MAXIMUM SENSITIVITY for single number detection
            # These settings are optimized for detecting SHORT utterances like "one", "two", etc.
            self.recognizer.energy_threshold = 4000  # VERY HIGH = catches even quiet speech
            self.recognizer.dynamic_energy_threshold = False  # DISABLE dynamic - use fixed threshold
            self.recognizer.pause_threshold = 0.3  # Very short pause threshold
            self.recognizer.phrase_threshold = 0.1  # Accept very small phrases
            self.recognizer.non_speaking_duration = 0.2  # Stop listening after 0.2s silence
            
            # Calibrate
            print("📊 Calibrating microphone (stay quiet for 3 seconds)...")
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=3)
            
            print(f"✅ Calibrated! Energy: {self.recognizer.energy_threshold:.1f}")
            
        except Exception as e:
            print(f"⚠️ Microphone setup error: {e}")
            self.microphone = sr.Microphone()
    
    def listen_for_answer(self, timeout: int = 15) -> Optional[str]:
        """
        Listen for user's answer with MAXIMUM SENSITIVITY for short number utterances
        Optimized specifically for detecting single words like "one", "two", etc.
        """
        try:
            print("🎤 Listening for your answer... (speak clearly)")
            print("💡 Say just ONE number word (like 'one', 'two', 'eight', 'five')")

            with self.microphone as source:
                # Minimal ambient noise adjustment for short utterances
                print("   📊 Preparing microphone...")
                # Very short adjustment to avoid cutting off quiet speech
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)

                # OPTIMIZED for SHORT utterances
                print("   🎙️ Ready - say your number now...\n")

                # Listen parameters optimized for SHORT SPEECH:
                # - timeout: max 15 seconds to START speaking
                # - phrase_time_limit: only 3 seconds to complete the utterance
                #   (numbers are short, so 3 seconds is plenty)
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,           # 15 seconds to start
                    phrase_time_limit=3        # Only need 3 seconds for a number word
                )

            print("🔄 Processing your speech...\n")

            # STRATEGY 1: Primary Google Recognition (en-US)
            try:
                text = self.recognizer.recognize_google(audio, language='en-US')
                print(f"✅ Detected: '{text}'")
                return text.strip()
            except sr.UnknownValueError:
                print("   ⚠️ Strategy 1 (en-US) failed, trying alternatives...")
            except sr.RequestError as e:
                print(f"⚠️ API error: {e}")
                return None

            # STRATEGY 2: Google Recognition with alternatives (en-US)
            try:
                result = self.recognizer.recognize_google(audio, language='en-US', show_all=True)
                if result and len(result) > 0:
                    for alt in result:
                        if 'transcript' in alt:
                            text = alt['transcript'].strip()
                            print(f"✅ Detected (alt): '{text}'")
                            return text
            except:
                print("   ⚠️ Strategy 2 (en-US + alternatives) failed...")

            # STRATEGY 3: Try with different language hint (en-IN - India English)
            # Sometimes works better for different accents
            try:
                text = self.recognizer.recognize_google(audio, language='en-IN')
                print(f"✅ Detected (en-IN): '{text}'")
                return text.strip()
            except:
                print("   ⚠️ Strategy 3 (en-IN) failed...")

            # STRATEGY 4: Try with en-GB (British English)
            try:
                text = self.recognizer.recognize_google(audio, language='en-GB')
                print(f"✅ Detected (en-GB): '{text}'")
                return text.strip()
            except:
                print("   ⚠️ Strategy 4 (en-GB) failed...")

            # STRATEGY 5: Get all alternatives from en-US with show_all and pick the shortest
            # (numbers are usually short words)
            try:
                result = self.recognizer.recognize_google(audio, language='en-US', show_all=True)
                if result and len(result) > 0:
                    # Sort by length - numbers are usually short
                    sorted_alts = sorted(
                        [alt.get('transcript', '').strip() for alt in result if 'transcript' in alt],
                        key=len
                    )
                    if sorted_alts and sorted_alts[0]:
                        text = sorted_alts[0]
                        print(f"✅ Detected (shortest alt): '{text}'")
                        return text
            except:
                pass

            print("❌ Could not detect speech - please speak louder and clearer")
            return None

        except sr.WaitTimeoutError:
            print("⏰ No speech detected - please speak louder and clearer")
            return None
        except sr.RequestError as e:
            print(f"❌ Network/API error: {e}")
            return None
        except Exception as e:
            print(f"❌ Listening error: {e}")
            return None
    
    def extract_number(self, speech: str, expected_range: Optional[Tuple[int, int]] = None) -> Optional[int]:
        """
        Extract number from speech using improved detector with context awareness

        Args:
            speech: The recognized speech text
            expected_range: Optional (min, max) range for the expected answer

        Returns:
            Detected number or None
        """
        if not speech:
            return None

        # DEBUG: Show what we received from speech recognition
        print(f"🔍 Speech received: '{speech}'")

        # DEBUG: Show what the detector found
        debug_matches = self.number_detector.debug_find_numbers(speech)
        if debug_matches:
            print(f"   📋 Debug matches found: {debug_matches}")
        else:
            print(f"   📋 Debug: No exact matches found")

        # Use the improved detector with optional context
        result = self.number_detector.detect_with_confidence(speech, expected_range)
        number = result['number']
        confidence = result['confidence']
        method = result['method']
        is_valid = result['is_valid']

        if number is not None:
            confidence_pct = int(confidence * 100)
            status = "✅" if confidence >= 0.75 else "⚠️"
            range_status = f"(in range)" if is_valid else f"(out of range!)"
            print(f"{status} Found: {number} | Confidence: {confidence_pct}% | Method: {method} {range_status}")

            # Show alternatives if confidence is low
            if confidence < 0.75 and result.get('alternatives'):
                alternatives_str = ', '.join(f"{a['number']}({int(a['confidence']*100)}%)" for a in result['alternatives'][:2])
                print(f"   📋 Alternatives: {alternatives_str}")

            return number
        else:
            print(f"❌ No number detected in '{speech.lower().strip()}'")
            print(f"   📋 Debug: Speech length={len(speech)}, cleaned='{self.number_detector.clean_text(speech)}'")
            return None
    
    def generate_question(self) -> Dict:
        """Generate a simple math question"""
        config = self.difficulty_levels[self.current_difficulty]
        min_val, max_val = config['range']
        operations = config['operations']
        
        operation = random.choice(operations)
        
        if operation == '+':
            a = random.randint(min_val, max_val)
            b = random.randint(min_val, max_val)
            # Keep answers reasonable
            if a + b > 12:
                a, b = random.randint(0, 3), random.randint(0, 3)
            answer = a + b
            question = f"{a} plus {b}"
            expression = f"{a} + {b}"
            
        elif operation == '-':
            b = random.randint(min_val, max_val)
            a = random.randint(b, max_val + 3)
            answer = a - b
            question = f"{a} minus {b}"
            expression = f"{a} - {b}"
            
        elif operation == '*':
            a = random.randint(1, 5)
            b = random.randint(1, 5)
            answer = a * b
            question = f"{a} times {b}"
            expression = f"{a} × {b}"
        
        return {
            'question': question,
            'expression': expression,
            'answer': answer,
            'operation': operation
        }
    
    def ask_question(self, question_data: Dict) -> bool:
        """Ask a question and get the answer"""
        self.current_question = question_data
        max_attempts = 3
        
        for attempt in range(max_attempts):
            # Ask the question
            if attempt == 0:
                question_text = f"What is {question_data['question']}?"
                print(f"\n❓ Question #{self.stats['total_questions']}: {question_text}")
                print(f"   📝 {question_data['expression']} = ?")
                self.speak(question_text)
            else:
                retry_text = f"Try again. What is {question_data['question']}?"
                print(f"\n🔄 Attempt {attempt + 1}: {retry_text}")
                self.speak(retry_text)
            
            # Listen for answer
            user_speech = self.listen_for_answer()
            
            if user_speech is None:
                if attempt < max_attempts - 1:
                    self.speak("I didn't hear you. Let me ask again.")
                    continue
                else:
                    # Give the answer
                    correct_msg = f"The answer is {question_data['answer']}."
                    self.speak(correct_msg)
                    return False
            
            # Check for quit
            if any(word in user_speech.lower() for word in ['quit', 'exit', 'stop']):
                return "quit"
            
            # Extract the number with context awareness (expected range)
            # Add some buffer to the expected answer range for flexibility
            correct_answer = question_data['answer']
            min_expected = max(0, correct_answer - 10)  # Allow some tolerance
            max_expected = correct_answer + 10
            user_answer = self.extract_number(user_speech, expected_range=(min_expected, max_expected))
            
            if user_answer is None:
                if attempt < max_attempts - 1:
                    self.speak("Please say just the number. For example, say 'five' or 'three'.")
                    continue
                else:
                    self.speak(f"The answer is {correct_answer}. Let's try another question.")
                    return False
            
            # Check if correct
            if user_answer == correct_answer:
                # Correct!
                responses = [
                    f"Excellent! {correct_answer} is correct!",
                    f"Perfect! The answer is {correct_answer}!",
                    f"Great job! {correct_answer} is right!",
                    f"Well done! {correct_answer} is the answer!"
                ]
                self.speak(random.choice(responses))
                return True
            else:
                # Wrong answer
                if attempt < max_attempts - 1:
                    self.speak(f"Not quite. You said {user_answer}. Try again.")
                else:
                    self.speak(f"The correct answer is {correct_answer}. You said {user_answer}.")
                    return False
        
        return False
    
    def show_stats(self):
        """Show statistics"""
        total = self.stats['total_questions']
        correct = self.stats['correct_answers']
        wrong = self.stats['wrong_answers']
        
        if total > 0:
            accuracy = (correct / total) * 100
            print(f"\n📊 Your Progress:")
            print(f"   Questions: {total}")
            print(f"   Correct: {correct}")
            print(f"   Wrong: {wrong}")
            print(f"   Accuracy: {accuracy:.1f}%")
            
            stats_msg = f"You got {correct} out of {total} questions correct. That's {accuracy:.0f} percent!"
            self.speak(stats_msg)
    
    def run_session(self):
        """Main tutoring session"""
        print("\n" + "="*60)
        print("🎓 SIMPLE VOICE MATH TUTOR")
        print("   Reliable Speech Recognition • Simple Questions")
        print("="*60)

        print("\n📋 Instructions:")
        print("   ✅ Listen to the question")
        print("   ✅ Say just the number (like 'three' or 'seven')")
        print("   ✅ Speak clearly and close to microphone")
        print("   ✅ Say 'quit' to exit anytime")
        print("-" * 60)

        # Skip welcome messages - go straight to questions
        print("\n🚀 Starting questions...\n")
        
        try:
            while True:
                # Generate question
                question_data = self.generate_question()
                self.stats['total_questions'] += 1
                
                # Ask the question
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
                
                # Pause between questions
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
    """Main function"""
    # Check API key
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY not found!")
        print("Create .env file with: OPENAI_API_KEY=your-key")
        sys.exit(1)
    
    print("🚀 Starting Simple Voice Math Tutor...")
    
    try:
        tutor = SimpleVoiceMathTutor(api_key)
        tutor.run_session()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Install: pip install openai speechrecognition python-dotenv pyaudio")

if __name__ == "__main__":
    main()