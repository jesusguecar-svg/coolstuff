/**
 * UI controller for the Texas Insurance Practice Exam web app.
 * Manages view transitions and DOM updates.
 */

(function () {
  "use strict";

  let session = null;
  let currentQuestion = null;

  // --- DOM refs ---
  const views = {
    welcome: document.getElementById("view-welcome"),
    question: document.getElementById("view-question"),
    feedback: document.getElementById("view-feedback"),
    summary: document.getElementById("view-summary"),
  };

  function showView(name) {
    Object.values(views).forEach(v => v.classList.remove("active"));
    views[name].classList.add("active");
    window.scrollTo(0, 0);
  }

  // --- Welcome view ---
  function initWelcome() {
    const stats = computeStats(QUESTION_BANK);
    const statsBox = document.getElementById("stats-box");
    statsBox.innerHTML =
      `<div class="stat"><span class="stat-num">${stats.total}</span> questions</div>` +
      `<div class="stat"><span class="stat-num">${stats.domainCount}</span> domains</div>` +
      `<div class="stat-difficulty">` +
        `<span class="diff easy">${stats.easy} easy</span>` +
        `<span class="diff medium">${stats.medium} medium</span>` +
        `<span class="diff hard">${stats.hard} hard</span>` +
      `</div>`;

    document.getElementById("count-hint").textContent = `of ${stats.total}`;
    document.getElementById("question-count").max = stats.total;
  }

  function computeStats(questions) {
    const domains = new Set();
    let easy = 0, medium = 0, hard = 0;
    questions.forEach(q => {
      domains.add(q.domain);
      if (q.difficulty === "easy") easy++;
      else if (q.difficulty === "medium") medium++;
      else hard++;
    });
    return { total: questions.length, domainCount: domains.size, easy, medium, hard };
  }

  // --- Question view ---
  function showQuestion(q) {
    currentQuestion = q;
    const pct = ((q.questionNumber - 1) / q.totalQuestions) * 100;
    document.getElementById("progress-bar").style.width = pct + "%";
    document.getElementById("q-domain").textContent = q.domain;
    const diffEl = document.getElementById("q-difficulty");
    diffEl.textContent = q.difficulty;
    diffEl.className = "badge badge-difficulty " + q.difficulty;
    document.getElementById("q-counter").textContent =
      `${q.questionNumber} / ${q.totalQuestions}`;
    document.getElementById("q-stem").textContent = q.stem;

    const optionsEl = document.getElementById("q-options");
    optionsEl.innerHTML = "";
    q.options.forEach(opt => {
      const btn = document.createElement("button");
      btn.className = "option-btn";
      btn.innerHTML = `<span class="option-label">${opt.label}</span><span class="option-text">${opt.text}</span>`;
      btn.addEventListener("click", () => handleAnswer(opt.label));
      optionsEl.appendChild(btn);
    });

    showView("question");
  }

  // --- Answer handling ---
  function handleAnswer(label) {
    const result = session.submitAnswer(label);
    showFeedback(result);
  }

  function showFeedback(result) {
    // Keep progress and meta context
    const q = currentQuestion;
    const pct = (q.questionNumber / q.totalQuestions) * 100;
    document.getElementById("feedback-progress-bar").style.width = pct + "%";
    document.getElementById("fb-domain").textContent = q.domain;
    const diffEl = document.getElementById("fb-difficulty");
    diffEl.textContent = q.difficulty;
    diffEl.className = "badge badge-difficulty " + q.difficulty;
    document.getElementById("fb-counter").textContent =
      `${q.questionNumber} / ${q.totalQuestions}`;
    document.getElementById("fb-stem").textContent = q.stem;

    // Banner
    const banner = document.getElementById("fb-banner");
    if (result.isCorrect) {
      banner.className = "feedback-banner correct";
      banner.textContent = `Correct! The answer is ${result.correctAnswer}.`;
    } else {
      banner.className = "feedback-banner wrong";
      banner.textContent =
        `Incorrect. You chose ${result.selected}; the correct answer is ${result.correctAnswer}.`;
    }

    // Correct explanation
    document.getElementById("fb-correct-label").textContent = result.correctAnswer;
    document.getElementById("fb-correct-text").textContent = result.correctExplanation;

    // Wrong explanations for all incorrect options
    const wrongBoxes = document.getElementById("fb-wrong-boxes");
    wrongBoxes.innerHTML = "";
    const wrongEntries = Object.entries(result.wrongExplanations);
    if (wrongEntries.length > 0) {
      // Show the user's wrong pick first (highlighted), then the rest
      const sorted = wrongEntries.sort((a, b) => {
        if (a[0] === result.selected) return -1;
        if (b[0] === result.selected) return 1;
        return a[0].localeCompare(b[0]);
      });
      // Find option text for each label
      const optionText = {};
      (result.options || []).forEach(o => { optionText[o.label] = o.text; });

      sorted.forEach(([label, explanation]) => {
        const isUserPick = !result.isCorrect && label === result.selected;
        const box = document.createElement("div");
        box.className = "explanation-box wrong-box" + (isUserPick ? " user-pick" : "");
        const optText = optionText[label] ? ` — ${optionText[label]}` : "";
        box.innerHTML =
          `<div class="explanation-label">` +
            `${label}${optText}` +
            `${isUserPick ? ' <span class="your-answer-tag">your answer</span>' : ""}` +
          `</div>` +
          `<div class="explanation-text">${explanation}</div>`;
        wrongBoxes.appendChild(box);
      });
    }

    // Next button
    const btnNext = document.getElementById("btn-next");
    btnNext.textContent = session.hasNext() ? "Next Question" : "See Results";

    showView("feedback");
  }

  // --- Summary view ---
  function showSummary(summary) {
    // Score
    const scoreBox = document.getElementById("score-box");
    const grade = summary.scorePercent >= 70 ? "pass" : "fail";
    scoreBox.innerHTML =
      `<div class="score-main ${grade}">` +
        `<span class="score-num">${summary.correctCount}/${summary.totalQuestions}</span>` +
        `<span class="score-pct">${summary.scorePercent}%</span>` +
      `</div>` +
      `<div class="score-detail">` +
        `Correct: ${summary.correctCount} &middot; Incorrect: ${summary.incorrectCount}` +
      `</div>`;

    // Domain breakdown
    const tbody = document.getElementById("domain-tbody");
    tbody.innerHTML = "";
    const sorted = Object.entries(summary.domainBreakdown)
      .sort((a, b) => a[0].localeCompare(b[0]));
    sorted.forEach(([domain, stats]) => {
      const pct = stats.total > 0 ? Math.round((stats.correct / stats.total) * 100) : 0;
      const tr = document.createElement("tr");
      tr.innerHTML =
        `<td>${domain}</td>` +
        `<td>${stats.correct}/${stats.total}</td>` +
        `<td class="${pct >= 70 ? 'pass' : 'fail'}">${pct}%</td>`;
      tbody.appendChild(tr);
    });

    // Missed questions
    const missed = summary.results.filter(r => !r.isCorrect);
    const missedSection = document.getElementById("missed-section");
    const missedList = document.getElementById("missed-list");
    if (missed.length > 0) {
      missedSection.style.display = "block";
      missedList.innerHTML = missed.map(r =>
        `<div class="missed-item">` +
          `<span class="missed-id">${r.questionId}</span> ` +
          `You chose <strong>${r.selected}</strong>, correct: <strong>${r.correctAnswer}</strong>` +
        `</div>`
      ).join("");
    } else {
      missedSection.style.display = "block";
      missedList.innerHTML = `<div class="perfect">Perfect score!</div>`;
    }

    showView("summary");
  }

  // --- Event listeners ---
  document.getElementById("btn-start").addEventListener("click", () => {
    const countInput = document.getElementById("question-count");
    let count = parseInt(countInput.value, 10);
    if (isNaN(count) || count < 1) count = 10;
    if (count > QUESTION_BANK.length) count = QUESTION_BANK.length;

    session = new PracticeSession(QUESTION_BANK, count);
    const q = session.nextQuestion();
    showQuestion(q);
  });

  document.getElementById("btn-next").addEventListener("click", () => {
    if (session.hasNext()) {
      showQuestion(session.nextQuestion());
    } else {
      showSummary(session.getSummary());
    }
  });

  document.getElementById("btn-restart").addEventListener("click", () => {
    session = null;
    currentQuestion = null;
    showView("welcome");
  });

  // Quick count buttons
  document.querySelectorAll(".quick-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      document.getElementById("question-count").value = btn.dataset.count;
    });
  });

  // Keyboard shortcuts: 1-4 or A-D to select answer
  document.addEventListener("keydown", (e) => {
    if (!views.question.classList.contains("active")) return;
    const keyMap = { "1": "A", "2": "B", "3": "C", "4": "D", "a": "A", "b": "B", "c": "C", "d": "D" };
    const label = keyMap[e.key.toLowerCase()];
    if (label) handleAnswer(label);
  });

  // Enter key for next question
  document.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      if (views.feedback.classList.contains("active")) {
        document.getElementById("btn-next").click();
      } else if (views.welcome.classList.contains("active")) {
        document.getElementById("btn-start").click();
      } else if (views.summary.classList.contains("active")) {
        document.getElementById("btn-restart").click();
      }
    }
  });

  // Initialize
  initWelcome();
})();
