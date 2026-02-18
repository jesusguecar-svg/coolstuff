import { NextResponse } from 'next/server';
import { getCurrentUser } from '@/lib/auth';
import { prisma } from '@/lib/prisma';

export async function POST(request: Request) {
  const user = await getCurrentUser();
  if (!user) return NextResponse.redirect(new URL('/admin?message=Login+required', request.url));
  const form = await request.formData();
  const payload = String(form.get('payload') || '[]');
  const records = JSON.parse(payload) as Array<any>;

  for (const record of records) {
    const subject = await prisma.subject.findUnique({ where: { slug: record.subjectSlug } });
    if (!subject) continue;
    await prisma.concept.upsert({
      where: { globalId: record.globalId },
      create: {
        globalId: record.globalId,
        slug: record.slug,
        subjectId: subject.id,
        tags: JSON.stringify(record.tags || []),
        us: { create: { titleEn: record.us.title_en, definitionEn: record.us.definition_en, jurisdictionScope: record.us.jurisdiction_scope || 'federal/common' } },
        ve: { create: { titleEs: record.ve.title_es, definitionEs: record.ve.definition_es } },
        mapping: { create: { equivalenceType: record.mapping.equivalence_type, rationale: record.mapping.mapping_rationale || 'Imported', differencesJson: JSON.stringify(record.mapping.key_differences || []), pitfallsJson: JSON.stringify(record.mapping.pitfalls || []) } },
        example: { create: { scenarioEn: record.example?.scenario_text_en || 'Pending', scenarioEs: record.example?.scenario_text_es || 'Pendiente' } }
      },
      update: {}
    });
  }

  return NextResponse.redirect(new URL('/admin?message=Import+completed', request.url));
}
