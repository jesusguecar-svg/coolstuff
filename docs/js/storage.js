/**
 * ExamStorage — localStorage abstraction for tracking answer history.
 * All data stored per profile key namespace.
 */

const ExamStorage = (function () {
  "use strict";

  const APP_KEY = "txexam_app_state";
  const HISTORY_PREFIX = "txexam_history__";

  function _safeJsonParse(raw, fallback) {
    try {
      return raw ? JSON.parse(raw) : fallback;
    } catch (e) {
      return fallback;
    }
  }

  function _getAppState() {
    const base = _safeJsonParse(localStorage.getItem(APP_KEY), {
      activeProfile: "default",
      profiles: ["default"],
      preferencesByProfile: {
        default: { language: "en", theme: "light" },
      },
    });

    const profiles = Array.isArray(base.profiles) && base.profiles.length
      ? [...new Set(base.profiles.map(p => String(p).trim()).filter(Boolean))]
      : ["default"];

    if (!profiles.includes("default")) profiles.unshift("default");

    const activeProfile = profiles.includes(base.activeProfile) ? base.activeProfile : "default";

    const prefsByProfile = (base.preferencesByProfile && typeof base.preferencesByProfile === "object")
      ? { ...base.preferencesByProfile }
      : {};

    profiles.forEach(p => {
      const pref = prefsByProfile[p] || {};
      prefsByProfile[p] = {
        language: pref.language === "es" ? "es" : "en",
        theme: pref.theme === "dark" ? "dark" : "light",
      };
    });

    return { activeProfile, profiles, preferencesByProfile: prefsByProfile };
  }

  function _saveAppState(state) {
    try {
      localStorage.setItem(APP_KEY, JSON.stringify(state));
    } catch (e) {}
  }

  function _historyKey(profile) {
    return HISTORY_PREFIX + profile;
  }

  function _load(profileName) {
    return _safeJsonParse(localStorage.getItem(_historyKey(profileName)), {});
  }

  function _save(profileName, data) {
    try {
      localStorage.setItem(_historyKey(profileName), JSON.stringify(data));
    } catch (e) {
      // localStorage full or unavailable — silently fail
    }
  }

  function _activeProfile() {
    return _getAppState().activeProfile || "default";
  }

  return {
    getProfiles() {
      return [..._getAppState().profiles];
    },

    getActiveProfile() {
      return _activeProfile();
    },

    setActiveProfile(profileName) {
      const state = _getAppState();
      if (!state.profiles.includes(profileName)) return false;
      state.activeProfile = profileName;
      if (!state.preferencesByProfile[profileName]) {
        state.preferencesByProfile[profileName] = { language: "en", theme: "light" };
      }
      _saveAppState(state);
      return true;
    },

    createProfile(profileName) {
      const clean = (profileName || "").trim();
      if (!clean) return { ok: false, error: "Profile name required." };
      const state = _getAppState();
      if (state.profiles.includes(clean)) return { ok: false, error: "Profile already exists." };
      state.profiles.push(clean);
      state.preferencesByProfile[clean] = { language: "en", theme: "light" };
      state.activeProfile = clean;
      _saveAppState(state);
      return { ok: true };
    },

    deleteProfile(profileName) {
      if (profileName === "default") return { ok: false, error: "Default profile cannot be deleted." };
      const state = _getAppState();
      if (!state.profiles.includes(profileName)) return { ok: false, error: "Profile not found." };
      state.profiles = state.profiles.filter(p => p !== profileName);
      delete state.preferencesByProfile[profileName];
      try { localStorage.removeItem(_historyKey(profileName)); } catch (e) {}
      if (state.activeProfile === profileName) state.activeProfile = "default";
      _saveAppState(state);
      return { ok: true };
    },

    getPreferences() {
      const state = _getAppState();
      return state.preferencesByProfile[_activeProfile()] || { language: "en", theme: "light" };
    },

    setPreferences(nextPrefs) {
      const state = _getAppState();
      const active = _activeProfile();
      const current = state.preferencesByProfile[active] || { language: "en", theme: "light" };
      state.preferencesByProfile[active] = { ...current, ...nextPrefs };
      _saveAppState(state);
    },

    /**
     * Record a single answer result.
     */
    recordAnswer(questionId, isCorrect, domain, difficulty) {
      const data = _load(_activeProfile());
      data[questionId] = {
        correct: isCorrect,
        domain: domain,
        difficulty: difficulty,
        ts: Date.now(),
      };
      _save(_activeProfile(), data);
    },

    /**
     * Return Set of all answered question IDs.
     */
    getAnsweredIds() {
      return new Set(Object.keys(_load(_activeProfile())));
    },

    /**
     * Return full history map: questionId -> result object.
     */
    getHistory() {
      return _load(_activeProfile());
    },

    /**
     * Compute aggregate stats from history.
     */
    getStats() {
      const data = _load(_activeProfile());
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
        localStorage.removeItem(_historyKey(_activeProfile()));
      } catch (e) {}
    },
  };
})();
