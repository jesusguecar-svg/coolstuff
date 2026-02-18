import Link from 'next/link';
import { prisma } from '@/lib/prisma';

export default async function HomePage() {
  const subjects = await prisma.subject.findMany({ orderBy: { nameEn: 'asc' } });
  return (
    <div className="space-y-6">
      <section className="rounded-lg border border-slate-800 bg-slate-900 p-4">
        <h2 className="text-xl font-semibold">Fast comparative legal catalog</h2>
        <p className="mt-2 text-slate-300">Search concept mappings and functional phrase equivalents between U.S. common law and Venezuelan civil law.</p>
        <div className="mt-4 flex gap-3">
          <Link href="/catalog" className="rounded bg-indigo-600 px-4 py-2 text-white">Browse Catalog</Link>
          <Link href="/learn" className="rounded bg-slate-700 px-4 py-2">Start Learning</Link>
        </div>
      </section>
      <section>
        <h3 className="mb-2 text-lg font-semibold">Subjects</h3>
        <div className="grid gap-2 md:grid-cols-2">
          {subjects.map((subject) => (
            <div key={subject.id} className="rounded border border-slate-800 p-3">
              <p className="font-medium">{subject.nameEn}</p>
              <p className="text-sm text-slate-400">{subject.nameEs}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
