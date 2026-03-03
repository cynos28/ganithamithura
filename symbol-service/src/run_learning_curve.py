
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
    
    # 1. Get Grade
    try:
        grade = int(input("Enter Grade (1-3): ").strip())
        if grade not in [1, 2, 3]: raise ValueError
    except:
        grade = 1
        print("Defaulting to Grade 1")

    # 2. Get Level
    try:
        level = int(input("Enter Level (1-3): ").strip())
        if level not in [1, 2, 3]: raise ValueError
    except:
        level = 1
        print("Defaulting to Level 1")

    # 3. Get Sublevel (Strict)
    print("\nSelect Phase:")
    phases = ["Starter", "Explorer", "Solver", "Champion"]
    for i, p in enumerate(phases):
        print(f"{i+1}. {p}")
    
    try:
        idx = int(input("Choose phase (1-4): ").strip()) - 1
        if 0 <= idx < len(phases):
            sublevel = phases[idx]
        else:
            raise ValueError
    except:
        sublevel = "Starter"
        print("Defaulting to Starter")
    
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
