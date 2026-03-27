"""
Practice session engine for one-question-at-a-time exam simulation.

Manages question sequencing, answer evaluation, explanation delivery,
and session summary generation.
"""

import random
from dataclasses import dataclass, field


@dataclass
class AnswerResult:
    """Result of answering a single question."""
    question_id: str
    selected: str
    correct_answer: str
    is_correct: bool
    correct_explanation: str
    wrong_explanation: str  # explanation for the selected wrong answer, or "" if correct


@dataclass
class SessionSummary:
    """Summary statistics for a completed practice session."""
    total_questions: int
    correct_count: int
    incorrect_count: int
    score_percent: float
    results: list  # list of AnswerResult
    domain_breakdown: dict = field(default_factory=dict)


class PracticeSession:
    """
    One-question-at-a-time practice session.

    Usage:
        session = PracticeSession(questions, count=10)
        while session.has_next():
            q = session.next_question()
            # present q to user, get their answer
            result = session.submit_answer("B")
            # show result.correct_explanation or result.wrong_explanation
        summary = session.get_summary()
    """

    def __init__(self, questions, count=None, shuffle=True):
        """
        Initialize a practice session.

        Args:
            questions: list of question dicts from the loader
            count: number of questions to include (None = all)
            shuffle: whether to randomize question order
        """
        pool = list(questions)
        if shuffle:
            random.shuffle(pool)
        if count is not None:
            pool = pool[:count]

        self._questions = pool
        self._index = 0
        self._results = []

    def has_next(self):
        """Return True if there are more questions in the session."""
        return self._index < len(self._questions)

    def next_question(self):
        """
        Return the next question dict for presentation.
        Does NOT include correct_answer or explanations.
        """
        if not self.has_next():
            return None
        q = self._questions[self._index]
        return {
            "question_number": self._index + 1,
            "total_questions": len(self._questions),
            "question_id": q["question_id"],
            "domain": q["domain"],
            "subdomain": q["subdomain"],
            "difficulty": q["difficulty"],
            "stem": q["stem"],
            "options": q["options"],
        }

    def submit_answer(self, selected_label):
        """
        Submit an answer for the current question.

        Args:
            selected_label: "A", "B", "C", or "D"

        Returns:
            AnswerResult with correctness and explanations
        """
        if not self.has_next():
            raise RuntimeError("No more questions in session")

        selected_label = selected_label.upper().strip()
        if selected_label not in ("A", "B", "C", "D"):
            raise ValueError(f"Invalid answer label: {selected_label}")

        q = self._questions[self._index]
        is_correct = selected_label == q["correct_answer"]

        wrong_explanation = ""
        if not is_correct:
            wrong_explanations = q.get("wrong_explanations", {})
            wrong_explanation = wrong_explanations.get(selected_label, "")

        result = AnswerResult(
            question_id=q["question_id"],
            selected=selected_label,
            correct_answer=q["correct_answer"],
            is_correct=is_correct,
            correct_explanation=q["correct_explanation"],
            wrong_explanation=wrong_explanation,
        )
        self._results.append(result)
        self._index += 1
        return result

    def get_summary(self):
        """Generate a summary of the completed session."""
        correct = sum(1 for r in self._results if r.is_correct)
        total = len(self._results)
        score = (correct / total * 100) if total > 0 else 0.0

        # Domain breakdown
        domain_stats = {}
        for i, r in enumerate(self._results):
            q = self._questions[i] if i < len(self._questions) else {}
            domain = q.get("domain", "Unknown")
            if domain not in domain_stats:
                domain_stats[domain] = {"correct": 0, "total": 0}
            domain_stats[domain]["total"] += 1
            if r.is_correct:
                domain_stats[domain]["correct"] += 1

        return SessionSummary(
            total_questions=total,
            correct_count=correct,
            incorrect_count=total - correct,
            score_percent=round(score, 1),
            results=self._results,
            domain_breakdown=domain_stats,
        )
