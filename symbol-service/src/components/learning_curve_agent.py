import os
import sys
import time
import json
import re
import subprocess
import platform
from openai import OpenAI
from typing import Dict, List, Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from components.core.base_math_tutor import BaseMathTutor
from components.voice_ai_math_tuor import SimpleVoiceMathTutor
from components.core.ai_question_generator import AIQuestionGenerator
from components.core.curriculum_helper import CurriculumHelper
from prompts.learning_curve_prompts import get_lesson_prompt, get_agent_decision_prompt, get_explanation_prompt
from prompts.react_prompts import get_react_prompt

class LearningCurveAgent(SimpleVoiceMathTutor):
    """
    Adaptive Learning Agent that manages a 5-10 minute session.
    Uses real voice and image generation for a rich teaching experience.
    """
    
    def __init__(self, grade: int, level: int, sublevel: str, duration_minutes: int = 5):
        # Initialize voice tutor parent (will setup voice/mic)
        super().__init__(grade, level, sublevel)
        
        self.duration_seconds = duration_minutes * 60
        self.start_time = None
        self.session_history = []
        try:
            self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        except Exception:
            self.client = None
            print("Warning: OpenAI API Key not found. Agent will run in fallback mode.")
        self.current_streak = 0
        
    # setup_voice is inherited from SimpleVoiceMathTutor

    def speak(self, text: str):
        """
        Speak text while displaying letter-by-letter synchronized with speech.
        """
        print("\n🔊 ", end="", flush=True)

        # Check if we're on macOS to use 'say' command (more reliable)
        if platform.system() == 'Darwin':
            try:
                # Calculate char delay for sync
                # Speech rate 140 WPM = ~2.3 words/sec, ~5 chars/word = ~11.5 chars/sec
                char_delay = 0.087  # ~11.5 chars per second

                # Strip emojis for speech (keep text clean for audio)
                # Regex to remove common emojis and symbols in the supplementary plane
                speech_text = re.sub(r'[^\w\s,.?!]', '', text) 

                # Start speech in background using macOS 'say' command
                speech_process = subprocess.Popen(
                    ['say', '-r', '140', speech_text],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )

                # Small delay for speech to start
                time.sleep(0.1)

                # Display text letter by letter
                for char in text:
                    print(char, end="", flush=True)
                    # Adjust delay for punctuation to make it feel more natural
                    if char in [',', '.', '!', '?']:
                        time.sleep(char_delay * 2)
                    else:
                        time.sleep(char_delay)

                # Wait for speech to complete
                speech_process.wait(timeout=15)

            except Exception as e:
                # Fallback to simple print if voice fails
                print(text)
        else:
            # Fallback for non-macOS
            print(text)
        
        print() # New line

    def run_session(self):
        """
        Run the interactive learning session using ReAct (Reason+Act) Loop.
        """
        print(f"\n📚 Student Profile: Grade {self.student_profile.grade}, Level {self.student_profile.level} - {self.student_profile.sublevel}")
        print(f"Starting Learning Curve Session ({self.duration_seconds/60:.1f} mins)")
        
        self.start_time = time.time()
        
        # Initial Greeting
        greeting = f"Hello! Let's practice some math together for about {int(self.duration_seconds/60)} minutes. Are you ready?"
        self.speak(greeting)
        
        # ReAct Loop
        while self.get_time_remaining() > 0:
            try:
                # 1. Plan (Reasoning)
                prompt = get_react_prompt(
                    self.student_profile.grade,
                    self.student_profile.level,
                    self.student_profile.sublevel,
                    json.dumps(self.session_history[-5:]),
                    int(self.get_time_remaining())
                )
                
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3, # Lower temperature for strict reasoning
                    stop=["Observation:"]
                )
                
                llm_output = response.choices[0].message.content.strip()
                
                # 2. Parse Thought and Action
                thought_match = re.search(r"Thought:\s*(.*?)(?=\nAction:|$)", llm_output, re.DOTALL)
                action_match = re.search(r"Action:\s*(.*?)(?=\nAction Input:|$)", llm_output, re.DOTALL)
                input_match = re.search(r"Action Input:\s*(.*)", llm_output, re.DOTALL)
                
                thought = thought_match.group(1).strip() if thought_match else "Deciding next step..."
                action = action_match.group(1).strip() if action_match else "TEACH_LESSON"
                action_input = input_match.group(1).strip() if input_match else ""
                
                # Display Reasoning (Agentic view)
                print(f"\n🧠 AGENT THOUGHT: {thought}")
                print(f"⚡ ACTION: {action} ({action_input})")
                
                # 3. Execute Action
                if action == "TEACH_LESSON":
                    self.teach_concept(action_input)
                    
                    # Auto-chain confirmation for natural flow
                    confirmed = self.ask_confirmation()
                    if confirmed:
                        self.record_interaction("check_understanding", "User confirmed Yes", True)
                    else:
                        self.record_interaction("check_understanding", "User said No", False)
                elif action == "FINISH_SESSION":
                    self.speak(action_input or "Great job! We are done.")
                    break
                    
                else:
                    print(f"Unknown action: {action}. Defaulting to Teach.")
                    self.teach_concept("General")
                
            except Exception as e:
                print(f"ReAct Loop Error: {e}")
                self.teach_concept("Basics")

        self.summarize_session()

    def ask_confirmation(self):
        self.speak("Do you understand? Enter 1 for Yes, 2 for No.")
        print("\n⌨️ Waiting for input (1=Yes, 2=No)...")
        while True:
            try:
                user_input = input("Enter choice (1/2): ").strip()
                if user_input == '1':
                    return True
                elif user_input == '2':
                    return False
                else:
                    print("Please enter number 1 for Yes or 2 for No.")
            except (EOFError, KeyboardInterrupt):
                return False
            
    def teach_concept(self, analogy_hint=""):
        if not self.client:
             self.speak(f"Learning about Grade {self.student_profile.grade} math.")
             return
             
        spec = CurriculumHelper.get_spec(
            self.student_profile.grade, 
            self.student_profile.level, 
            self.student_profile.sublevel
        )
        curriculum_info = json.dumps(spec) if spec else "Basic arithmetic"
        
        # Inject the analogy hint from ReAct into the lesson prompt
        prompt = get_lesson_prompt(
            self.student_profile.grade,
            self.student_profile.level,
            self.student_profile.sublevel,
            curriculum_info
        )
        if analogy_hint:
             prompt += f"\nIMPORTANT Inustrction: {analogy_hint}"
             
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            lesson_text = response.choices[0].message.content
            self.speak(lesson_text)
            self.record_interaction("teach", lesson_text, True)
        except Exception as e:
            print(f"Error in teach_concept: {e}")
            self.speak("Let's add some numbers together.")
            self.record_interaction("error", str(e), False)

    def get_time_remaining(self):
        if not self.start_time:
            return self.duration_seconds
        elapsed = time.time() - self.start_time
        return max(0, self.duration_seconds - elapsed)

    def record_interaction(self, type, content, result):
        # Result: True (Good/Yes), False (Bad/No), None (Info)
        res_str = "Correct" if result is True else "Wrong" if result is False else "N/A"
        
        self.session_history.append({
            "type": type,
            "content": str(content)[:100], # Store a bit more context
            "result": res_str,
            "timestamp": time.time()
        })

    def level_up(self):
        # Simple logic to move sublevels
        pass 

    def level_down(self):
         pass

    def summarize_session(self):
        correct = len([x for x in self.session_history if x.get('result') == 'Correct'])
        total_q = len([x for x in self.session_history if x.get('type') == 'question'])
        print("\n=== Session Summary ===")
        print(f"Questions Attempted: {total_q}")
        print(f"Correct Answers: {correct}")
        if total_q > 0:
            print(f"Accuracy: {int(correct/total_q*100)}%")
        print("=======================")

