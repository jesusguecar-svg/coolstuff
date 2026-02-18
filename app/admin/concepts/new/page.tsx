import { prisma } from '@/lib/prisma';

export default async function NewConceptPage() {
  const subjects = await prisma.subject.findMany({ orderBy: { nameEn: 'asc' } });
  return (
    <form action="/api/admin/concepts" method="post" className="space-y-2 rounded border border-slate-800 p-4">
      <h2 className="text-xl font-semibold">Create concept comparison</h2>
      <select name="subjectSlug" className="w-full rounded bg-slate-800 p-2">{subjects.map((s) => <option key={s.id} value={s.slug}>{s.nameEn}</option>)}</select>
      <input name="globalId" placeholder="Global concept id" className="w-full rounded bg-slate-800 p-2" required />
      <input name="slug" placeholder="Slug" className="w-full rounded bg-slate-800 p-2" required />
      <input name="titleEn" placeholder="US title" className="w-full rounded bg-slate-800 p-2" required />
      <input name="titleEs" placeholder="VE title" className="w-full rounded bg-slate-800 p-2" required />
      <textarea name="definitionEn" placeholder="US definition" className="h-20 w-full rounded bg-slate-800 p-2" required />
      <textarea name="definitionEs" placeholder="VE definition" className="h-20 w-full rounded bg-slate-800 p-2" required />
      <select name="equivalenceType" className="w-full rounded bg-slate-800 p-2">
        <option>EQUIVALENT</option><option>ANALOGOUS</option><option>NO_DIRECT_EQUIVALENT</option>
      </select>
      <textarea name="rationale" placeholder="Mapping rationale" className="h-20 w-full rounded bg-slate-800 p-2" required />
      <button className="rounded bg-indigo-600 px-3 py-2">Create</button>
    </form>
  );
}
