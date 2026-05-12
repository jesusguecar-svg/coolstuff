// Unit quiz engine — filters questions by unit and runs a quiz session
const UnitQuiz = {
  currentQuestions: [],
  currentIndex: 0,
  answers: [],
  unitId: null,

  start(unitId, container) {
    this.unitId = unitId;
    this.currentIndex = 0;
    this.answers = [];

    // Filter questions for this unit
    const pool = QUESTION_BANK.filter(q => q.unit_id === unitId);

    if (pool.length === 0) {
      container.innerHTML = `
        <div class="quiz-empty">
          <h2>No Questions Available</h2>
          <p>There are no practice questions for this unit yet.</p>
          <a href="#/unit/${unitId}" class="btn btn-secondary">Back to Lesson</a>
          <a href="#/" class="btn btn-secondary">Back to Course</a>
        </div>
      `;
      return;
    }

    // Shuffle and take up to 20
    this.currentQuestions = this._shuffle(pool).slice(0, 20);
    this._renderQuestion(container);
  },

  _shuffle(arr) {
    const a = [...arr];
    for (let i = a.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
  },

  _renderQuestion(container) {
    const q = this.currentQuestions[this.currentIndex];
    const total = this.currentQuestions.length;
    const num = this.currentIndex + 1;
    const pct = Math.round((num / total) * 100);

    container.innerHTML = `
      <div class="quiz-view">
        <div class="quiz-header">
          <a href="#/unit/${this.unitId}" class="breadcrumb">Unit Lesson</a>
          <span class="breadcrumb-sep">/</span>
          <span>Quiz</span>
        </div>
        <div class="quiz-progress">
          <div class="quiz-progress-track"><div class="quiz-progress-bar" style="width:${pct}%"></div></div>
          <span class="quiz-counter">${num} / ${total}</span>
        </div>
        <div class="quiz-meta">
          <span class="badge">${q.domain}</span>
          <span class="badge difficulty-${q.difficulty}">${q.difficulty}</span>
        </div>
        <div class="quiz-stem">${q.stem}</div>
        <div class="quiz-options" id="quizOptions">
          ${q.options.map(o => `
            <button class="quiz-option" data-label="${o.label}">
              <span class="option-label">${o.label}</span>
              <span class="option-text">${o.text}</span>
            </button>
          `).join("")}
        </div>
      </div>
    `;

    container.querySelectorAll(".quiz-option").forEach(btn => {
      btn.onclick = () => this._handleAnswer(btn.dataset.label, container);
    });

    // Keyboard support
    this._keyHandler = (e) => {
      const key = e.key.toUpperCase();
      if (["A", "B", "C", "D"].includes(key)) {
        this._handleAnswer(key, container);
      } else if (["1", "2", "3", "4"].includes(e.key)) {
        this._handleAnswer(String.fromCharCode(64 + parseInt(e.key)), container);
      }
    };
    document.addEventListener("keydown", this._keyHandler);
  },

  _handleAnswer(label, container) {
    document.removeEventListener("keydown", this._keyHandler);

    const q = this.currentQuestions[this.currentIndex];
    const correct = label === q.correct_answer;
    this.answers.push({ question: q, chosen: label, correct });

    // Show feedback
    const options = container.querySelectorAll(".quiz-option");
    options.forEach(btn => {
      btn.disabled = true;
      btn.classList.add("disabled");
      if (btn.dataset.label === q.correct_answer) {
        btn.classList.add("correct");
      } else if (btn.dataset.label === label && !correct) {
        btn.classList.add("wrong");
      }
    });

    const feedbackDiv = document.createElement("div");
    feedbackDiv.className = `quiz-feedback ${correct ? "feedback-correct" : "feedback-wrong"}`;
    feedbackDiv.innerHTML = `
      <div class="feedback-banner">
        ${correct ? "Correct!" : `Incorrect. The answer is ${q.correct_answer}.`}
      </div>
      <div class="feedback-explanation">
        <strong>Why ${q.correct_answer} is correct:</strong>
        <p>${q.correct_explanation}</p>
      </div>
      ${!correct ? `
        <div class="feedback-wrong-explanation">
          <strong>Why ${label} is wrong:</strong>
          <p>${q.wrong_explanations[label] || ""}</p>
        </div>
      ` : ""}
      <button class="btn btn-primary" id="nextQuestionBtn">
        ${this.currentIndex < this.currentQuestions.length - 1 ? "Next Question" : "See Results"}
      </button>
    `;

    container.querySelector(".quiz-view").appendChild(feedbackDiv);
    feedbackDiv.scrollIntoView({ behavior: "smooth" });

    document.getElementById("nextQuestionBtn").onclick = () => {
      this.currentIndex++;
      if (this.currentIndex < this.currentQuestions.length) {
        this._renderQuestion(container);
      } else {
        this._renderResults(container);
      }
    };
  },

  _renderResults(container) {
    const total = this.answers.length;
    const correctCount = this.answers.filter(a => a.correct).length;
    const pct = Math.round((correctCount / total) * 100);
    const passed = pct >= 70;

    // Save result
    CourseProgress.saveQuizResult(this.unitId, correctCount, total);

    const wrongAnswers = this.answers.filter(a => !a.correct);

    container.innerHTML = `
      <div class="quiz-results">
        <div class="quiz-header">
          <a href="#/" class="breadcrumb">Course</a>
          <span class="breadcrumb-sep">/</span>
          <span>Quiz Results</span>
        </div>
        <div class="results-score ${passed ? "score-pass" : "score-fail"}">
          <div class="score-number">${correctCount}/${total}</div>
          <div class="score-pct">${pct}%</div>
          <div class="score-label">${passed ? "Passed" : "Needs Review"}</div>
        </div>
        ${wrongAnswers.length > 0 ? `
          <h3>Questions to Review</h3>
          <div class="review-list">
            ${wrongAnswers.map(a => `
              <div class="review-card">
                <div class="review-stem">${a.question.stem}</div>
                <div class="review-answer">
                  <span class="wrong-choice">Your answer: ${a.chosen} — ${a.question.options.find(o => o.label === a.chosen)?.text || ""}</span>
                </div>
                <div class="review-answer">
                  <span class="correct-choice">Correct: ${a.question.correct_answer} — ${a.question.options.find(o => o.label === a.question.correct_answer)?.text || ""}</span>
                </div>
                <div class="review-explanation">${a.question.correct_explanation}</div>
              </div>
            `).join("")}
          </div>
        ` : `<p class="perfect-score">Perfect score! Great work.</p>`}
        <div class="results-actions">
          <a href="#/unit/${this.unitId}/quiz" class="btn btn-secondary">Retake Quiz</a>
          <a href="#/unit/${this.unitId}" class="btn btn-secondary">Review Lesson</a>
          <a href="#/" class="btn btn-primary">Back to Course</a>
        </div>
      </div>
    `;

    window.scrollTo(0, 0);
  },
};
