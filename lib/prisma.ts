import crypto from 'crypto';

type Subject = { id: string; slug: string; nameEn: string; nameEs: string };
type Concept = any;
type Phrase = any;

type DB = {
  subjects: Subject[];
  concepts: Concept[];
  phrases: Phrase[];
  users: any[];
  sessions: any[];
  userStats: any[];
  progress: any[];
  sources: any[];
};

const subjects = [
  ['constitutional-law', 'Constitutional Law', 'Derecho Constitucional'],
  ['contracts-obligations', 'Contracts & Obligations', 'Contratos y Obligaciones'],
  ['torts', 'Torts', 'Responsabilidad Civil Extracontractual'],
  ['property', 'Property', 'Bienes y Derechos Reales'],
  ['civil-procedure', 'Civil Procedure', 'Procedimiento Civil'],
  ['criminal-law', 'Criminal Law', 'Derecho Penal'],
  ['evidence', 'Evidence', 'Derecho Probatorio'],
  ['business-commercial', 'Business & Commercial', 'Mercantil y Societario']
];

const db: DB = (globalThis as any).__lexdb ?? {
  subjects: subjects.map((s) => ({ id: crypto.randomUUID(), slug: s[0], nameEn: s[1], nameEs: s[2] })),
  concepts: Array.from({ length: 12 }).map((_, i) => ({
    id: crypto.randomUUID(),
    globalId: `lexbridge-c-${i + 1}`,
    slug: `concept-${i + 1}`,
    subject: null,
    tags: JSON.stringify(['comparison', 'sources-needed']),
    us: { titleEn: `US Concept ${i + 1}`, definitionEn: `Plain-language U.S. definition for concept ${i + 1}.`, jurisdictionScope: 'federal/common' },
    ve: { titleEs: `Concepto VE ${i + 1}`, definitionEs: `Definición en lenguaje simple para concepto ${i + 1}.` },
    mapping: { equivalenceType: ['EQUIVALENT', 'ANALOGOUS', 'NO_DIRECT_EQUIVALENT'][i % 3], rationale: 'Functional mapping for educational comparison.', differencesJson: JSON.stringify(['Different procedural posture.']), pitfallsJson: JSON.stringify(['Do not assume literal translation.']) },
    example: { scenarioEn: `Scenario EN for concept ${i + 1}.`, scenarioEs: `Escenario ES para concepto ${i + 1}.` },
    flashcards: [{ id: crypto.randomUUID(), front: `Define concept ${i + 1}`, back: 'Answer', lang: 'en' }],
    quizItems: [{ id: crypto.randomUUID(), prompt: 'Identify equivalence type', type: 'MULTIPLE_CHOICE' }],
    sourceLinks: []
  })),
  phrases: Array.from({ length: 30 }).map((_, i) => ({ id: crypto.randomUUID(), phraseEn: `Phrase EN ${i + 1}`, phraseEs: `Frase ES ${i + 1}`, literalTranslation: i % 2 ? null : `Literal ${i + 1}`, explanation: 'Functional equivalent explanation.', contextTagsJson: JSON.stringify(['contracts', 'pleadings']), examples: [{ id: crypto.randomUUID(), sentenceEn: 'Used in filing.', sentenceEs: 'Usado en escrito.' }] })),
  users: [],
  sessions: [],
  userStats: [],
  progress: [],
  sources: []
};
(globalThis as any).__lexdb = db;

db.concepts.forEach((c, i) => { c.subject = db.subjects[i % db.subjects.length]; });

const whereMatch = (obj: any, where: any) => {
  if (!where) return true;
  return Object.entries(where).every(([k, v]: any) => {
    if (k === 'slug' && typeof v === 'string') return obj.slug === v;
    if (k === 'email') return obj.email === v;
    if (k === 'userId') return obj.userId === v;
    return true;
  });
};

