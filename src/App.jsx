import React, { useEffect, useMemo, useState } from 'react';
import { Scale, ShieldCheck, BookOpenCheck, Landmark, ArrowRight, CheckCircle2, Sparkles } from 'lucide-react';
import { initializeApp } from 'firebase/app';
import {
  getAuth,
  onAuthStateChanged,
  signInAnonymously,
  signInWithCustomToken,
} from 'firebase/auth';
import {
  doc,
  getDoc,
  getFirestore,
  onSnapshot,
  serverTimestamp,
  setDoc,
} from 'firebase/firestore';

const STARTER_MODULES = [
  {
    id: 'self-defense',
    domain: 'Criminal Law',
    title: 'Self-Defense',
    estimatedMinutes: 8,
    difficulty: 'Beginner',
    relationType: 'Analogous',
    civilSide: {
      term: 'Legítima defensa',
      definition:
        'Eximente de responsabilidad cuando se repele una agresión ilegítima con necesidad racional del medio empleado y sin provocación suficiente.',
      citation: 'Código Penal venezolano (CP), Art. 65.',
    },
    usSide: {
      term: 'Self-Defense',
      definition:
        'A justified use of force when a defendant reasonably believes it is necessary to prevent imminent unlawful force.',
      citation: 'Model Penal Code § 3.04; Restatement (Second) of Torts § 63 (defensive force principles).',
      landmarkCase: 'Brown v. United States, 256 U.S. 335 (1921).',
    },
    mbeTip:
      'On MBE fact patterns, isolate imminence and proportionality first; deadly force usually requires threat of death/serious bodily harm.',
  },
  {
    id: 'negligence',
    domain: 'Torts',
    title: 'Negligence',
    estimatedMinutes: 12,
    difficulty: 'Intermediate',
    relationType: 'Direct Equivalent',
    civilSide: {
      term: 'Responsabilidad civil por culpa',
      definition:
        'Obligación de reparar daños causados por imprudencia, negligencia o impericia al infringir el deber general de no dañar.',
      citation: 'Código Civil venezolano (CC), Art. 1.185.',
    },
    usSide: {
      term: 'Negligence',
      definition:
        'Failure to exercise reasonable care under the circumstances, causing compensable harm.',
      citation: 'Restatement (Second) of Torts § 282.',
      landmarkCase: 'Palsgraf v. Long Island Railroad Co., 248 N.Y. 339 (1928).',
    },
    mbeTip:
      'Duty and proximate cause are frequent traps; if foreseeability is weak, analyze whether the plaintiff is outside the risk zone.',
  },
  {
    id: 'breach-of-contract',
    domain: 'Contracts',
    title: 'Breach of Contract',
    estimatedMinutes: 10,
    difficulty: 'Beginner',
    relationType: 'Direct Equivalent',
    civilSide: {
      term: 'Incumplimiento contractual',
      definition:
        'Cuando una parte no ejecuta la prestación debida en tiempo, modo o lugar, generando responsabilidad patrimonial.',
      citation: 'Código Civil venezolano (CC), Arts. 1.264 y 1.271.',
    },
    usSide: {
      term: 'Breach of Contract',
      definition:
        'Unjustified failure to perform a contractual duty when performance is due.',
      citation: 'Restatement (Second) of Contracts § 235; UCC § 2-601.',
      landmarkCase: 'Jacob & Youngs v. Kent, 230 N.Y. 239 (1921).',
    },
    mbeTip:
      'Classify breach as material or minor before choosing remedy; substantial performance often limits rescission.',
  },
];

const LESSON_STEPS = ['Civil Law View', 'Common Law View', 'Comparative Synthesis'];

