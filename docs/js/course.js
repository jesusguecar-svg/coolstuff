// Course router and home view controller
const CourseApp = {
  container: null,

  init() {
    this.container = document.getElementById("app");
    window.addEventListener("hashchange", () => this.route());
    this.route();
  },

  route() {
    const hash = location.hash.slice(1) || "/";

    // /#/unit/N1/quiz
    const quizMatch = hash.match(/^\/unit\/([A-Z0-9]+)\/quiz$/);
    if (quizMatch) {
      UnitQuiz.start(quizMatch[1], this.container);
      return;
    }

    // /#/unit/N1
    const unitMatch = hash.match(/^\/unit\/([A-Z0-9]+)$/);
    if (unitMatch) {
      this.showLesson(unitMatch[1]);
      return;
    }

    // Default: course home
    this.showHome();
  },

  showHome() {
    const progress = CourseProgress.getOverallProgress(LESSONS);
    const questionsByUnit = {};
    for (const q of QUESTION_BANK) {
      if (!questionsByUnit[q.unit_id]) questionsByUnit[q.unit_id] = 0;
      questionsByUnit[q.unit_id]++;
    }

    // Continue section
    let continueHtml = "";
    if (progress.lastUnit) {
      const lastLesson = LESSONS.find(l => l.unit_id === progress.lastUnit);
      if (lastLesson) {
        const status = CourseProgress.getUnitStatus(progress.lastUnit);
        const nextAction = status === "lesson_done"
          ? `<a href="#/unit/${progress.lastUnit}/quiz" class="btn btn-primary btn-sm">Take Quiz</a>`
          : `<a href="#/unit/${progress.lastUnit}" class="btn btn-primary btn-sm">Continue</a>`;
        continueHtml = `
          <div class="continue-bar">
            <p>Continue: <strong>Unit ${lastLesson.order} — ${lastLesson.title}</strong></p>
            ${nextAction}
          </div>
        `;
      }
    }

    // Unit cards
    const unitsHtml = LESSONS.map(lesson => {
      const status = CourseProgress.getUnitStatus(lesson.unit_id);
      const ud = CourseProgress.getUnit(lesson.unit_id);
      const qCount = questionsByUnit[lesson.unit_id] || 0;

      let scoreHtml = "";
      if (ud.quizScore !== null && ud.quizScore !== undefined) {
        const pct = Math.round((ud.quizScore / ud.quizTotal) * 100);
        const cls = pct >= 70 ? "pass" : "fail";
        scoreHtml = `<span class="unit-score ${cls}">${pct}%</span>`;
      }

      let statusText = `${qCount} questions`;
      if (status === "lesson_done") statusText = "Lesson complete";
      else if (status === "quiz_done") statusText = `Quiz: ${ud.quizScore}/${ud.quizTotal}`;

      const href = status === "lesson_done" ? `#/unit/${lesson.unit_id}/quiz` : `#/unit/${lesson.unit_id}`;

      return `
        <a href="${href}" class="unit-card">
          <div class="unit-number ${status.replace("_", "-")}">${lesson.order}</div>
          <div class="unit-info">
            <div class="unit-title">${lesson.title}</div>
            <div class="unit-subtitle">${lesson.exam_weight} exam weight · ${statusText}</div>
          </div>
          <div class="unit-right">
            ${scoreHtml}
            <span class="unit-arrow">&rsaquo;</span>
          </div>
        </a>
      `;
    }).join("");

    this.container.innerHTML = `
      <div class="course-home">
        <div class="course-hero">
          <h1>Texas Life, Accident & Health</h1>
          <p>Step-by-step exam preparation — study each unit, then test your knowledge.</p>
        </div>

        <div class="progress-summary">
          <div class="stat-card">
            <div class="stat-value">${progress.lessonsComplete}/${progress.totalUnits}</div>
            <div class="stat-label">Lessons Complete</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">${progress.quizzesPassed}/${progress.totalUnits}</div>
            <div class="stat-label">Quizzes Taken</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">${progress.avgScore !== null ? progress.avgScore + "%" : "—"}</div>
            <div class="stat-label">Avg Quiz Score</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">${QUESTION_BANK.length}</div>
            <div class="stat-label">Practice Questions</div>
          </div>
        </div>

        ${continueHtml}

        <div class="section-title">Course Units</div>
        <div class="unit-list">
          ${unitsHtml}
        </div>
      </div>
    `;

    window.scrollTo(0, 0);
  },

  showLesson(unitId) {
    const lesson = LESSONS.find(l => l.unit_id === unitId);
    if (!lesson) {
      this.container.innerHTML = `<div class="course-home"><p>Unit not found.</p><a href="#/">Back to Course</a></div>`;
      return;
    }

    LessonRenderer.render(
      lesson,
      this.container,
      (id) => CourseProgress.markLessonComplete(id),
      (id) => { location.hash = `#/unit/${id}/quiz`; }
    );
  },
};

// Boot
CourseApp.init();
