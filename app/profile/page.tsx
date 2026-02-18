import { redirect } from 'next/navigation';
import { getCurrentUser } from '@/lib/auth';
import { prisma } from '@/lib/prisma';

export default async function ProfilePage() {
  const user = await getCurrentUser();
  if (!user) redirect('/admin?message=Please+login+from+admin+page');

  const [stats, progress] = await Promise.all([
    prisma.userStat.findUnique({ where: { userId: user.id } }),
    prisma.progressConcept.findMany({ where: { userId: user.id }, include: { concept: { include: { us: true, subject: true } } }, orderBy: { nextReviewAt: 'asc' } })
  ]);

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold">Profile</h2>
      <div className="grid gap-3 md:grid-cols-3">
        <div className="rounded border border-slate-800 p-3">XP: {stats?.xp ?? 0}</div>
        <div className="rounded border border-slate-800 p-3">Streak: {stats?.streak ?? 0}</div>
        <div className="rounded border border-slate-800 p-3">Review due: {progress.filter((p) => !p.nextReviewAt || p.nextReviewAt <= new Date()).length}</div>
      </div>
      <h3 className="font-semibold">Weak concepts</h3>
      {progress.filter((p) => p.mastery <= 2).map((p) => (
        <div key={p.id} className="rounded border border-slate-800 p-2 text-sm">{p.concept.us?.titleEn} · mastery {p.mastery} · next {p.nextReviewAt?.toLocaleDateString() || 'today'}</div>
      ))}
    </div>
  );
}
