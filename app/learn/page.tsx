import Link from 'next/link';
import { getCurrentUser } from '@/lib/auth';
import { prisma } from '@/lib/prisma';

export default async function LearnPage({ searchParams }: { searchParams: { subject?: string; concept?: string } }) {
  const user = await getCurrentUser();
  const subjects = await prisma.subject.findMany({ orderBy: { nameEn: 'asc' } });
  const concepts = await prisma.concept.findMany({
    where: searchParams.subject ? { subject: { slug: searchParams.subject } } : undefined,
    include: { us: true, ve: true, mapping: true, quizItems: true },
    take: 12
  });
  const selected = searchParams.concept ? concepts.find((c) => c.id === searchParams.concept) : concepts[0];

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold">Duolingo-like learning mode (MVP)</h2>
      {!user && <p className="rounded border border-amber-500/40 bg-amber-500/10 p-2 text-sm">Sign in to track XP, streak, and mastery.</p>}
      <form className="flex gap-2">
        <select name="subject" defaultValue={searchParams.subject || ''} className="rounded bg-slate-800 p-2">
          <option value="">All courses</option>
          {subjects.map((s) => <option key={s.id} value={s.slug}>{s.nameEn}</option>)}
        </select>
        <button className="rounded bg-indigo-600 px-3">Load</button>
      </form>

      <div className="grid gap-3 md:grid-cols-3">
        {concepts.map((concept) => (
          <Link key={concept.id} href={`/learn?subject=${searchParams.subject || ''}&concept=${concept.id}`} className="rounded border border-slate-800 p-3">
            <p className="font-medium">{concept.us?.titleEn}</p>
            <p className="text-sm text-slate-400">{concept.mapping?.equivalenceType}</p>
          </Link>
        ))}
      </div>

      {selected && (
        <section className="space-y-3 rounded border border-slate-800 p-4">
          <h3 className="text-lg font-semibold">Lesson: {selected.us?.titleEn}</h3>
          <p className="text-sm">Exercise 1 (Match): {selected.us?.titleEn} ↔ {selected.ve?.titleEs}</p>
          <p className="text-sm">Exercise 2 (Equivalence type): {selected.mapping?.equivalenceType}</p>
          <p className="text-sm">Exercise 3 (Authority type): case vs statute vs code article</p>
          <p className="text-sm">Exercise 4 (Fill blank): {selected.us?.definitionEn.slice(0, 50)}...</p>
          <form action="/api/progress/lesson" method="post">
            <input type="hidden" name="conceptId" value={selected.id} />
            <button className="rounded bg-emerald-600 px-3 py-2">Complete lesson (+XP)</button>
          </form>
        </section>
      )}
    </div>
  );
}
