import Link from 'next/link';
import { searchConcepts } from '@/lib/data';
import { prisma } from '@/lib/prisma';

export default async function CatalogPage({ searchParams }: { searchParams: { q?: string; subject?: string; equivalence?: string; jurisdiction?: string } }) {
  const [subjects, concepts] = await Promise.all([
    prisma.subject.findMany({ orderBy: { nameEn: 'asc' } }),
    searchConcepts(searchParams.q, {
      subject: searchParams.subject,
      equivalence: searchParams.equivalence,
      jurisdiction: searchParams.jurisdiction
    })
  ]);

  return (
    <div className="space-y-4">
      <form className="grid gap-2 rounded border border-slate-800 bg-slate-900 p-3 md:grid-cols-4">
        <input name="q" defaultValue={searchParams.q} placeholder="Search concepts, definitions, citations" className="rounded bg-slate-800 p-2" />
        <select name="subject" defaultValue={searchParams.subject || ''} className="rounded bg-slate-800 p-2">
          <option value="">All subjects</option>
          {subjects.map((s) => <option key={s.id} value={s.slug}>{s.nameEn}</option>)}
        </select>
        <select name="equivalence" defaultValue={searchParams.equivalence || ''} className="rounded bg-slate-800 p-2">
          <option value="">Any equivalence</option>
          <option value="EQUIVALENT">Equivalent</option>
          <option value="ANALOGOUS">Analogous</option>
          <option value="NO_DIRECT_EQUIVALENT">No direct equivalent</option>
        </select>
        <input name="jurisdiction" defaultValue={searchParams.jurisdiction} placeholder="Jurisdiction keyword" className="rounded bg-slate-800 p-2" />
        <button className="rounded bg-indigo-600 px-3 py-2 md:col-span-4">Apply filters</button>
      </form>

      <div className="grid gap-3">
        {concepts.length === 0 && (
          <div className="rounded border border-amber-500/40 bg-amber-500/10 p-3">
            <p className="font-medium">Not yet in catalog.</p>
            <p className="text-sm">This concept is not available yet. Please submit it through the admin import workflow.</p>
          </div>
        )}
        {concepts.map((concept) => {
          const usSources = concept.sourceLinks.filter((s) => s.side === 'US').length;
          const veSources = concept.sourceLinks.filter((s) => s.side === 'VE').length;
          return (
            <Link key={concept.id} href={`/catalog/${concept.slug}`} className="rounded border border-slate-800 p-3 hover:border-indigo-400">
              <div className="flex items-center justify-between gap-2">
                <p className="font-semibold">{concept.us?.titleEn} ↔ {concept.ve?.titleEs}</p>
                <span className="rounded bg-slate-800 px-2 py-1 text-xs">{concept.mapping?.equivalenceType.replaceAll('_', ' ')}</span>
              </div>
              <p className="mt-1 text-sm text-slate-400">{concept.subject.nameEn}</p>
              <p className="mt-2 text-sm">US sources: {usSources} · VE sources: {veSources}</p>
              {(usSources === 0 || veSources === 0) && <p className="mt-1 text-sm text-amber-300">Sources missing for one side.</p>}
            </Link>
          );
        })}
      </div>
    </div>
  );
}
