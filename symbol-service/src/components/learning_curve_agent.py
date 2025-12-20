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
from components.core.curriculum_helper import CurriculumHelper
from prompts.learning_curve_prompts import get_teaching_style_prompt
from prompts.react_prompts import get_reasoning_prompt

class LearningCurveAgent(SimpleVoiceMathTutor):
    """
    Adaptive Learning Agent that uses a ReAct (Reason+Act) architecture.
    Focuses on finding the best TEACHING STRATEGY for the student.
    """
    
    def __init__(self, grade: int, level: int, sublevel: str, duration_minutes: int = 5):
        super().__init__(grade, level, sublevel)
        
        self.duration_seconds = duration_minutes * 60
        self.start_time = None
        self.client = None
        
        # Memory Modules
        self.short_term_memory = []   # Last few interactions
        self.strategies_tried = []    # List of strategies used (e.g., 'story', 'visual')
        self.concepts_taught = []     # Topics covered
        
        try:
            self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        except Exception:
            print("Warning: OpenAI API Key not found. Agent will run in fallback mode.")
        
    def speak(self, text: str):
        """
        Speak text while displaying letter-by-letter synchronized with speech.
        """
        print("\n🔊 ", end="", flush=True)

        if platform.system() == 'Darwin':
            try:
                char_delay = 0.087  
                speech_text = re.sub(r'[^\w\s,.?!]', '', text) 
                
                speech_process = subprocess.Popen(
                    ['say', '-r', '140', speech_text],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )

                time.sleep(0.1)

                for char in text:
                    print(char, end="", flush=True)
                    if char in [',', '.', '!', '?']:
                        time.sleep(char_delay * 2)
                    else:
                        time.sleep(char_delay)

                speech_process.wait(timeout=15)

            except Exception as e:
                print(text)
        else:
            print(text)
        print() 

    def run_session(self):
        """
        ReAct Logic: Perceive -> Memory -> Reason -> Act -> Feedback
        """
        print(f"\n📚 Student Profile: Grade {self.student_profile.grade}, Level {self.student_profile.level}")
        print(f"Starting Adaptive Teaching Session ({self.duration_seconds/60:.1f} mins)")
        
        self.start_time = time.time()
        
        # Progression Path
        self.phases = ["Starter", "Explorer", "Solver", "Champion"]
        try:
            self.current_phase_idx = self.phases.index(self.student_profile.sublevel)
        except ValueError:
            self.current_phase_idx = 0
            
        self.student_profile.sublevel = self.phases[self.current_phase_idx]

        # Initial Perception
        self.speak(f"Hello! I'm your math friend. We are starting with {self.student_profile.sublevel} level.")
        
        # Main ReAct Loop
        while self.get_time_remaining() > 0:
            try:
                # 1. PERCEPTION & MEMORY
                # (Gathered from previous loop's feedback)
                
                # 2. REASONING (The Brain)
                # Decide HOW to teach based on history
                thought, action, strategy = self.reason()
                
                print(f"\n🧠 THOUGHT: {thought}")
                print(f"⚡ ACTION: {action} (Strategy: {strategy})")
                
                # 3. ACTION (Execution)
                if action == "TEACH":
                    self.execute_teach(strategy)
                elif action == "ENCOURAGE":
                    self.execute_encourage()
                elif action == "FINISH":
                    self.speak("You did great today! See you next time!")
                    break
                else:
                    self.execute_teach("standard")
                
                # 4. FEEDBACK (Perception Loop)
                # Always check for understanding after teaching
                if action == "TEACH":
                    understood = self.perceive_understanding()
                    self.update_memory(action, strategy, understood)
                    
                    if understood:
                        # SUCCESS: PROGRESSION LOGIC
                        if self.current_phase_idx < len(self.phases) - 1:
                            self.current_phase_idx += 1
                            new_phase = self.phases[self.current_phase_idx]
                            self.student_profile.sublevel = new_phase
                            
                            self.speak(f"Awesome! You mastered that. Let's move up to {new_phase} mode!")
                            print(f"\n🚀 PROMOTED:  {self.phases[self.current_phase_idx-1]} -> {new_phase}")
                            
                            # Clear specific strategy memory so we start fresh for new topic
                            # but keep general history
                            self.strategies_tried = [] 
                        else:
                            self.speak("Wow! You are a Champion! You completed all levels for this topic!")
                            break # Session complete
                    else:
                        print(f"\n🔄 STAYING: Retrying {self.student_profile.sublevel} with different strategy.")

                
            except Exception as e:
                print(f"ReAct Loop Error: {e}")
                self.execute_teach("simple")

        self.summarize_session()

    def reason(self):
        """
        Uses LLM to decide the next best teaching strategy.
        """
        if not self.client:
            return "Fallback mode", "TEACH", "standard"

        curriculum = CurriculumHelper.get_spec(
            self.student_profile.grade, 
            self.student_profile.level, 
            self.student_profile.sublevel
        )
        curriculum_info = json.dumps(curriculum) if curriculum else "Basic Math"

        prompt = get_reasoning_prompt(
            grade=self.student_profile.grade,
            history=self.short_term_memory,
            strategies_used=self.strategies_tried,
            time_remaining=int(self.get_time_remaining()),
            curriculum=curriculum_info
        )
        
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            stop=["Observation:"]
        )
        
        output = response.choices[0].message.content.strip()
        
        # Parse output
        # Expecting: Thought: ... \n Action: ... \n Strategy: ...
        thought_match = re.search(r"Thought:\s*(.*?)(?=\nAction:|$)", output, re.DOTALL)
        action_match = re.search(r"Action:\s*(.*?)(?=\nStrategy:|$)", output, re.DOTALL)
        strategy_match = re.search(r"Strategy:\s*(.*)", output, re.DOTALL)
        
        thought = thought_match.group(1).strip() if thought_match else "Deciding next step..."
        action = action_match.group(1).strip() if action_match else "TEACH"
        strategy = strategy_match.group(1).strip() if strategy_match else "standard"
        
        # Safety fallback
        if action not in ["TEACH", "ENCOURAGE", "FINISH"]:
            action = "TEACH"
            
        return thought, action, strategy

    def execute_teach(self, strategy):
        """
        Generates and speaks a lesson based on the chosen strategy.
        """
        curriculum = CurriculumHelper.get_spec(
             self.student_profile.grade, 
             self.student_profile.level, 
             self.student_profile.sublevel
        )
        
        prompt = get_teaching_style_prompt(
            grade=self.student_profile.grade,
            topic=json.dumps(curriculum),
            style=strategy
        )
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8 # Higher temp for creativity
            )
            lesson_text = response.choices[0].message.content.strip()
            self.speak(lesson_text)
            
        except Exception:
            self.speak("Let's put some numbers together! 1 plus 1 is 2.")

    def execute_encourage(self):
        self.speak("You're doing great! Math is just like a puzzle.")

    def perceive_understanding(self):
        """
        Ask the user if they understood. 
        Returns True (Yes) or False (No).
        """
        self.speak("Did that make sense? Press 1 for Yes, 2 for No.")
        print("\n⌨️  Waiting for input (1=Yes 👍 / 2=No 👎)...")
        while True:
            try:
                user_input = input("Enter choice: ").strip()
                if user_input == '1':
                    print("✅ Student understood.")
                    return True
                elif user_input == '2':
                    print("❌ Student needs help.")
                    return False
            except (EOFError, KeyboardInterrupt):
                return False
                
    def update_memory(self, action, strategy, result):
        """
        Update short-term and long-term memory.
        """
        self.strategies_tried.append(strategy)
        
        status = "Understood" if result else "Confused"
        entry = f"Action: {action} ({strategy}) -> Result: {status}"
        
        self.short_term_memory.append(entry)
        # Keep memory small
        if len(self.short_term_memory) > 5:
            self.short_term_memory.pop(0)

    def get_time_remaining(self):
        if not self.start_time:
            return self.duration_seconds
        elapsed = time.time() - self.start_time
        return max(0, self.duration_seconds - elapsed)

    def summarize_session(self):
        print("\n=== Session Summary ===")
        print(f"Strategies Used: {set(self.strategies_tried)}")
        print("=======================")

