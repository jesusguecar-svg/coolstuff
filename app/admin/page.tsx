import Link from 'next/link';
import { getCurrentUser } from '@/lib/auth';
import { prisma } from '@/lib/prisma';

export default async function AdminPage({ searchParams }: { searchParams: { message?: string } }) {
  const user = await getCurrentUser();
  const [conceptCount, phraseCount, sourceCount] = await Promise.all([
    prisma.concept.count(),
    prisma.phrase.count(),
    prisma.source.count()
  ]);

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold">Admin dashboard</h2>
      {searchParams.message && <p className="rounded border border-amber-500/40 bg-amber-500/10 p-2 text-sm">{searchParams.message}</p>}
      {!user ? (
        <div className="grid gap-3 md:grid-cols-2">
          <form action="/api/auth/login" method="post" className="space-y-2 rounded border border-slate-800 p-3">
            <h3 className="font-semibold">Login</h3>
            <input className="w-full rounded bg-slate-800 p-2" type="email" name="email" placeholder="Email" required />
            <input className="w-full rounded bg-slate-800 p-2" type="password" name="password" placeholder="Password" required />
            <button className="rounded bg-indigo-600 px-3 py-2">Login</button>
          </form>
          <form action="/api/auth/register" method="post" className="space-y-2 rounded border border-slate-800 p-3">
            <h3 className="font-semibold">Register</h3>
            <input className="w-full rounded bg-slate-800 p-2" type="email" name="email" required />
            <input className="w-full rounded bg-slate-800 p-2" type="password" name="password" minLength={8} required />
            <button className="rounded bg-emerald-600 px-3 py-2">Create account</button>
          </form>
        </div>
      ) : (
        <>
          <div className="grid gap-3 md:grid-cols-3">
            <div className="rounded border border-slate-800 p-3">Concepts: {conceptCount}</div>
            <div className="rounded border border-slate-800 p-3">Phrases: {phraseCount}</div>
            <div className="rounded border border-slate-800 p-3">Sources: {sourceCount}</div>
          </div>
          <div className="flex flex-wrap gap-3">
            <Link href="/admin/concepts/new" className="rounded bg-indigo-600 px-3 py-2">Create Concept</Link>
            <Link href="/admin/phrases/new" className="rounded bg-indigo-600 px-3 py-2">Create Phrase</Link>
            <a href="/api/admin/export" className="rounded bg-slate-700 px-3 py-2">Export JSON</a>
          </div>
          <form action="/api/admin/import" method="post" className="space-y-2 rounded border border-slate-800 p-3">
            <h3 className="font-semibold">Import concepts JSON</h3>
            <textarea name="payload" className="h-36 w-full rounded bg-slate-800 p-2" placeholder="Paste JSON array"></textarea>
            <button className="rounded bg-indigo-600 px-3 py-2">Import</button>
          </form>
          <form action="/api/auth/logout" method="post"><button className="rounded bg-rose-700 px-3 py-2">Logout</button></form>
        </>
      )}
    </div>
  );
}
