import { NextResponse } from 'next/server';
import { createSession, hashPassword } from '@/lib/auth';
import { prisma } from '@/lib/prisma';

export async function POST(request: Request) {
  const form = await request.formData();
  const email = String(form.get('email') || '').trim().toLowerCase();
  const password = String(form.get('password') || '');
  if (!email || password.length < 8) return NextResponse.redirect(new URL('/admin?message=Invalid+credentials', request.url));

  const existing = await prisma.user.findUnique({ where: { email } });
  if (existing) return NextResponse.redirect(new URL('/admin?message=Email+already+registered', request.url));

  const user = await prisma.user.create({ data: { email, passwordHash: await hashPassword(password) } });
  await prisma.userStat.create({ data: { userId: user.id } });
  await createSession(user.id);
  return NextResponse.redirect(new URL('/admin', request.url));
}
