
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.components.learning_curve_agent import LearningCurveAgent
from src.components.core.base_math_tutor import BaseMathTutor
from dotenv import load_dotenv

def main():
    load_dotenv()
    
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not found in .env")
        return

    print("--- Learning Curve Agent Runner ---")
    grade, level, sublevel = BaseMathTutor.get_student_profile_interactive()
    
    # Let user pick duration
    try:
        duration = int(input("\nEnter session duration in minutes (5-10) [default: 5]: ").strip() or 5)
    except:
        duration = 5
        
    print(f"\nInitializing Agent for Grade {grade}, Level {level} ({sublevel})...")
    
    agent = LearningCurveAgent(grade, level, sublevel, duration_minutes=duration)
    agent.run_session()

if __name__ == "__main__":
    main()
