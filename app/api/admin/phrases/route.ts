import { NextResponse } from 'next/server';
import { getCurrentUser } from '@/lib/auth';
import { prisma } from '@/lib/prisma';

export async function POST(request: Request) {
  const user = await getCurrentUser();
  if (!user) return NextResponse.redirect(new URL('/admin?message=Login+required', request.url));
  const form = await request.formData();
  await prisma.phrase.create({
    data: {
      phraseEn: String(form.get('phraseEn')),
      phraseEs: String(form.get('phraseEs')),
      literalTranslation: String(form.get('literalTranslation') || ''),
      explanation: String(form.get('explanation')),
      contextTagsJson: JSON.stringify(String(form.get('tags')).split(',').map((tag) => tag.trim())),
      authorityRefs: null
    }
  });
  return NextResponse.redirect(new URL('/admin?message=Phrase+created', request.url));
}
