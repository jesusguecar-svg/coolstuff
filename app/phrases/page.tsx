import { prisma } from '@/lib/prisma';

export default async function PhrasesPage({ searchParams }: { searchParams: { q?: string } }) {
  const q = searchParams.q;
  const phrases = await prisma.phrase.findMany({
    where: q
      ? {
          OR: [
            { phraseEn: { contains: q, mode: 'insensitive' } },
            { phraseEs: { contains: q, mode: 'insensitive' } },
            { explanation: { contains: q, mode: 'insensitive' } }
          ]
        }
      : undefined,
    include: { examples: true },
    orderBy: { phraseEn: 'asc' }
  });

  return (
    <div className="space-y-4">
      <form><input name="q" defaultValue={q} placeholder="Search legal phrase" className="w-full rounded bg-slate-800 p-2" /></form>
      {phrases.map((phrase) => (
        <article key={phrase.id} className="rounded border border-slate-800 p-3">
          <h3 className="font-semibold">{phrase.phraseEn} ↔ {phrase.phraseEs}</h3>
          {phrase.literalTranslation && <p className="text-sm text-slate-400">Literal: {phrase.literalTranslation}</p>}
          <p className="mt-2 text-sm">{phrase.explanation}</p>
          <p className="mt-2 text-xs text-slate-400">Tags: {JSON.parse(phrase.contextTagsJson).join(', ')}</p>
          {phrase.examples[0] && <p className="mt-2 text-sm">Ex: {phrase.examples[0].sentenceEn} / {phrase.examples[0].sentenceEs}</p>}
        </article>
      ))}
    </div>
  );
}
