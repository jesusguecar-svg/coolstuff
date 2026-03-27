/**
 * UI controller for the Texas Insurance Practice Exam web app.
 * Manages view transitions, filtering, deferred feedback, and dashboard stats.
 */

(function () {
  "use strict";

  let session = null;
  let currentQuestion = null;
  let deferredMode = false;

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

  // =========================================================
  //  Welcome View — Stats, Filters, Count
  // =========================================================

  function initWelcome() {
    renderDashboardStats();
    populateDomainCheckboxes();
    updateCountHint();
  }

  function renderDashboardStats() {
    const statsBox = document.getElementById("stats-box");
    const history = ExamStorage.getStats();
    const totalBank = QUESTION_BANK.length;
    const domains = new Set(QUESTION_BANK.map(q => q.domain));

    if (history.totalAnswered === 0) {
      // Fresh user — simple stats
      const easy = QUESTION_BANK.filter(q => q.difficulty === "easy").length;
      const medium = QUESTION_BANK.filter(q => q.difficulty === "medium").length;
      const hard = QUESTION_BANK.filter(q => q.difficulty === "hard").length;
      statsBox.innerHTML =
        `<div class="stat"><span class="stat-num">${totalBank}</span> questions</div>` +
        `<div class="stat"><span class="stat-num">${domains.size}</span> domains</div>` +
        `<div class="stat-difficulty">` +
          `<span class="diff easy">${easy} easy</span>` +
          `<span class="diff medium">${medium} medium</span>` +
          `<span class="diff hard">${hard} hard</span>` +
        `</div>`;
      return;
    }

    // Returning user — rich stats
    const pct = Math.round((history.totalCorrect / history.totalAnswered) * 100);
    const progressPct = Math.round((history.totalAnswered / totalBank) * 100);

    let html = `<div class="dash-section dash-overall">`;
    html += `<div class="dash-big-num">${pct}%</div>`;
    html += `<div class="dash-sub">${history.totalAnswered} of ${totalBank} answered (${progressPct}% complete)</div>`;
    html += `<div class="progress-full"><div class="progress-full-bar" style="width:${progressPct}%"></div></div>`;
    html += `</div>`;

    // Difficulty breakdown
    html += `<div class="dash-section"><h4>By Difficulty</h4><div class="dash-row">`;
    ["easy", "medium", "hard"].forEach(d => {
      const s = history.byDifficulty[d];
      const dpct = s.answered > 0 ? Math.round((s.correct / s.answered) * 100) : 0;
      html += `<div class="dash-diff-item">` +
        `<div class="diff-label ${d}">${d}</div>` +
        `<div class="diff-stat">${dpct}% (${s.answered})</div>` +
        `</div>`;
    });
    html += `</div></div>`;

    // Domain breakdown
    html += `<div class="dash-section"><h4>By Domain</h4>`;
    const sortedDomains = [...domains].sort();
    sortedDomains.forEach(domain => {
      const ds = history.byDomain[domain];
      const answered = ds ? ds.answered : 0;
      const correct = ds ? ds.correct : 0;
      const domainTotal = QUESTION_BANK.filter(q => q.domain === domain).length;
      const dpct = answered > 0 ? Math.round((correct / answered) * 100) : 0;
      const coveragePct = Math.round((answered / domainTotal) * 100);
      html += `<div class="dash-domain-row">` +
        `<span class="domain-name">${domain}</span>` +
        `<div class="progress-mini"><div class="progress-mini-bar" style="width:${coveragePct}%"></div></div>` +
        `<span class="domain-pct">${dpct}%</span>` +
        `</div>`;
    });
    html += `</div>`;

    // Clear history button
    html += `<div class="dash-clear"><button class="link-btn" id="btn-clear-history">Clear history</button></div>`;

    statsBox.innerHTML = html;

    document.getElementById("btn-clear-history").addEventListener("click", () => {
      ExamStorage.clearHistory();
      renderDashboardStats();
      updateCountHint();
    });
  }

  function populateDomainCheckboxes() {
    const container = document.getElementById("domain-checkboxes");
    const domains = [...new Set(QUESTION_BANK.map(q => q.domain))].sort();
    const subCounts = getDomainSubdomainCounts();

    container.innerHTML = domains.map(d => {
      const total = QUESTION_BANK.filter(q => q.domain === d).length;
      const catalog = DOMAIN_CATALOG[d];
      const desc = catalog ? catalog.description : "";
      const subs = subCounts[d] || {};
      const subHtml = Object.keys(subs).sort().map(s =>
        `<div class="domain-card-sub-item"><span>${s}</span><span class="sub-count">${subs[s]}</span></div>`
      ).join("");
      const outlineHtml = catalog && catalog.outlineSections
        ? catalog.outlineSections.map(s => `<span class="outline-tag">${s}</span>`).join("")
        : "";

      return `<div class="domain-card">` +
        `<div class="domain-card-header">` +
          `<input type="checkbox" value="${d}" checked>` +
          `<span class="domain-card-name">${d}</span>` +
          `<span class="domain-card-count">${total}</span>` +
          `<button class="domain-card-arrow" aria-label="Expand">&#9660;</button>` +
        `</div>` +
        `<div class="domain-card-body">` +
          (desc ? `<p class="domain-card-desc">${desc}</p>` : "") +
          (outlineHtml ? `<div class="domain-card-outline">${outlineHtml}</div>` : "") +
          (subHtml ? `<div class="domain-card-subs"><div class="domain-card-subs-title">Subdomains</div>${subHtml}</div>` : "") +
        `</div>` +
      `</div>`;
    }).join("");

    // Listen for checkbox changes
    container.querySelectorAll("input[type=checkbox]").forEach(cb => {
      cb.addEventListener("change", updateCountHint);
    });

    // Expand/collapse
    container.querySelectorAll(".domain-card-arrow").forEach(arrow => {
      arrow.addEventListener("click", (e) => {
        e.stopPropagation();
        const card = arrow.closest(".domain-card");
        card.classList.toggle("expanded");
      });
    });

    // Click header name to expand too
    container.querySelectorAll(".domain-card-name").forEach(name => {
      name.addEventListener("click", (e) => {
        const card = name.closest(".domain-card");
        card.classList.toggle("expanded");
      });
    });
  }

  function getFilteredPool() {
    // Difficulty
    const diffToggles = document.querySelectorAll("#difficulty-toggles input:checked");
    const activeDiffs = new Set([...diffToggles].map(cb => cb.value));

    // Domains
    const domainCbs = document.querySelectorAll("#domain-checkboxes input:checked");
    const activeDomains = new Set([...domainCbs].map(cb => cb.value));

    // Skip answered
    const skipAnswered = document.getElementById("opt-skip-answered").checked;
    const answeredIds = skipAnswered ? ExamStorage.getAnsweredIds() : new Set();

    // Deferred feedback
    const deferFeedback = document.getElementById("opt-deferred-feedback").checked;

    let pool = QUESTION_BANK.filter(q =>
      activeDiffs.has(q.difficulty) &&
      activeDomains.has(q.domain) &&
      (!skipAnswered || !answeredIds.has(q.question_id))
    );

    return { pool, deferFeedback };
  }

  function updateCountHint() {
    const { pool } = getFilteredPool();
    const hint = document.getElementById("count-hint");
    const input = document.getElementById("question-count");
    const warning = document.getElementById("filter-warning");
    const startBtn = document.getElementById("btn-start");

    hint.textContent = `of ${pool.length}`;
    input.max = pool.length;

    if (pool.length === 0) {
      warning.classList.add("visible");
      startBtn.disabled = true;
    } else {
      warning.classList.remove("visible");
      startBtn.disabled = false;
      if (parseInt(input.value, 10) > pool.length) {
        input.value = pool.length;
      }
    }
  }

  // =========================================================
  //  Question View
  // =========================================================

  function showQuestion(q) {
    currentQuestion = q;
    const pct = ((q.questionNumber - 1) / q.totalQuestions) * 100;
    document.getElementById("progress-bar").style.width = pct + "%";
    document.getElementById("q-domain").textContent = q.domain;
    document.getElementById("q-subdomain").textContent = q.subdomain;
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

  // =========================================================
  //  Answer Handling
  // =========================================================

  function handleAnswer(label) {
    const result = session.submitAnswer(label);

    // Record to localStorage
    const q = currentQuestion;
    ExamStorage.recordAnswer(result.questionId, result.isCorrect, q.domain, q.difficulty);

    if (deferredMode) {
      // Skip feedback, go to next question or summary
      if (session.hasNext()) {
        showQuestion(session.nextQuestion());
      } else {
        showSummary(session.getSummary());
      }
    } else {
      showFeedback(result);
    }
  }

  // =========================================================
  //  Feedback View
  // =========================================================

  function showFeedback(result) {
    const q = currentQuestion;
    const pct = (q.questionNumber / q.totalQuestions) * 100;
    document.getElementById("feedback-progress-bar").style.width = pct + "%";
    document.getElementById("fb-domain").textContent = q.domain;
    document.getElementById("fb-subdomain").textContent = q.subdomain;
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

    // Wrong explanations
    const wrongBoxes = document.getElementById("fb-wrong-boxes");
    wrongBoxes.innerHTML = "";
    const wrongEntries = Object.entries(result.wrongExplanations);
    if (wrongEntries.length > 0) {
      const sorted = wrongEntries.sort((a, b) => {
        if (a[0] === result.selected) return -1;
        if (b[0] === result.selected) return 1;
        return a[0].localeCompare(b[0]);
      });
      const optionText = {};
      (result.options || []).forEach(o => { optionText[o.label] = o.text; });

      sorted.forEach(([lbl, explanation]) => {
        const isUserPick = !result.isCorrect && lbl === result.selected;
        const box = document.createElement("div");
        box.className = "explanation-box wrong-box" + (isUserPick ? " user-pick" : "");
        const optText = optionText[lbl] ? ` — ${optionText[lbl]}` : "";
        box.innerHTML =
          `<div class="explanation-label">` +
            `${lbl}${optText}` +
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

  // =========================================================
  //  Summary View
  // =========================================================

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

    // Domain + subdomain breakdown
    const tbody = document.getElementById("domain-tbody");
    tbody.innerHTML = "";

    // Build subdomain stats
    const subBreakdown = {};
    summary.results.forEach((r, i) => {
      const q = session.questions[i];
      const key = q.domain + "|||" + q.subdomain;
      if (!subBreakdown[key]) subBreakdown[key] = { domain: q.domain, subdomain: q.subdomain, correct: 0, total: 0 };
      subBreakdown[key].total++;
      if (r.isCorrect) subBreakdown[key].correct++;
    });

    const sorted = Object.entries(summary.domainBreakdown)
      .sort((a, b) => a[0].localeCompare(b[0]));
    sorted.forEach(([domain, stats]) => {
      const pct = stats.total > 0 ? Math.round((stats.correct / stats.total) * 100) : 0;
      // Domain header row
      const tr = document.createElement("tr");
      tr.className = "domain-header-row";
      const domainSubs = Object.values(subBreakdown).filter(s => s.domain === domain);
      const hasMultipleSubs = domainSubs.length > 1;
      tr.innerHTML =
        `<td>${hasMultipleSubs ? '<button class="subdomain-toggle" aria-label="Expand subdomains">&#9654;</button> ' : ''}${domain}</td>` +
        `<td>${stats.correct}/${stats.total}</td>` +
        `<td class="${pct >= 70 ? 'pass' : 'fail'}">${pct}%</td>`;
      tbody.appendChild(tr);

      // Subdomain rows (hidden by default)
      if (hasMultipleSubs) {
        domainSubs.sort((a, b) => a.subdomain.localeCompare(b.subdomain)).forEach(sub => {
          const spct = sub.total > 0 ? Math.round((sub.correct / sub.total) * 100) : 0;
          const subTr = document.createElement("tr");
          subTr.className = "subdomain-row";
          subTr.innerHTML =
            `<td>${sub.subdomain}</td>` +
            `<td>${sub.correct}/${sub.total}</td>` +
            `<td class="${spct >= 70 ? 'pass' : 'fail'}">${spct}%</td>`;
          tbody.appendChild(subTr);
        });
      }

      // Toggle subdomain rows
      if (hasMultipleSubs) {
        const toggle = tr.querySelector(".subdomain-toggle");
        toggle.addEventListener("click", () => {
          tr.classList.toggle("expanded");
          let next = tr.nextElementSibling;
          while (next && next.classList.contains("subdomain-row")) {
            next.classList.toggle("visible");
            next = next.nextElementSibling;
          }
        });
      }
    });

    // Missed questions (immediate mode)
    const missed = summary.results.filter(r => !r.isCorrect);
    const missedSection = document.getElementById("missed-section");
    const missedList = document.getElementById("missed-list");
    const deferredSection = document.getElementById("deferred-review");
    const deferredList = document.getElementById("deferred-review-list");

    if (deferredMode) {
      // Deferred: show full question-by-question review
      missedSection.style.display = "none";
      deferredSection.style.display = "block";
      deferredList.innerHTML = "";

      const questions = session.questions;
      summary.results.forEach((r, i) => {
        const q = questions[i];
        const card = document.createElement("div");
        card.className = "review-card " + (r.isCorrect ? "review-correct" : "review-wrong");

        let inner = `<div class="review-header">`;
        inner += `<span class="review-num">Q${i + 1}</span>`;
        inner += `<span class="review-result ${r.isCorrect ? 'correct' : 'wrong'}">${r.isCorrect ? 'Correct' : 'Incorrect'}</span>`;
        inner += `</div>`;
        inner += `<div class="review-stem">${q.stem}</div>`;
        inner += `<div class="review-answer"><span class="label">Your answer:</span> ${r.selected}</div>`;
        if (!r.isCorrect) {
          inner += `<div class="review-answer"><span class="label">Correct answer:</span> ${r.correctAnswer}</div>`;
        }
        inner += `<div class="review-explanation"><strong>Why ${r.correctAnswer} is correct:</strong> ${r.correctExplanation}</div>`;

        // Wrong explanations
        const wrongEntries = Object.entries(r.wrongExplanations);
        if (wrongEntries.length > 0) {
          wrongEntries.sort((a, b) => a[0].localeCompare(b[0]));
          wrongEntries.forEach(([lbl, explanation]) => {
            const tag = (!r.isCorrect && lbl === r.selected) ? ' <span class="your-answer-tag">your answer</span>' : '';
            inner += `<div class="review-explanation"><strong>Why ${lbl} is wrong${tag}:</strong> ${explanation}</div>`;
          });
        }

        card.innerHTML = inner;
        deferredList.appendChild(card);
      });
    } else {
      // Immediate mode: show missed questions
      deferredSection.style.display = "none";
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
    }

    showView("summary");
  }

  // =========================================================
  //  Event Listeners
  // =========================================================

  // Start button
  document.getElementById("btn-start").addEventListener("click", () => {
    const { pool, deferFeedback } = getFilteredPool();
    if (pool.length === 0) return;

    deferredMode = deferFeedback;

    let count = parseInt(document.getElementById("question-count").value, 10);
    if (isNaN(count) || count < 1) count = 10;
    if (count > pool.length) count = pool.length;

    session = new PracticeSession(pool, count);
    const q = session.nextQuestion();
    showQuestion(q);
  });

  // Next button
  document.getElementById("btn-next").addEventListener("click", () => {
    if (session.hasNext()) {
      showQuestion(session.nextQuestion());
    } else {
      showSummary(session.getSummary());
    }
  });

  // Restart
  document.getElementById("btn-restart").addEventListener("click", () => {
    session = null;
    currentQuestion = null;
    deferredMode = false;
    initWelcome();
    showView("welcome");
  });

  // Quick count buttons
  document.querySelectorAll(".quick-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      document.getElementById("question-count").value = btn.dataset.count;
    });
  });

  // Filter toggle
  document.getElementById("filter-toggle").addEventListener("click", () => {
    const body = document.getElementById("filter-body");
    const arrow = document.getElementById("filter-arrow");
    body.classList.toggle("open");
    arrow.classList.toggle("open");
  });

  // Difficulty toggles
  document.querySelectorAll("#difficulty-toggles input").forEach(cb => {
    cb.addEventListener("change", updateCountHint);
  });

  // Domain all/none
  document.getElementById("domain-select-all").addEventListener("click", () => {
    document.querySelectorAll("#domain-checkboxes input").forEach(cb => { cb.checked = true; });
    updateCountHint();
  });
  document.getElementById("domain-select-none").addEventListener("click", () => {
    document.querySelectorAll("#domain-checkboxes input").forEach(cb => { cb.checked = false; });
    updateCountHint();
  });

  // Skip answered toggle
  document.getElementById("opt-skip-answered").addEventListener("change", updateCountHint);

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

  // =========================================================
  //  Domain Guide Modal
  // =========================================================

  function renderDomainGuide() {
    const body = document.getElementById("domain-guide-body");
    const subCounts = getDomainSubdomainCounts();
    const domains = [...new Set(QUESTION_BANK.map(q => q.domain))].sort();

    let html = `<p class="guide-intro">This exam covers <strong>${QUESTION_BANK.length} questions</strong> across <strong>${domains.length} domains</strong>. Select domains in the filter panel to focus your study.</p>`;

    domains.forEach(d => {
      const total = QUESTION_BANK.filter(q => q.domain === d).length;
      const catalog = DOMAIN_CATALOG[d];
      const subs = subCounts[d] || {};

      html += `<div class="guide-domain">`;
      html += `<div class="guide-domain-header"><span class="guide-domain-name">${d}</span><span class="guide-domain-count">${total} questions</span></div>`;

      if (catalog) {
        html += `<p class="guide-domain-desc">${catalog.description}</p>`;
        if (catalog.outlineSections && catalog.outlineSections.length) {
          html += `<div class="guide-outline-tags">`;
          catalog.outlineSections.forEach(s => {
            html += `<span class="outline-tag">${s}</span>`;
          });
          html += `</div>`;
        }
      }

      const subKeys = Object.keys(subs).sort();
      if (subKeys.length > 0) {
        html += `<div class="guide-sub-list">`;
        subKeys.forEach(s => {
          html += `<div class="guide-sub-item"><span>${s}</span><span class="sub-count">${subs[s]}</span></div>`;
        });
        html += `</div>`;
      }

      html += `</div>`;
    });

    body.innerHTML = html;
  }

  function openDomainGuide() {
    renderDomainGuide();
    document.getElementById("domain-guide-overlay").classList.add("active");
    document.body.style.overflow = "hidden";
  }

  function closeDomainGuide() {
    document.getElementById("domain-guide-overlay").classList.remove("active");
    document.body.style.overflow = "";
  }

  document.getElementById("btn-domain-guide").addEventListener("click", openDomainGuide);
  document.getElementById("domain-guide-close").addEventListener("click", closeDomainGuide);
  document.getElementById("domain-guide-overlay").addEventListener("click", (e) => {
    if (e.target === e.currentTarget) closeDomainGuide();
  });

  // Escape key closes modal
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && document.getElementById("domain-guide-overlay").classList.contains("active")) {
      closeDomainGuide();
    }
  });

  // Initialize
  initWelcome();
})();
