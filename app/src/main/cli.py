"""
CLI entry point for the Texas General Lines Practice Engine.

Runs an interactive one-question-at-a-time practice session using
validated question batches loaded from the manifest.
"""

import sys
from pathlib import Path

# Ensure app/src is importable
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.loader import load_all_questions, get_question_stats
from core.session import PracticeSession
from components.display import show_question, show_result, show_summary
from components.input_handler import get_answer_input, get_session_config


def print_welcome():
    """Display welcome banner."""
    print()
    print("=" * 60)
    print("  Texas General Lines Life, Accident, Health & HMO")
    print("  Practice Exam Engine")
    print("=" * 60)
    print()


def print_stats(stats):
    """Display question bank statistics."""
    print(f"  Loaded {stats['total_questions']} questions from {stats['total_batches']} batches")
    print(f"  Difficulty: {stats['difficulties'].get('easy', 0)} easy, "
          f"{stats['difficulties'].get('medium', 0)} medium, "
          f"{stats['difficulties'].get('hard', 0)} hard")
    print(f"  Domains: {len(stats['domains'])}")
    print()


def run_session():
    """Run a single interactive practice session."""
    print_welcome()

    # Load questions
    try:
        stats = get_question_stats()
        print_stats(stats)
        questions = load_all_questions()
    except FileNotFoundError as e:
        print(f"  Error: {e}")
        print("  Ensure validated batch files and manifest are present in data/questions_validated/")
        sys.exit(1)

    # Configure session
    config = get_session_config(len(questions))
    session = PracticeSession(questions, count=config["count"])

    print()
    print(f"  Starting {config['count']}-question practice session...")
    print("  (Ctrl+C to quit early)")
    print()

    # Question loop
    while session.has_next():
        question_data = session.next_question()
        show_question(question_data)

        answer = get_answer_input()
        if answer is None:
            print("\n  Session ended early.")
            break

        result = session.submit_answer(answer)
        show_result(result)

        # Pause between questions
        if session.has_next():
            try:
                input("  Press Enter for next question...")
            except (EOFError, KeyboardInterrupt):
                print("\n  Session ended early.")
                break

    # Summary
    summary = session.get_summary()
    show_summary(summary)


def main():
    """Main entry point."""
    try:
        run_session()
    except KeyboardInterrupt:
        print("\n\n  Goodbye!")
        sys.exit(0)


if __name__ == "__main__":
    main()
