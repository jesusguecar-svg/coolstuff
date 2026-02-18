import { NextResponse } from 'next/server';
import { getCurrentUser } from '@/lib/auth';
import { conceptInclude } from '@/lib/data';
import { prisma } from '@/lib/prisma';

export async function GET(request: Request) {
  const user = await getCurrentUser();
  if (!user) return NextResponse.redirect(new URL('/admin?message=Login+required', request.url));
  const concepts = await prisma.concept.findMany({ include: conceptInclude });
  return NextResponse.json(concepts);
}
