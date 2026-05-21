const ExamStorage = (function () {
  "use strict";

  const APP_KEY = "txexam_app_state_v2";
  const LEGACY_APP_KEY = "txexam_app_state";
  const HISTORY_PREFIX = "txexam_history_v2__";
  const LEGACY_HISTORY_PREFIX = "txexam_history__";
  const DEFAULT_PROFILE = "default";
  const DEFAULT_PREFS = { language: "en", theme: "light" };

  function _safeJsonParse(raw, fallback) {
    try { return raw ? JSON.parse(raw) : fallback; } catch (_) { return fallback; }
  }

  function _normalizeState(state) {
    const s = state && typeof state === "object" ? state : {};
    const profiles = Array.isArray(s.profiles) ? s.profiles.filter(p => typeof p === "string" && p.trim()) : [DEFAULT_PROFILE];
    if (!profiles.length) profiles.push(DEFAULT_PROFILE);
    if (!profiles.includes(DEFAULT_PROFILE)) profiles.unshift(DEFAULT_PROFILE);

    const preferencesByProfile = (s.preferencesByProfile && typeof s.preferencesByProfile === "object") ? s.preferencesByProfile : {};
    profiles.forEach((p) => {
      const pref = preferencesByProfile[p] && typeof preferencesByProfile[p] === "object" ? preferencesByProfile[p] : {};
      preferencesByProfile[p] = {
        language: pref.language === "es" ? "es" : "en",
        theme: pref.theme === "dark" ? "dark" : "light",
      };
    });

    const activeProfile = profiles.includes(s.activeProfile) ? s.activeProfile : profiles[0];
    return { activeProfile, profiles, preferencesByProfile };
  }

  function _saveAppState(state) {
    try { localStorage.setItem(APP_KEY, JSON.stringify(_normalizeState(state))); } catch (_) {}
  }

  function _getAppState() {
    const v2 = _safeJsonParse(localStorage.getItem(APP_KEY), null);
    if (v2) return _normalizeState(v2);

    const legacy = _safeJsonParse(localStorage.getItem(LEGACY_APP_KEY), null);
    const migrated = _normalizeState(legacy || { activeProfile: DEFAULT_PROFILE, profiles: [DEFAULT_PROFILE], preferencesByProfile: { [DEFAULT_PROFILE]: DEFAULT_PREFS } });
    _saveAppState(migrated);

    migrated.profiles.forEach((p) => {
      const hasV2 = localStorage.getItem(_historyKey(p));
      if (!hasV2) {
        const legacyHistory = _safeJsonParse(localStorage.getItem(LEGACY_HISTORY_PREFIX + p), {});
        _save(p, _normalizeHistory(legacyHistory));
      }
    });

    return migrated;
  }

  function _historyKey(profile) { return HISTORY_PREFIX + profile; }

  function _normalizeHistory(data) {
    if (!data || typeof data !== "object" || Array.isArray(data)) return {};
    const out = {};
    Object.entries(data).forEach(([qid, entry]) => {
      if (!entry || typeof entry !== "object") return;
      const difficulty = ["easy", "medium", "hard"].includes(entry.difficulty) ? entry.difficulty : null;
      const domain = typeof entry.domain === "string" ? entry.domain : "Unknown";
      if (!difficulty) return;
      out[qid] = {
        correct: !!entry.correct,
        domain,
        difficulty,
        ts: Number.isFinite(entry.ts) ? entry.ts : Date.now(),
      };
    });
    return out;
  }

  function _load(profileName) {
    const parsed = _safeJsonParse(localStorage.getItem(_historyKey(profileName)), {});
    const normalized = _normalizeHistory(parsed);
    if (JSON.stringify(parsed) !== JSON.stringify(normalized)) _save(profileName, normalized);
    return normalized;
  }

  function _save(profileName, data) {
    try { localStorage.setItem(_historyKey(profileName), JSON.stringify(_normalizeHistory(data))); } catch (_) {}
  }

  function _activeProfile() { return _getAppState().activeProfile || DEFAULT_PROFILE; }

  return {
    getProfiles() { return [..._getAppState().profiles]; },
    getActiveProfile() { return _activeProfile(); },
    setActiveProfile(profileName) {
      const state = _getAppState();
      if (!state.profiles.includes(profileName)) return false;
      state.activeProfile = profileName;
      _saveAppState(state);
      return true;
    },
    createProfile(profileName) {
      const clean = (profileName || "").trim();
      if (!clean) return { ok: false, error: "Profile name required." };
      const state = _getAppState();
      if (state.profiles.includes(clean)) return { ok: false, error: "Profile already exists." };
      state.profiles.push(clean);
      state.preferencesByProfile[clean] = { ...DEFAULT_PREFS };
      state.activeProfile = clean;
      _saveAppState(state);
      return { ok: true };
    },
    deleteProfile(profileName) {
      if (profileName === DEFAULT_PROFILE) return { ok: false, error: "Default profile cannot be deleted." };
      const state = _getAppState();
      if (!state.profiles.includes(profileName)) return { ok: false, error: "Profile not found." };
      state.profiles = state.profiles.filter(p => p !== profileName);
      delete state.preferencesByProfile[profileName];
      try { localStorage.removeItem(_historyKey(profileName)); } catch (_) {}
      if (state.activeProfile === profileName) state.activeProfile = DEFAULT_PROFILE;
      _saveAppState(state);
      return { ok: true };
    },
    getPreferences() { return _getAppState().preferencesByProfile[_activeProfile()] || { ...DEFAULT_PREFS }; },
    setPreferences(nextPrefs) {
      const state = _getAppState();
      const active = _activeProfile();
      const current = state.preferencesByProfile[active] || { ...DEFAULT_PREFS };
      state.preferencesByProfile[active] = { ...current, ...nextPrefs };
      _saveAppState(state);
    },
    recordAnswer(questionId, isCorrect, domain, difficulty) {
      const data = _load(_activeProfile());
      data[questionId] = { correct: !!isCorrect, domain: domain || "Unknown", difficulty: difficulty || "easy", ts: Date.now() };
      _save(_activeProfile(), data);
    },
    getAnsweredIds() { return new Set(Object.keys(_load(_activeProfile()))); },
    getHistory() { return _load(_activeProfile()); },
    getStats() {
      const entries = Object.values(_load(_activeProfile()));
      const totalAnswered = entries.length;
      const totalCorrect = entries.filter(e => e.correct).length;
      const byDomain = {};
      const byDifficulty = { easy: { answered: 0, correct: 0 }, medium: { answered: 0, correct: 0 }, hard: { answered: 0, correct: 0 } };
      entries.forEach((e) => {
        if (!byDomain[e.domain]) byDomain[e.domain] = { answered: 0, correct: 0 };
        byDomain[e.domain].answered++;
        if (e.correct) byDomain[e.domain].correct++;
        if (byDifficulty[e.difficulty]) {
          byDifficulty[e.difficulty].answered++;
          if (e.correct) byDifficulty[e.difficulty].correct++;
        }
      });
      return { totalAnswered, totalCorrect, byDomain, byDifficulty };
    },
    clearHistory() { try { localStorage.removeItem(_historyKey(_activeProfile())); } catch (_) {} },
  };
})();
