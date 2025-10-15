#!/usr/bin/env python3
"""
Interactive Performance Prediction Script

Run this script to predict student performance levels interactively.
"""

import sys
import os

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.performance_metrics import PerformancePredictor
import logging

# Configure logging to show only errors
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def print_banner():
    """Print welcome banner."""
    print("\n" + "=" * 70)
    print("  STUDENT PERFORMANCE LEVEL PREDICTOR")
    print("  Advanced ML-based Classification System")
    print("=" * 70 + "\n")


def print_section(title):
    """Print section header."""
    print(f"\n{'─' * 70}")
    print(f"  {title}")
    print('─' * 70)


def get_valid_input(prompt, input_type, min_val=None, max_val=None, allow_quit=True):
    """
    Get and validate user input.

    Args:
        prompt: Input prompt message
        input_type: Type to convert to (str, int, float)
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        allow_quit: Allow user to type 'quit' to exit

    Returns:
        Validated input value
    """
    while True:
        try:
            user_input = input(f"  {prompt}: ").strip()

            # Check for quit command
            if allow_quit and user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Exiting... Goodbye!")
                sys.exit(0)

            # Convert to appropriate type
            if input_type == str:
                if not user_input:
                    print("  ❌ Input cannot be empty. Please try again.")
                    continue
                return user_input
            elif input_type == int:
                value = int(user_input)
            elif input_type == float:
                value = float(user_input)
            else:
                return user_input

            # Validate range
            if min_val is not None and value < min_val:
                print(f"  ❌ Value must be at least {min_val}. Please try again.")
                continue

            if max_val is not None and value > max_val:
                print(f"  ❌ Value must be at most {max_val}. Please try again.")
                continue

            return value

        except ValueError:
            print(f"  ❌ Invalid input. Please enter a valid {input_type.__name__}.")
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Exiting...")
            sys.exit(0)


def get_student_data():
    """
    Collect student data interactively.

    Returns:
        Dictionary with student data
    """
    print_section("STUDENT DATA INPUT")
    print("  Please provide the following information:")
    print("  (Type 'quit' at any time to exit)\n")

    # Get user ID
    user_id = get_valid_input(
        "Student ID (e.g., student_123)",
        str
    )

    # Get average score
    print("\n  📊 Average Score:")
    print("     The student's average performance score")
    avg_score = get_valid_input(
        "Average Score (0-100)",
        float,
        min_val=0,
        max_val=100
    )

    # Get average time
    print("\n  ⏱️  Average Time:")
    print("     Average time taken to complete tasks (in seconds)")
    avg_time = get_valid_input(
        "Average Time (seconds)",
        float,
        min_val=1,
        max_val=1000
    )

    # Get grade level
    print("\n  🎓 Grade Level:")
    print("     The student's current grade (1-3)")
    grade = get_valid_input(
        "Grade Level (1-3)",
        int,
        min_val=1,
        max_val=3
    )

    return {
        'user_id': user_id,
        'avg_score': avg_score,
        'avg_time': avg_time,
        'grade': grade
    }


def display_input_summary(student_data):
    """Display summary of input data."""
    print_section("INPUT SUMMARY")
    print(f"  Student ID:     {student_data['user_id']}")
    print(f"  Average Score:  {student_data['avg_score']:.1f}")
    print(f"  Average Time:   {student_data['avg_time']:.1f} seconds")
    print(f"  Grade Level:    {student_data['grade']}")
    print()


def display_prediction_results(result):
    """
    Display prediction results in a formatted manner.

    Args:
        result: Prediction result dictionary
    """
    print_section("PREDICTION RESULTS")

    # Main classification
    print("\n  🎯 CLASSIFICATION:")
    print(f"     Level:    {result['level_name']} (Level {result['level']})")
    print(f"     Sublevel: {result['sublevel_name']}")

    # Confidence
    confidence_emoji = {
        'High': '🟢',
        'Medium': '🟡',
        'Low': '🔴'
    }
    emoji = confidence_emoji.get(result['confidence_category'], '⚪')

    print(f"\n  {emoji} CONFIDENCE:")
    print(f"     Overall:  {result['overall_confidence']:.1%} ({result['confidence_category']})")
    print(f"     Level:    {result['level_confidence']:.1%}")
    print(f"     Sublevel: {result['sublevel_confidence']:.1%}")

    # Probability distribution
    print(f"\n  📊 LEVEL PROBABILITIES:")
    for level, prob in result['level_probabilities'].items():
        bar_length = int(prob * 40)  # Scale to 40 chars
        bar = '█' * bar_length + '░' * (40 - bar_length)
        print(f"     {level}: {bar} {prob:.1%}")

    # Performance metrics
    print(f"\n  ⚡ PERFORMANCE:")
    print(f"     Efficiency Ratio:  {result['features_summary']['efficiency_ratio']:.2f} pts/sec")
    print(f"     Score Percentile:  {result['features_summary']['score_percentile']:.0f}th")
    print(f"     Prediction Time:   {result['prediction_latency_ms']:.1f}ms")

    # Recommendation
    print(f"\n  💡 RECOMMENDATION:")
    recommendations = result['recommendation'].split('; ')
    for rec in recommendations:
        print(f"     • {rec}")

    # Warnings (if any)
    if result.get('validation_warnings'):
        print(f"\n  ⚠️  WARNINGS:")
        warnings = result['validation_warnings'].split('; ')
        for warning in warnings:
            print(f"     • {warning}")

    print()


