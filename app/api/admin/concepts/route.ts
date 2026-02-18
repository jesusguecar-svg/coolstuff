import { NextResponse } from 'next/server';
import { getCurrentUser } from '@/lib/auth';
import { prisma } from '@/lib/prisma';

export async function POST(request: Request) {
  const user = await getCurrentUser();
  if (!user) return NextResponse.redirect(new URL('/admin?message=Login+required', request.url));
  const form = await request.formData();
  const subjectSlug = String(form.get('subjectSlug'));
  const subject = await prisma.subject.findUnique({ where: { slug: subjectSlug } });
  if (!subject) return NextResponse.redirect(new URL('/admin?message=Subject+not+found', request.url));

  await prisma.concept.create({
    data: {
      globalId: String(form.get('globalId')),
      slug: String(form.get('slug')),
      subjectId: subject.id,
      tags: '[]',
      us: { create: { titleEn: String(form.get('titleEn')), definitionEn: String(form.get('definitionEn')), jurisdictionScope: 'federal/common' } },
      ve: { create: { titleEs: String(form.get('titleEs')), definitionEs: String(form.get('definitionEs')) } },
      mapping: { create: { equivalenceType: String(form.get('equivalenceType')) as any, rationale: String(form.get('rationale')), differencesJson: '[]', pitfallsJson: '[]' } },
      example: { create: { scenarioEn: 'Example pending.', scenarioEs: 'Ejemplo pendiente.' } }
    }
  });
  return NextResponse.redirect(new URL('/admin?message=Concept+created', request.url));
}
