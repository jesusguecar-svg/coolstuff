/**
 * ExamStorage — localStorage abstraction for tracking answer history.
 * All data stored under a single key: txexam_history
 */

const ExamStorage = (function () {
  "use strict";

  const STORAGE_KEY = "txexam_history";

  function _load() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      return raw ? JSON.parse(raw) : {};
    } catch (e) {
      return {};
    }
  }

  function _save(data) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
    } catch (e) {
      // localStorage full or unavailable — silently fail
    }
  }

  return {
    /**
     * Record a single answer result.
     */
    recordAnswer(questionId, isCorrect, domain, difficulty) {
      const data = _load();
      data[questionId] = {
        correct: isCorrect,
        domain: domain,
        difficulty: difficulty,
        ts: Date.now(),
      };
      _save(data);
    },

    /**
     * Return Set of all answered question IDs.
     */
    getAnsweredIds() {
      return new Set(Object.keys(_load()));
    },

    /**
     * Return full history map: questionId -> result object.
     */
    getHistory() {
      return _load();
    },

    /**
     * Compute aggregate stats from history.
     */
    getStats() {
      const data = _load();
      const entries = Object.values(data);
      const totalAnswered = entries.length;
      const totalCorrect = entries.filter(e => e.correct).length;

      const byDomain = {};
      const byDifficulty = { easy: { answered: 0, correct: 0 }, medium: { answered: 0, correct: 0 }, hard: { answered: 0, correct: 0 } };

      entries.forEach(e => {
        // Domain
        if (!byDomain[e.domain]) {
          byDomain[e.domain] = { answered: 0, correct: 0 };
        }
        byDomain[e.domain].answered++;
        if (e.correct) byDomain[e.domain].correct++;

        // Difficulty
        if (byDifficulty[e.difficulty]) {
          byDifficulty[e.difficulty].answered++;
          if (e.correct) byDifficulty[e.difficulty].correct++;
        }
      });

      return { totalAnswered, totalCorrect, byDomain, byDifficulty };
    },

    /**
     * Wipe all stored data.
     */
    clearHistory() {
      try {
        localStorage.removeItem(STORAGE_KEY);
      } catch (e) {}
    },
  };
})();
