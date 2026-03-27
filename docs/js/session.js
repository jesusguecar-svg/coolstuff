/**
 * PracticeSession — port of app/src/core/session.py
 * Manages one-question-at-a-time exam sessions.
 */

class PracticeSession {
  /**
   * @param {Array} questions - Array of question objects from QUESTION_BANK
   * @param {number} count - Number of questions for this session
   * @param {boolean} shuffle - Whether to randomize order
   */
  constructor(questions, count = null, shuffle = true) {
    let pool = [...questions];
    if (shuffle) {
      for (let i = pool.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [pool[i], pool[j]] = [pool[j], pool[i]];
      }
    }
    if (count !== null) {
      pool = pool.slice(0, count);
    }
    this._questions = pool;
    this._index = 0;
    this._results = [];
  }

  hasNext() {
    return this._index < this._questions.length;
  }

  /**
   * Return the next question for presentation (no answers/explanations).
   */
  nextQuestion() {
    if (!this.hasNext()) return null;
    const q = this._questions[this._index];
    return {
      questionNumber: this._index + 1,
      totalQuestions: this._questions.length,
      questionId: q.question_id,
      domain: q.domain,
      subdomain: q.subdomain,
      difficulty: q.difficulty,
      stem: q.stem,
      options: q.options,
    };
  }

  /**
   * Submit an answer and get the result with explanations.
   * @param {string} selectedLabel - "A", "B", "C", or "D"
   * @returns {Object} AnswerResult
   */
  submitAnswer(selectedLabel) {
    if (!this.hasNext()) throw new Error("No more questions");
    selectedLabel = selectedLabel.toUpperCase().trim();
    if (!["A", "B", "C", "D"].includes(selectedLabel)) {
      throw new Error("Invalid answer: " + selectedLabel);
    }

    const q = this._questions[this._index];
    const isCorrect = selectedLabel === q.correct_answer;
    let wrongExplanation = "";
    if (!isCorrect) {
      wrongExplanation = (q.wrong_explanations || {})[selectedLabel] || "";
    }

    const result = {
      questionId: q.question_id,
      selected: selectedLabel,
      correctAnswer: q.correct_answer,
      isCorrect,
      correctExplanation: q.correct_explanation,
      wrongExplanation,
    };

    this._results.push(result);
    this._index++;
    return result;
  }

  /**
   * Generate session summary with domain breakdown.
   */
  getSummary() {
    const correct = this._results.filter(r => r.isCorrect).length;
    const total = this._results.length;
    const scorePercent = total > 0 ? Math.round((correct / total) * 1000) / 10 : 0;

    const domainBreakdown = {};
    this._results.forEach((r, i) => {
      const q = this._questions[i] || {};
      const domain = q.domain || "Unknown";
      if (!domainBreakdown[domain]) {
        domainBreakdown[domain] = { correct: 0, total: 0 };
      }
      domainBreakdown[domain].total++;
      if (r.isCorrect) domainBreakdown[domain].correct++;
    });

    return {
      totalQuestions: total,
      correctCount: correct,
      incorrectCount: total - correct,
      scorePercent,
      results: this._results,
      domainBreakdown,
    };
  }
}