function getFirebaseSettings() {
  let parsed = {};

  try {
    if (typeof __firebase_config !== 'undefined' && __firebase_config) {
      parsed = JSON.parse(__firebase_config);
    }
  } catch (error) {
    console.error('Invalid Firebase config payload. Falling back to env config.', error);
  }

  return {
    appId:
      (typeof __app_id !== 'undefined' && __app_id) ||
      parsed.appId ||
      import.meta.env.VITE_FIREBASE_APP_ID ||
      'lexbridge-pro',
    firebaseConfig: {
      apiKey: parsed.apiKey || import.meta.env.VITE_FIREBASE_API_KEY || '',
      authDomain: parsed.authDomain || import.meta.env.VITE_FIREBASE_AUTH_DOMAIN || '',
      projectId: parsed.projectId || import.meta.env.VITE_FIREBASE_PROJECT_ID || '',
      storageBucket: parsed.storageBucket || import.meta.env.VITE_FIREBASE_STORAGE_BUCKET || '',
      messagingSenderId:
        parsed.messagingSenderId || import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID || '',
      appId: parsed.appId || import.meta.env.VITE_FIREBASE_APP_ID || 'lexbridge-pro',
    },
  };
}

const appTheme = 'min-h-screen bg-slate-900 text-slate-100 selection:bg-indigo-600/40';

