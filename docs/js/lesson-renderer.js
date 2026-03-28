// Lesson rendering module
const LessonRenderer = {
  render(lesson, container, onComplete, onQuiz) {
    const status = CourseProgress.getUnitStatus(lesson.unit_id);
    const toc = lesson.sections
      .filter(s => s.level <= 2)
      .map((s, i) => `<a href="#section-${i}" class="toc-link">${s.heading}</a>`)
      .join("");

    container.innerHTML = `
      <div class="lesson-layout">
        <nav class="lesson-toc">
          <div class="toc-header">Contents</div>
          ${toc}
        </nav>
        <article class="lesson-content">
          <div class="lesson-header">
            <a href="#/" class="breadcrumb">Course</a>
            <span class="breadcrumb-sep">/</span>
            <span>Unit ${lesson.order}: ${lesson.title}</span>
          </div>
          <div class="lesson-meta">
            <span class="badge weight-badge">${lesson.exam_weight} exam weight</span>
            <span class="badge time-badge">${lesson.reading_time_min} min read</span>
          </div>
          <div class="lesson-body" id="lessonBody">
            ${lesson.sections.map((s, i) => `
              <section id="section-${i}">
                <h${Math.min(s.level + 1, 4)}>${s.heading}</h${Math.min(s.level + 1, 4)}>
                ${s.content_html}
              </section>
            `).join("")}
          </div>
          <div class="lesson-footer">
            ${status === "not_started" ? `
              <button class="btn btn-primary btn-lg" id="markCompleteBtn">
                Mark Lesson Complete & Take Quiz
              </button>
            ` : `
              <div class="lesson-complete-badge">Lesson Complete</div>
              <button class="btn btn-primary" id="takeQuizBtn">
                ${status === "quiz_done" ? "Retake Quiz" : "Take Unit Quiz"}
              </button>
            `}
            <a href="#/" class="btn btn-secondary">Back to Course</a>
          </div>
        </article>
      </div>
    `;

    const markBtn = document.getElementById("markCompleteBtn");
    if (markBtn) {
      markBtn.onclick = () => {
        onComplete(lesson.unit_id);
        onQuiz(lesson.unit_id);
      };
    }

    const quizBtn = document.getElementById("takeQuizBtn");
    if (quizBtn) {
      quizBtn.onclick = () => onQuiz(lesson.unit_id);
    }

    // Scroll to top
    window.scrollTo(0, 0);
  },
};
