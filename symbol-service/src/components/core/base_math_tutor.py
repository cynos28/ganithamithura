"""
Base Math Tutor Class

Shared functionality for all math tutors:
- Student profile management
- Question generation
- Statistics tracking
- Speech utilities
- Microphone setup

Subclasses implement specific features (voice output, image generation, etc.)
"""

import os
import sys
from abc import ABC, abstractmethod
from typing import Dict, Optional, Tuple

# Add parent directory to path
# sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..')) # Not trustworthy depending on runner

from src.prompts.math_question_prompts import get_question_generation_prompt, get_system_prompt


class StudentProfile:
    """Represents a student's profile and curriculum level."""

    VALID_GRADES = [1, 2, 3]
    VALID_LEVELS = [1, 2, 3]
    VALID_SUBLEVELS = ["Starter", "Explorer", "Solver", "Champion"]

    def __init__(self, grade: int, level: int, sublevel: str):
        """
        Initialize student profile.

        Args:
            grade: 1, 2, or 3
            level: 1, 2, or 3
            sublevel: Starter, Explorer, Solver, or Champion
        """
        if grade not in self.VALID_GRADES:
            raise ValueError(f"Grade must be {self.VALID_GRADES}")
        if level not in self.VALID_LEVELS:
            raise ValueError(f"Level must be {self.VALID_LEVELS}")
        if sublevel not in self.VALID_SUBLEVELS:
            raise ValueError(f"Sublevel must be {self.VALID_SUBLEVELS}")

        self.grade = grade
        self.level = level
        self.sublevel = sublevel

    def __str__(self):
        return f"Grade {self.grade}, Level {self.level} - {self.sublevel}"


class BaseMathTutor(ABC):
    """
    Abstract base class for math tutors.

    Provides:
    - Student profile management
    - Statistics tracking
    - Question generation prompts
    - Microphone setup helpers

    Subclasses must implement:
    - setup_voice()
    - speak()
    - run_session()
    """

    def __init__(self, grade: int, level: int, sublevel: str):
        """
        Initialize base tutor with student profile.

        Args:
            grade: 1, 2, or 3
            level: 1, 2, or 3
            sublevel: Starter, Explorer, Solver, or Champion
        """
        self.student_profile = StudentProfile(grade, level, sublevel)

        # Statistics
        self.stats = {
            'total_questions': 0,
            'correct_answers': 0,
            'wrong_answers': 0,
            'questions_history': []
        }

        # Track recent questions to avoid repetition
        self.recent_questions = []
        self.max_recent_questions = 10

    @abstractmethod
    def setup_voice(self):
        """Setup voice system (implementation depends on subclass)."""
        pass

    @abstractmethod
    def speak(self, text: str):
        """Speak text (implementation depends on subclass)."""
        pass

    @abstractmethod
    def run_session(self):
        """Run tutoring session (implementation depends on subclass)."""
        pass

    def get_question_prompt(self) -> str:
        """
        Get AI prompt for question generation based on student profile.

        Returns:
            Prompt string for AI question generation
        """
        return get_question_generation_prompt(
            grade=self.student_profile.grade,
            performance_level=self.student_profile.level,
            sublevel=self.student_profile.sublevel
        )

    def get_system_prompt(self) -> str:
        """
        Get system prompt for AI.

        Returns:
            System prompt string
        """
        return get_system_prompt()

    def display_profile(self):
        """Display student profile information."""
        print(f"\n📚 Student Profile: {self.student_profile}")

    def show_stats(self):
        """Display session statistics."""
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

    @staticmethod
    def get_student_profile_interactive() -> Tuple[int, int, str]:
        """
        Interactively get student profile from user.

        Returns:
            Tuple of (grade, level, sublevel)
        """
        print("\n" + "="*60)
        print("📚 STUDENT PROFILE SETUP")
        print("="*60)

        # Get Grade
        print("\n📖 Enter Grade Level (1, 2, or 3) [default: 1]: ", end="")
        try:
            grade_input = input().strip()
            grade = int(grade_input) if grade_input else 1
            if grade not in [1, 2, 3]:
                print("⚠️ Invalid grade, using default: 1")
                grade = 1
        except ValueError:
            print("⚠️ Invalid input, using default: 1")
            grade = 1

        grade_names = {
            1: "Grade 1 - Addition",
            2: "Grade 2 - Multi-digit & Multiplication",
            3: "Grade 3 - Extended Operations"
        }
        print(f"✅ Selected: {grade_names[grade]}")

        # Get Performance Level
        print("\n📊 Choose Performance Level:")
        print("   1. Beginning     - Foundation skills")
        print("   2. Intermediate  - Developing skills")
        print("   3. Advanced      - Mastery level")
        print("\nEnter 1-3 [default: 1]: ", end="")

        try:
            level_input = input().strip()
            level = int(level_input) if level_input else 1
            if level not in [1, 2, 3]:
                print("⚠️ Invalid level, using default: 1")
                level = 1
        except ValueError:
            print("⚠️ Invalid input, using default: 1")
            level = 1

        level_names = {1: "Beginning", 2: "Intermediate", 3: "Advanced"}
        print(f"✅ Selected: Level {level} - {level_names[level]}")

        # Get Sublevel
        print("\n🎯 Choose Sublevel:")
        print("   1. Starter   - Basic foundational concepts")
        print("   2. Explorer  - Developing skills and patterns")
        print("   3. Solver    - Competent problem solving")
        print("   4. Champion  - Advanced challenges and mastery")
        print("\nEnter 1-4 [default: 1]: ", end="")

        sublevel_options = ["Starter", "Explorer", "Solver", "Champion"]
        try:
            sublevel_choice = input().strip()
            choice = int(sublevel_choice) if sublevel_choice else 1
            if choice < 1 or choice > 4:
                print("⚠️ Invalid choice, using default: Starter")
                sublevel = "Starter"
            else:
                sublevel = sublevel_options[choice - 1]
        except ValueError:
            print("⚠️ Invalid input, using default: Starter")
            sublevel = "Starter"

        print(f"✅ Selected: {sublevel}")

        return grade, level, sublevel
