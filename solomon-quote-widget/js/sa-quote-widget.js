/* ============================================================
   Solomon Agency — Request a Case Quote Widget
   Part 4: BODY-END JS (paste into Carrd → Hidden Embed → Body End)
   ============================================================ */

(function () {
  'use strict';

  /* ---- Configuration ---- */
  var CONFIG = {
    rootSelector: '.sa-quote-widget',
    quoteFormHref: '#quote-form',
    introCallHref: '#intro-call'
  };

  /* ---- Scoring Maps ---- */
  var SCORES = {
    caseType: {
      'family': 1,
      'naturalization': 1,
      'adjustment': 2,
      'rfe': 2,
      'humanitarian': 3,
      'waiver': 3,
      'other': 2
    },
    urgency: {
      'standard': 0,
      'priority': 2,
      'rush': 4
    },
    supportPerItem: 1,
    bilingual: {
      'yes': 1,
      'no': 0
    },
    fileCondition: {
      'organized': 0,
      'scattered': 2,
      'very-scattered': 4
    },
    volume: {
      'one': 0,
      'multiple': 2,
      'ongoing': 3
    }
  };

  /* ---- Result Bands ---- */
  var BANDS = [
    {
      min: 0, max: 5,
      fit: 'Strong fit',
      fitClass: 'saqw-result-badge--strong',
      turnaround: '3\u20135 business days',
      price: 'Starts at $145\u2013$225',
      ctas: ['quote']
    },
    {
      min: 6, max: 10,
      fit: 'Likely fit',
      fitClass: 'saqw-result-badge--likely',
      turnaround: '2\u20134 business days',
      price: 'Starts at $225\u2013$375',
      ctas: ['quote']
    },
    {
      min: 11, max: 15,
      fit: 'Likely fit',
      fitClass: 'saqw-result-badge--likely',
      turnaround: '2\u20133 business days',
      price: 'Starts at $375\u2013$650',
      ctas: ['quote', 'intro']
    },
    {
      min: 16, max: Infinity,
      fit: 'Needs quick review',
      fitClass: 'saqw-result-badge--review',
      turnaround: 'Custom review needed',
      price: 'Requires custom quote',
      ctas: ['intro']
    }
  ];

  /* ---- Label Maps (for summary string) ---- */
  var LABELS = {
    caseType: {
      'family': 'Family-based',
      'humanitarian': 'Humanitarian',
      'waiver': 'Waiver-related',
      'adjustment': 'Adjustment support',
      'rfe': 'RFE evidence support',
      'naturalization': 'Naturalization',
      'other': 'Other/custom'
    },
    urgency: {
      'standard': 'Standard',
      'priority': 'Priority',
      'rush': 'Rush'
    },
    support: {
      'intake': 'Intake cleanup',
      'doc-org': 'Document organization',
      'evidence': 'Missing evidence checklist',
      'bilingual-followup': 'Bilingual client follow-up',
      'summary': 'Case summary/timeline',
      'exhibit': 'Exhibit index prep'
    },
    bilingual: {
      'yes': 'Yes',
      'no': 'No'
    },
    fileCondition: {
      'organized': 'Mostly organized',
      'scattered': 'Somewhat scattered',
      'very-scattered': 'Very scattered/incomplete'
    },
    volume: {
      'one': 'One case',
      'multiple': 'Multiple cases',
      'ongoing': 'Ongoing support'
    }
  };

  /* ---- DOM Helpers ---- */
  function qs(selector, context) {
    return (context || document).querySelector(selector);
  }

  function qsa(selector, context) {
    return (context || document).querySelectorAll(selector);
  }

  /* ---- Scoring Engine ---- */
  function calculateScore(inputs) {
    var score = 0;
    score += (SCORES.caseType[inputs.caseType] || 0);
    score += (SCORES.urgency[inputs.urgency] || 0);
    score += (inputs.supportCount * SCORES.supportPerItem);
    score += (SCORES.bilingual[inputs.bilingual] || 0);
    score += (SCORES.fileCondition[inputs.fileCondition] || 0);
    score += (SCORES.volume[inputs.volume] || 0);
    return score;
  }

  function determineBand(score) {
    for (var i = 0; i < BANDS.length; i++) {
      if (score >= BANDS[i].min && score <= BANDS[i].max) {
        return BANDS[i];
      }
    }
    return BANDS[BANDS.length - 1];
  }

  function applyRushOverride(band, urgency, score) {
    if (urgency !== 'rush') return band;
    if (score >= 16) return band;

    return {
      fit: band.fit,
      fitClass: band.fitClass,
      turnaround: '24\u201348 hours',
      price: band.price,
      ctas: band.ctas,
      rushApplies: true
    };
  }

  /* ---- Input Gathering ---- */
  function gatherInputs(root) {
    var caseTypeEl = qs('#saqw-case-type', root);
    var urgencyEl = qs('#saqw-urgency', root);
    var checkboxes = qsa('input[name="saqw-support"]:checked', root);
    var bilingualEl = qs('#saqw-bilingual', root);
    var fileConditionEl = qs('#saqw-file-condition', root);
    var volumeEl = qs('#saqw-volume', root);

    return {
      caseType: caseTypeEl ? caseTypeEl.value : '',
      urgency: urgencyEl ? urgencyEl.value : '',
      supportCount: checkboxes ? checkboxes.length : 0,
      supportItems: Array.prototype.map.call(checkboxes, function (cb) {
        return cb.value;
      }),
      bilingual: bilingualEl ? bilingualEl.value : '',
      fileCondition: fileConditionEl ? fileConditionEl.value : '',
      volume: volumeEl ? volumeEl.value : ''
    };
  }

  /* ---- Validation ---- */
  function validate(inputs) {
    var missing = [];
    if (!inputs.caseType) missing.push('Case Type');
    if (!inputs.urgency) missing.push('Urgency');
    if (!inputs.bilingual) missing.push('Bilingual Coordination');
    if (!inputs.fileCondition) missing.push('File Condition');
    if (!inputs.volume) missing.push('Volume');
    return missing;
  }

  /* ---- Rendering ---- */
  function renderResult(root, result) {
    var emptyEl = qs('#saqw-result-empty', root);
    var filledEl = qs('#saqw-result-filled', root);
    var badgeEl = qs('#saqw-fit-label', root);
    var turnaroundEl = qs('#saqw-turnaround', root);
    var priceEl = qs('#saqw-price', root);
    var rushNoteEl = qs('#saqw-rush-note', root);
    var ctaAreaEl = qs('#saqw-cta-area', root);

    if (!emptyEl || !filledEl) return;

    // Toggle visibility
    emptyEl.classList.add('saqw-hidden');
    filledEl.classList.remove('saqw-hidden');

    // Fit badge
    if (badgeEl) {
      badgeEl.textContent = result.fit;
      badgeEl.className = 'saqw-result-badge ' + result.fitClass;
    }

    // Turnaround
    if (turnaroundEl) {
      turnaroundEl.textContent = result.turnaround;
    }

    // Price
    if (priceEl) {
      priceEl.textContent = result.price;
    }

    // Rush note
    if (rushNoteEl) {
      if (result.rushApplies) {
        rushNoteEl.classList.remove('saqw-hidden');
      } else {
        rushNoteEl.classList.add('saqw-hidden');
      }
    }

    // CTAs
    if (ctaAreaEl) {
      ctaAreaEl.innerHTML = '';
      var ctaConfigs = {
        'quote': { href: CONFIG.quoteFormHref, text: 'Request a Case Quote', secondary: false },
        'intro': { href: CONFIG.introCallHref, text: 'Book an Intro Call', secondary: false }
      };

      // If there are multiple CTAs, the second one is secondary
      for (var i = 0; i < result.ctas.length; i++) {
        var ctaType = result.ctas[i];
        var cfg = ctaConfigs[ctaType];
        if (!cfg) continue;

        var a = document.createElement('a');
        a.href = cfg.href;
        a.textContent = cfg.text;
        a.className = 'saqw-result-cta';

        if (i > 0) {
          a.className += ' saqw-result-cta--secondary';
        }

        ctaAreaEl.appendChild(a);
      }
    }
  }

  /* ---- Summary String Builder ---- */
  function buildSummaryString(inputs, result, score) {
    var supportLabels = inputs.supportItems.map(function (val) {
      return LABELS.support[val] || val;
    });

    var parts = [
      'Case: ' + (LABELS.caseType[inputs.caseType] || inputs.caseType),
      'Urgency: ' + (LABELS.urgency[inputs.urgency] || inputs.urgency),
      'Support: ' + (supportLabels.length > 0 ? supportLabels.join(', ') : 'None'),
      'Bilingual: ' + (LABELS.bilingual[inputs.bilingual] || inputs.bilingual),
      'File: ' + (LABELS.fileCondition[inputs.fileCondition] || inputs.fileCondition),
      'Volume: ' + (LABELS.volume[inputs.volume] || inputs.volume),
      'Score: ' + score,
      'Fit: ' + result.fit,
      'Turnaround: ' + result.turnaround,
      'Price: ' + result.price
    ];

    if (result.rushApplies) {
      parts.push('Rush: Yes');
    }

    return parts.join(' | ');
  }

  /* ---- Show / Hide Validation ---- */
  function showValidation(root, message) {
    var el = qs('#saqw-validation', root);
    if (!el) return;
    el.textContent = message;
    el.classList.remove('saqw-hidden');
  }

  function hideValidation(root) {
    var el = qs('#saqw-validation', root);
    if (!el) return;
    el.textContent = '';
    el.classList.add('saqw-hidden');
  }

  /* ---- Widget Initialization ---- */
  function init(root) {
    var submitBtn = qs('#saqw-submit', root);
    if (!submitBtn) return;

    submitBtn.addEventListener('click', function () {
      hideValidation(root);

      var inputs = gatherInputs(root);
      var missing = validate(inputs);

      if (missing.length > 0) {
        showValidation(root, 'Please complete: ' + missing.join(', '));
        return;
      }

      var score = calculateScore(inputs);
      var band = determineBand(score);
      var result = applyRushOverride(band, inputs.urgency, score);

      renderResult(root, result);

      // Write summary to hidden field
      var summaryEl = qs('#saqw-estimate-summary', root);
      if (summaryEl) {
        summaryEl.value = buildSummaryString(inputs, result, score);
      }
    });
  }

  /* ---- Bootstrap ---- */
  function bootstrap() {
    var roots = qsa(CONFIG.rootSelector);
    if (!roots || roots.length === 0) return;

    for (var i = 0; i < roots.length; i++) {
      init(roots[i]);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', bootstrap);
  } else {
    bootstrap();
  }

})();
