"""Display components for rendering questions, results, and summaries."""


def show_question(question_data):
    """Render a question for the user."""
    print()
    print(f"━━━ Question {question_data['question_number']}/{question_data['total_questions']} ━━━")
    print(f"[{question_data['domain']} > {question_data['subdomain']}]  Difficulty: {question_data['difficulty']}")
    print()
    print(question_data["stem"])
    print()
    for opt in question_data["options"]:
        print(f"  {opt['label']}) {opt['text']}")
    print()


def show_result(result):
    """Render the result of a submitted answer."""
    if result.is_correct:
        print(f"  CORRECT! The answer is {result.correct_answer}.")
    else:
        print(f"  INCORRECT. You chose {result.selected}; the correct answer is {result.correct_answer}.")
    print()
    print(f"  Why {result.correct_answer} is correct:")
    print(f"    {result.correct_explanation}")
    if not result.is_correct and result.wrong_explanation:
        print()
        print(f"  Why {result.selected} is wrong:")
        print(f"    {result.wrong_explanation}")
    print()


def show_summary(summary):
    """Render the end-of-session summary."""
    print()
    print("=" * 60)
    print("  SESSION SUMMARY")
    print("=" * 60)
    print(f"  Score: {summary.correct_count}/{summary.total_questions} ({summary.score_percent}%)")
    print(f"  Correct: {summary.correct_count}  |  Incorrect: {summary.incorrect_count}")
    print()

    if summary.domain_breakdown:
        print("  Domain Breakdown:")
        for domain, stats in sorted(summary.domain_breakdown.items()):
            pct = round(stats["correct"] / stats["total"] * 100, 1) if stats["total"] > 0 else 0
            print(f"    {domain}: {stats['correct']}/{stats['total']} ({pct}%)")
    print()

    # List missed questions
    missed = [r for r in summary.results if not r.is_correct]
    if missed:
        print(f"  Questions to Review ({len(missed)}):")
        for r in missed:
            print(f"    {r.question_id} — You chose {r.selected}, correct was {r.correct_answer}")
    else:
        print("  Perfect score!")
    print("=" * 60)
    print()
