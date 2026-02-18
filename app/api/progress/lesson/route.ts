import { NextResponse } from 'next/server';
import { getCurrentUser } from '@/lib/auth';
import { dateKey, nextReviewDate } from '@/lib/srs';
import { prisma } from '@/lib/prisma';

export async function POST(request: Request) {
  const user = await getCurrentUser();
  if (!user) return NextResponse.redirect(new URL('/admin?message=Login+required', request.url));
  const form = await request.formData();
  const conceptId = String(form.get('conceptId') || '');
  if (!conceptId) return NextResponse.redirect(new URL('/learn', request.url));

  const existing = await prisma.progressConcept.findUnique({ where: { userId_conceptId: { userId: user.id, conceptId } } });
  const mastery = Math.min(5, (existing?.mastery ?? 0) + 1);
  const now = new Date();
  await prisma.progressConcept.upsert({
    where: { userId_conceptId: { userId: user.id, conceptId } },
    update: { mastery, lastStudiedAt: now, nextReviewAt: nextReviewDate(mastery, existing?.lapseCount ?? 0) },
    create: { userId: user.id, conceptId, mastery, lastStudiedAt: now, nextReviewAt: nextReviewDate(mastery, 0) }
  });

  const stats = await prisma.userStat.upsert({
    where: { userId: user.id },
    create: { userId: user.id, xp: 20, streak: 1, lastStudyDate: now },
    update: {}
  });

  const today = dateKey(now);
  const previous = stats.lastStudyDate ? dateKey(stats.lastStudyDate) : null;
  const yesterday = new Date(now);
  yesterday.setDate(yesterday.getDate() - 1);
  const newStreak = previous === today ? stats.streak : previous === dateKey(yesterday) ? stats.streak + 1 : 1;

  await prisma.userStat.update({ where: { userId: user.id }, data: { xp: { increment: 20 }, streak: newStreak, lastStudyDate: now } });
  return NextResponse.redirect(new URL('/profile', request.url));
}
