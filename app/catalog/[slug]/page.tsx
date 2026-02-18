import { notFound } from 'next/navigation';
import { prisma } from '@/lib/prisma';

export default async function ConceptDetail({ params }: { params: { slug: string } }) {
  const concept = await prisma.concept.findUnique({
    where: { slug: params.slug },
    include: {
      subject: true,
      us: true,
      ve: true,
      mapping: true,
      example: true,
      flashcards: true,
      quizItems: true,
      sourceLinks: { include: { source: true }, orderBy: { pinToTop: 'desc' } }
    }
  });

  if (!concept) return notFound();

  const usLinks = concept.sourceLinks.filter((item) => item.side === 'US');
  const veLinks = concept.sourceLinks.filter((item) => item.side === 'VE');

  return (
    <div className="space-y-4">
      <div className="rounded border border-slate-800 p-4">
        <p className="text-sm text-slate-400">{concept.subject.nameEn}</p>
        <h2 className="text-2xl font-semibold">{concept.us?.titleEn} ↔ {concept.ve?.titleEs}</h2>
        <span className="mt-2 inline-block rounded bg-indigo-700 px-2 py-1 text-xs">{concept.mapping?.equivalenceType.replaceAll('_', ' ')}</span>
        <p className="mt-2">{concept.mapping?.rationale}</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <section className="rounded border border-slate-800 p-4">
          <h3 className="font-semibold">U.S. concept</h3>
          <p className="mt-1 text-sm text-slate-400">Jurisdiction scope: {concept.us?.jurisdictionScope}</p>
          <p className="mt-2">{concept.us?.definitionEn}</p>
        </section>
        <section className="rounded border border-slate-800 p-4">
          <h3 className="font-semibold">Venezuela concept</h3>
          <p className="mt-2">{concept.ve?.definitionEs}</p>
        </section>
      </div>

      <section className="grid gap-3 md:grid-cols-2">
        <div className="rounded border border-slate-800 p-4">
          <h3 className="font-semibold">Authorities (US)</h3>
          {usLinks.length === 0 ? <p className="mt-2 text-amber-300">Sources missing</p> : usLinks.map((link) => (
            <div key={link.id} className="mt-2 rounded bg-slate-900 p-2 text-sm">
              <p className="font-medium">{link.source.citation}</p>
              <p>{link.summary}</p>
              <p className="text-slate-400">{link.source.court} · {link.source.year ?? 'n/a'} · {link.source.jurisdiction}</p>
              {link.source.url && <a href={link.source.url} target="_blank">Open source</a>}
            </div>
          ))}
        </div>
        <div className="rounded border border-slate-800 p-4">
          <h3 className="font-semibold">Authorities (Venezuela)</h3>
          {veLinks.length === 0 ? <p className="mt-2 text-amber-300">Sources missing</p> : veLinks.map((link) => (
            <div key={link.id} className="mt-2 rounded bg-slate-900 p-2 text-sm">
              <p className="font-medium">{link.source.citation}</p>
              <p>{link.summary}</p>
              <p className="text-slate-400">{link.source.extraJson}</p>
              {link.source.url && <a href={link.source.url} target="_blank">Open source</a>}
            </div>
          ))}
        </div>
      </section>

      <section className="rounded border border-slate-800 p-4">
        <h3 className="font-semibold">Example / Illustration</h3>
        <p className="mt-2">{concept.example?.scenarioEn}</p>
        <p className="mt-2 text-slate-300">{concept.example?.scenarioEs}</p>
      </section>

      <section className="grid gap-3 md:grid-cols-2">
        <div className="rounded border border-slate-800 p-4">
          <h3 className="font-semibold">Differences</h3>
          <ul className="mt-2 list-disc space-y-1 pl-5 text-sm">
            {JSON.parse(concept.mapping?.differencesJson || '[]').map((item: string) => <li key={item}>{item}</li>)}
          </ul>
        </div>
        <div className="rounded border border-slate-800 p-4">
          <h3 className="font-semibold">Pitfalls</h3>
          <ul className="mt-2 list-disc space-y-1 pl-5 text-sm">
            {JSON.parse(concept.mapping?.pitfallsJson || '[]').map((item: string) => <li key={item}>{item}</li>)}
          </ul>
        </div>
      </section>

      <section className="rounded border border-slate-800 p-4">
        <h3 className="font-semibold">Study cards</h3>
        <div className="mt-2 grid gap-2 md:grid-cols-2">{concept.flashcards.map((card) => (
          <div key={card.id} className="rounded bg-slate-900 p-2 text-sm"><p className="font-medium">{card.front}</p><p>{card.back}</p></div>
        ))}</div>
      </section>
    </div>
  );
}