def display_level_guide():
    """Display guide explaining levels and sublevels."""
    print_section("UNDERSTANDING THE LEVELS")

    print("\n  📚 PERFORMANCE LEVELS:\n")

    print("     Level 1 - Beginning Proficiency")
    print("       Students are building foundational skills")
    print("       Typical score range: 30-70\n")

    print("     Level 2 - Intermediate Proficiency")
    print("       Students have solid understanding and skills")
    print("       Typical score range: 60-85\n")

    print("     Level 3 - Advanced Proficiency")
    print("       Students demonstrate exceptional mastery")
    print("       Typical score range: 75-100\n")

    print("  🏆 SUBLEVELS:\n")

    print("     Starter:   Initial learning phase, building basics")
    print("     Explorer:  Developing skills, showing progress")
    print("     Solver:    Competent problem-solving abilities")
    print("     Champion:  Exceptional performance and mastery")

    print()


def load_predictor(model_dir='models/performance_metrics'):
    """
    Load the trained predictor.

    Args:
        model_dir: Directory containing trained models

    Returns:
        Loaded PerformancePredictor or None if failed
    """
    print("  🔄 Loading trained models...")

    if not os.path.exists(model_dir):
        print(f"\n  ❌ Error: Model directory '{model_dir}' not found!")
        print(f"  💡 Please train the models first:")
        print(f"     python scripts/train_performance_models.py --sample\n")
        return None

    try:
        predictor = PerformancePredictor()
        predictor.load_models(model_dir)
        print("  ✅ Models loaded successfully!\n")
        return predictor
    except Exception as e:
        print(f"\n  ❌ Error loading models: {e}")
        print(f"  💡 Please retrain the models:")
        print(f"     python scripts/train_performance_models.py --sample\n")
        return None


def ask_continue():
    """Ask user if they want to make another prediction."""
    while True:
        response = input("\n  Would you like to predict for another student? (yes/no): ").strip().lower()
        if response in ['yes', 'y']:
            return True
        elif response in ['no', 'n', 'quit', 'exit', 'q']:
            return False
        else:
            print("  ❌ Please enter 'yes' or 'no'")


def main():
    """Main function."""
    try:
        # Print banner
        print_banner()

        # Load predictor
        predictor = load_predictor()
        if predictor is None:
            sys.exit(1)

        # Main prediction loop
        while True:
            try:
                # Get student data
                student_data = get_student_data()

                # Display input summary
                display_input_summary(student_data)

                # Confirm before prediction
                confirm = input("  Proceed with prediction? (yes/no): ").strip().lower()
                if confirm not in ['yes', 'y']:
                    print("  ⏭️  Skipping prediction...\n")
                    if not ask_continue():
                        break
                    continue

                # Make prediction
                print("\n  🔮 Analyzing student performance...")
                result = predictor.predict(student_data)

                # Display results
                display_prediction_results(result)

                # Show guide
                show_guide = input("  Would you like to see the level guide? (yes/no): ").strip().lower()
                if show_guide in ['yes', 'y']:
                    display_level_guide()

                # Ask to continue
                if not ask_continue():
                    break

            except KeyboardInterrupt:
                print("\n\n  ⏸️  Interrupted. Returning to menu...")
                if not ask_continue():
                    break
            except Exception as e:
                print(f"\n  ❌ Error during prediction: {e}")
                if not ask_continue():
                    break

        # Exit message
        print("\n" + "=" * 70)
        print("  Thank you for using the Performance Predictor!")
        print("  For more information, see: QUICK_START.md")
        print("=" * 70 + "\n")

    except KeyboardInterrupt:
        print("\n\n👋 Exiting... Goodbye!\n")
        sys.exit(0)


if __name__ == "__main__":
    main()