export default function App() {
  const [booting, setBooting] = useState(true);
  const [authReady, setAuthReady] = useState(false);
  const [user, setUser] = useState(null);
  const [profile, setProfile] = useState(null);
  const [demoMode, setDemoMode] = useState(false);
  const [modules] = useState(STARTER_MODULES);
  const [activeLesson, setActiveLesson] = useState(null);
  const [lessonStep, setLessonStep] = useState(0);
  const [searchTerm, setSearchTerm] = useState('');

  const firebaseSettings = useMemo(() => getFirebaseSettings(), []);

  useEffect(() => {
    let unsubAuth = () => {};

    const hasConfig =
      firebaseSettings.firebaseConfig.apiKey &&
      firebaseSettings.firebaseConfig.projectId &&
      firebaseSettings.firebaseConfig.appId;

    if (!hasConfig) {
      setDemoMode(true);
      setUser({ uid: 'demo-user' });
      setProfile({
        displayName: 'Comparative Scholar (Demo)',
        xp: 0,
        completedLessons: [],
      });
      setAuthReady(true);
      setBooting(false);
      return () => {};
    }

    let auth;

    try {
      const firebaseApp = initializeApp(firebaseSettings.firebaseConfig);
      auth = getAuth(firebaseApp);
      getFirestore(firebaseApp);
    } catch (error) {
      console.error('Firebase initialization failed. Switching to demo mode.', error);
      setDemoMode(true);
      setUser({ uid: 'demo-user' });
      setProfile({
        displayName: 'Comparative Scholar (Demo)',
        xp: 0,
        completedLessons: [],
      });
      setAuthReady(true);
      setBooting(false);
      return () => {};
    }

    const runAuth = async () => {
      try {
        if (typeof __initial_auth_token !== 'undefined' && __initial_auth_token) {
          await signInWithCustomToken(auth, __initial_auth_token);
        } else {
          await signInAnonymously(auth);
        }
      } catch (error) {
        console.error('Authentication failed. Switching to demo mode.', error);
        setDemoMode(true);
        setUser({ uid: 'demo-user' });
        setProfile({
          displayName: 'Comparative Scholar (Demo)',
          xp: 0,
          completedLessons: [],
        });
        setAuthReady(true);
        setBooting(false);
      }
    };

    runAuth();

    unsubAuth = onAuthStateChanged(auth, (signedInUser) => {
      setUser(signedInUser);
      setAuthReady(true);
    });

    return () => {
      unsubAuth();
    };
  }, [firebaseSettings]);

  useEffect(() => {
    if (!authReady || !user || demoMode) {
      return;
    }

    const appId = firebaseSettings.appId;
    const db = getFirestore();
    const profileRef = doc(db, `artifacts/${appId}/users/${user.uid}/profile/data`);
    const curriculumRef = doc(db, `artifacts/${appId}/users/${user.uid}/curriculum/data`);

    const ensureProfile = async () => {
      const existing = await getDoc(profileRef);
      if (!existing.exists()) {
        await setDoc(profileRef, {
          displayName: 'Comparative Scholar',
          xp: 0,
          completedLessons: [],
          createdAt: serverTimestamp(),
          updatedAt: serverTimestamp(),
        });
      }

      const curriculum = await getDoc(curriculumRef);
      if (!curriculum.exists()) {
        await setDoc(curriculumRef, {
          modules: STARTER_MODULES,
          seededAt: serverTimestamp(),
        });
      }

      setBooting(false);
    };

    ensureProfile().catch((error) => {
      console.error('Failed to initialize user profile.', error);
      setBooting(false);
    });

    const unsubProfile = onSnapshot(profileRef, (snap) => {
      if (snap.exists()) {
        setProfile(snap.data());
      }
    });

    return () => {
      unsubProfile();
    };
  }, [authReady, demoMode, firebaseSettings.appId, user]);

  const completeLesson = async () => {
    if (!user || !activeLesson) {
      return;
    }

    if (demoMode) {
      const alreadyCompleted = profile?.completedLessons?.includes(activeLesson.id);
      const nextCompleted = alreadyCompleted
        ? profile?.completedLessons || []
        : [...(profile?.completedLessons || []), activeLesson.id];

      setProfile((prev) => ({
        ...(prev || {}),
        xp: (prev?.xp || 0) + (alreadyCompleted ? 0 : 25),
        completedLessons: nextCompleted,
      }));

      setActiveLesson(null);
      setLessonStep(0);
      return;
    }

    const db = getFirestore();
    const profileRef = doc(db, `artifacts/${firebaseSettings.appId}/users/${user.uid}/profile/data`);
    const alreadyCompleted = profile?.completedLessons?.includes(activeLesson.id);

    const nextCompleted = alreadyCompleted
      ? profile?.completedLessons || []
      : [...(profile?.completedLessons || []), activeLesson.id];

    await setDoc(
      profileRef,
      {
        xp: (profile?.xp || 0) + (alreadyCompleted ? 0 : 25),
        completedLessons: nextCompleted,
        updatedAt: serverTimestamp(),
      },
      { merge: true }
    );

    setActiveLesson(null);
    setLessonStep(0);
  };

  const openLesson = (module) => {
    setActiveLesson(module);
    setLessonStep(0);
  };

  const filteredModules = useMemo(() => {
    const normalized = searchTerm.trim().toLowerCase();

    if (!normalized) {
      return modules;
    }

    return modules.filter((module) => {
      const haystack = `${module.domain} ${module.title} ${module.relationType} ${module.mbeTip}`.toLowerCase();
      return haystack.includes(normalized);
    });
  }, [modules, searchTerm]);

  const completedCount = profile?.completedLessons?.length || 0;
  const completionProgress = Math.round((completedCount / modules.length) * 100);
  const nextSuggestedLesson = modules.find((module) => !profile?.completedLessons?.includes(module.id));

  if (!authReady || booting) {
    return (
      <main className={`${appTheme} flex items-center justify-center p-8`}>
        <section className="w-full max-w-xl rounded-2xl border border-slate-700 bg-slate-800/60 p-8 text-center shadow-2xl backdrop-blur animate-in fade-in duration-500">
          <Sparkles className="mx-auto mb-4 h-10 w-10 text-indigo-400" />
          <h1 className="text-3xl font-bold tracking-tight text-white">LexBridge Pro</h1>
          <p className="mt-3 text-slate-300">
            Initializing comparative law workspace and synchronizing your profile...
          </p>
        </section>
      </main>
    );
  }

  return (
    <main className={`${appTheme} p-6 md:p-10`}>
      <div className="mx-auto max-w-6xl space-y-8">
        <header className="rounded-2xl border border-slate-700 bg-slate-800/70 p-6 shadow-xl animate-in slide-in-from-top-2 duration-500">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <p className="text-sm uppercase tracking-[0.2em] text-indigo-300">Built for bar exam migrants</p>
              <h1 className="mt-1 text-3xl font-semibold text-white">Bridge Civil Law to U.S. MBE in 10 minutes a day</h1>
              {demoMode && (
                <p className="mt-2 text-xs text-amber-300">
                  Demo mode is active (Firebase unavailable). Interactions are local-only.
                </p>
              )}
            </div>
            <div className="rounded-xl border border-indigo-500/40 bg-indigo-600/20 px-4 py-2">
              <p className="text-sm text-indigo-200">Scholar XP</p>
              <p className="text-2xl font-bold text-white">{profile?.xp ?? 0}</p>
            </div>
          </div>

          <div className="mt-5 grid gap-4 rounded-xl border border-slate-600/70 bg-slate-900/40 p-4 md:grid-cols-[1fr_auto] md:items-center">
            <div>
              <p className="text-sm text-slate-200">Progress: {completedCount}/{modules.length} lessons completed ({completionProgress}%)</p>
              <div className="mt-2 h-2 rounded-full bg-slate-700">
                <div className="h-2 rounded-full bg-emerald-500 transition-all" style={{ width: `${completionProgress}%` }} />
              </div>
              <p className="mt-2 text-xs text-slate-400">
                {nextSuggestedLesson
                  ? `Recommended next lesson: ${nextSuggestedLesson.title}`
                  : 'Great work — you completed the full starter track.'}
              </p>
            </div>
            {nextSuggestedLesson && (
              <button
                type="button"
                onClick={() => openLesson(nextSuggestedLesson)}
                className="inline-flex items-center gap-2 rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-500"
              >
                Continue learning <ArrowRight className="h-4 w-4" />
              </button>
            )}
          </div>
        </header>

        <section className="grid gap-4 md:grid-cols-[1fr_auto] md:items-center">
          <label className="text-sm text-slate-300">
            Find a topic fast
            <input
              type="search"
              placeholder="Search by concept, domain, or exam tip..."
              value={searchTerm}
              onChange={(event) => setSearchTerm(event.target.value)}
              className="mt-2 w-full rounded-lg border border-slate-600 bg-slate-800 px-3 py-2 text-sm text-white placeholder:text-slate-400 focus:border-indigo-400 focus:outline-none"
            />
          </label>
          <p className="text-xs text-slate-400">Each lesson has 3 steps and takes ~8-12 minutes.</p>
        </section>

        <section className="grid gap-4 md:grid-cols-3">
          {filteredModules.map((module) => {
            const complete = profile?.completedLessons?.includes(module.id);
            return (
              <article
                key={module.id}
                className="rounded-2xl border border-slate-700 bg-slate-800/70 p-5 shadow-lg transition hover:border-indigo-500/60 hover:bg-slate-800 animate-in fade-in zoom-in-95 duration-500"
              >
                <div className="flex items-center justify-between">
                  <span className="rounded-md border border-slate-600 px-2 py-1 text-xs text-slate-300">{module.domain}</span>
                  {complete ? (
                    <CheckCircle2 className="h-5 w-5 text-emerald-400" />
                  ) : (
                    <BookOpenCheck className="h-5 w-5 text-indigo-300" />
                  )}
                </div>
                <h2 className="mt-3 text-xl font-semibold text-white">{module.title}</h2>
                <p className="mt-1 text-sm text-slate-300">Relation: {module.relationType}</p>
                <p className="mt-1 text-xs text-slate-400">
                  {module.difficulty} · {module.estimatedMinutes} min
                </p>
                <p className="mt-3 text-sm text-slate-300 line-clamp-2">MBE Tip: {module.mbeTip}</p>
                <button
                  type="button"
                  onClick={() => openLesson(module)}
                  className="mt-4 inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-indigo-500"
                >
                  Start 3-Step Lesson <ArrowRight className="h-4 w-4" />
                </button>
              </article>
            );
          })}

          {filteredModules.length === 0 && (
            <article className="rounded-2xl border border-dashed border-slate-600 bg-slate-800/40 p-6 text-sm text-slate-300 md:col-span-3">
              No results for <strong>{searchTerm}</strong>. Try a broader keyword like "defense" or "contracts".
            </article>
          )}
        </section>
      </div>

      {activeLesson && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 p-4 animate-in fade-in duration-300">
          <div className="w-full max-w-3xl rounded-2xl border border-slate-700 bg-slate-900 p-6 shadow-2xl animate-in zoom-in-95 duration-300">
            <div className="mb-4 flex items-center justify-between">
              <h3 className="text-2xl font-semibold text-white">{activeLesson.title}</h3>
              <button
                type="button"
                className="rounded-md border border-slate-600 px-3 py-1 text-slate-300 hover:text-white"
                onClick={() => setActiveLesson(null)}
              >
                Close
              </button>
            </div>

            <div className="mb-5">
              <div className="mb-2 flex items-center justify-between text-sm text-slate-300">
                <span>{LESSON_STEPS[lessonStep]}</span>
                <span>
                  Step {lessonStep + 1}/{LESSON_STEPS.length}
                </span>
              </div>
              <div className="h-2 rounded-full bg-slate-700">
                <div
                  className="h-2 rounded-full bg-indigo-600 transition-all"
                  style={{ width: `${((lessonStep + 1) / LESSON_STEPS.length) * 100}%` }}
                />
              </div>
            </div>

            <section className="min-h-56 rounded-xl border border-slate-700 bg-slate-800/70 p-4 text-sm leading-6 text-slate-200">
              {lessonStep === 0 && (
                <div className="space-y-2 animate-in fade-in duration-300">
                  <p className="flex items-center gap-2 text-indigo-200">
                    <ShieldCheck className="h-4 w-4" /> Civil Law View
                  </p>
                  <p>
                    <strong>Término:</strong> {activeLesson.civilSide.term}
                  </p>
                  <p>
                    <strong>Definición:</strong> {activeLesson.civilSide.definition}
                  </p>
                  <p>
                    <strong>Cita:</strong> {activeLesson.civilSide.citation}
                  </p>
                </div>
              )}

              {lessonStep === 1 && (
                <div className="space-y-2 animate-in fade-in duration-300">
                  <p className="flex items-center gap-2 text-indigo-200">
                    <Scale className="h-4 w-4" /> Common Law View
                  </p>
                  <p>
                    <strong>Term:</strong> {activeLesson.usSide.term}
                  </p>
                  <p>
                    <strong>Definition:</strong> {activeLesson.usSide.definition}
                  </p>
                  <p>
                    <strong>Citation:</strong> {activeLesson.usSide.citation}
                  </p>
                  <p>
                    <strong>Landmark Case:</strong> {activeLesson.usSide.landmarkCase}
                  </p>
                </div>
              )}

              {lessonStep === 2 && (
                <div className="space-y-2 animate-in fade-in duration-300">
                  <p className="flex items-center gap-2 text-indigo-200">
                    <Landmark className="h-4 w-4" /> Comparative Synthesis
                  </p>
                  <p>
                    <strong>Relation Type:</strong> {activeLesson.relationType}
                  </p>
                  <p>
                    <strong>Exam Strategy:</strong> {activeLesson.mbeTip}
                  </p>
                  <p>
                    Translate triggers: map civil-code elements into US issue-spotting buckets (duty,
                    breach, causation, defense) to avoid false equivalence.
                  </p>
                </div>
              )}
            </section>

            <div className="mt-6 flex justify-between">
              <button
                type="button"
                onClick={() => setLessonStep((s) => Math.max(0, s - 1))}
                disabled={lessonStep === 0}
                className="rounded-lg border border-slate-600 px-4 py-2 text-sm text-slate-200 disabled:cursor-not-allowed disabled:opacity-40"
              >
                Back
              </button>

              {lessonStep < LESSON_STEPS.length - 1 ? (
                <button
                  type="button"
                  onClick={() => setLessonStep((s) => Math.min(LESSON_STEPS.length - 1, s + 1))}
                  className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-500"
                >
                  Next
                </button>
              ) : (
                <button
                  type="button"
                  onClick={completeLesson}
                  className="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-500"
                >
                  Complete Lesson (+25 XP)
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
