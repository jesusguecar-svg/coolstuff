"""User input handling for the practice engine CLI."""


def get_answer_input():
    """Prompt user for an answer selection (A/B/C/D)."""
    while True:
        try:
            choice = input("Your answer (A/B/C/D): ").strip().upper()
        except (EOFError, KeyboardInterrupt):
            print()
            return None
        if choice in ("A", "B", "C", "D"):
            return choice
        print("  Please enter A, B, C, or D.")


def get_session_config(total_available):
    """Prompt user for session configuration."""
    print(f"  {total_available} questions available.")
    print()
    count_input = input(f"  How many questions? (1-{total_available}, or Enter for 10): ").strip()

    if not count_input:
        count = min(10, total_available)
    else:
        try:
            count = int(count_input)
            count = max(1, min(count, total_available))
        except ValueError:
            count = min(10, total_available)

    return {"count": count}
