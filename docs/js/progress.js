// Course progress tracking via localStorage
const PROGRESS_KEY = "txcourse_progress_v1";

const CourseProgress = {
  _load() {
    try {
      return JSON.parse(localStorage.getItem(PROGRESS_KEY)) || {};
    } catch {
      return {};
    }
  },

  _save(data) {
    localStorage.setItem(PROGRESS_KEY, JSON.stringify(data));
  },

  getAll() {
    return this._load();
  },

  getUnit(unitId) {
    const data = this._load();
    return data[unitId] || { lessonComplete: false, quizScore: null, quizTotal: null, quizDate: null };
  },

  markLessonComplete(unitId) {
    const data = this._load();
    if (!data[unitId]) data[unitId] = {};
    data[unitId].lessonComplete = true;
    data.lastUnit = unitId;
    if (!data.startedAt) data.startedAt = new Date().toISOString().slice(0, 10);
    this._save(data);
  },

  saveQuizResult(unitId, score, total) {
    const data = this._load();
    if (!data[unitId]) data[unitId] = {};
    data[unitId].quizScore = score;
    data[unitId].quizTotal = total;
    data[unitId].quizDate = new Date().toISOString().slice(0, 10);
    data.lastUnit = unitId;
    this._save(data);
  },

  getOverallProgress(units) {
    const data = this._load();
    let lessonsComplete = 0;
    let quizzesPassed = 0;
    let totalScore = 0;
    let totalQuestions = 0;

    for (const u of units) {
      const ud = data[u.unit_id];
      if (!ud) continue;
      if (ud.lessonComplete) lessonsComplete++;
      if (ud.quizScore !== null && ud.quizScore !== undefined) {
        quizzesPassed++;
        totalScore += ud.quizScore;
        totalQuestions += ud.quizTotal;
      }
    }

    return {
      lessonsComplete,
      quizzesPassed,
      totalUnits: units.length,
      avgScore: totalQuestions > 0 ? Math.round((totalScore / totalQuestions) * 100) : null,
      lastUnit: data.lastUnit || null,
      startedAt: data.startedAt || null,
    };
  },

  getUnitStatus(unitId) {
    const ud = this.getUnit(unitId);
    if (ud.quizScore !== null && ud.quizScore !== undefined) return "quiz_done";
    if (ud.lessonComplete) return "lesson_done";
    return "not_started";
  },

  reset() {
    localStorage.removeItem(PROGRESS_KEY);
  },
};