export const prisma: any = {
  subject: {
    findMany: async () => [...db.subjects].sort((a, b) => a.nameEn.localeCompare(b.nameEn)),
    findUnique: async ({ where }: any) => db.subjects.find((s) => whereMatch(s, where)) ?? null,
    findUniqueOrThrow: async ({ where }: any) => db.subjects.find((s) => whereMatch(s, where))
  },
  concept: {
    findMany: async ({ where }: any = {}) => db.concepts.filter((c) => (!where?.subject?.slug || c.subject.slug === where.subject.slug)),
    findUnique: async ({ where }: any) => db.concepts.find((c) => c.slug === where.slug) ?? null,
    count: async () => db.concepts.length,
    create: async ({ data }: any) => { const c = { id: crypto.randomUUID(), ...data, subject: db.subjects.find((s) => s.id === data.subjectId), sourceLinks: [], flashcards: [], quizItems: [] }; db.concepts.push(c); return c; },
    upsert: async ({ where, create }: any) => db.concepts.find((c) => c.globalId === where.globalId) ?? (db.concepts.push({ id: crypto.randomUUID(), ...create, subject: db.subjects.find((s) => s.id === create.subjectId), sourceLinks: [], flashcards: [], quizItems: [] }), db.concepts[db.concepts.length - 1])
  },
  phrase: {
    findMany: async () => db.phrases,
    count: async () => db.phrases.length,
    create: async ({ data }: any) => { const p = { id: crypto.randomUUID(), ...data, examples: [] }; db.phrases.push(p); return p; }
  },
  source: { count: async () => db.sources.length },
  user: {
    findUnique: async ({ where }: any) => db.users.find((u) => whereMatch(u, where)) ?? null,
    create: async ({ data }: any) => { const u = { id: crypto.randomUUID(), role: 'USER', createdAt: new Date(), ...data }; db.users.push(u); return u; }
  },
  session: {
    create: async ({ data }: any) => { db.sessions.push({ id: crypto.randomUUID(), createdAt: new Date(), ...data }); },
    findUnique: async ({ where, include }: any) => { const s = db.sessions.find((x) => x.token === where.token); if (!s) return null; return include?.user ? { ...s, user: db.users.find((u) => u.id === s.userId) } : s; },
    deleteMany: async ({ where }: any) => { db.sessions = db.sessions.filter((s) => s.token !== where.token); }
  },
  userStat: {
    create: async ({ data }: any) => { const s = { id: crypto.randomUUID(), ...data, xp: 0, streak: 0 }; db.userStats.push(s); return s; },
    findUnique: async ({ where }: any) => db.userStats.find((s) => s.userId === where.userId) ?? null,
    upsert: async ({ where, create }: any) => db.userStats.find((s) => s.userId === where.userId) ?? (db.userStats.push({ id: crypto.randomUUID(), ...create }), db.userStats[db.userStats.length - 1]),
    update: async ({ where, data }: any) => { const s = db.userStats.find((x) => x.userId === where.userId); if (!s) return null; s.xp = data.xp?.increment ? s.xp + data.xp.increment : data.xp ?? s.xp; s.streak = data.streak ?? s.streak; s.lastStudyDate = data.lastStudyDate ?? s.lastStudyDate; return s; }
  },
  progressConcept: {
    findMany: async ({ where }: any) => db.progress.filter((p) => p.userId === where.userId).map((p) => ({ ...p, concept: db.concepts.find((c) => c.id === p.conceptId) })),
    findUnique: async ({ where }: any) => db.progress.find((p) => p.userId === where.userId_conceptId.userId && p.conceptId === where.userId_conceptId.conceptId) ?? null,
    upsert: async ({ where, create, update }: any) => { const idx = db.progress.findIndex((p) => p.userId === where.userId_conceptId.userId && p.conceptId === where.userId_conceptId.conceptId); if (idx >= 0) { db.progress[idx] = { ...db.progress[idx], ...update }; return db.progress[idx]; } const p = { id: crypto.randomUUID(), lapseCount: 0, ...create }; db.progress.push(p); return p; }
  }
};
