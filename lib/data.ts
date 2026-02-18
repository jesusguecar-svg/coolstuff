import { prisma } from './prisma';

export const conceptInclude = {
  subject: true,
  us: true,
  ve: true,
  mapping: true,
  example: true,
  flashcards: true,
  quizItems: true,
  sourceLinks: { include: { source: true }, orderBy: [{ pinToTop: 'desc' as const }] }
};

export async function searchConcepts(query?: string, filters?: { subject?: string; equivalence?: string; jurisdiction?: string }) {
  const where: any = {
    ...(filters?.subject ? { subject: { slug: filters.subject } } : {}),
    ...(filters?.equivalence ? { mapping: { equivalenceType: filters.equivalence } } : {}),
    ...(query
      ? {
          OR: [
            { us: { titleEn: { contains: query } } },
            { ve: { titleEs: { contains: query } } },
            { tags: { contains: query } },
            { us: { definitionEn: { contains: query } } },
            { ve: { definitionEs: { contains: query } } },
            { sourceLinks: { some: { source: { citation: { contains: query } } } } }
          ]
        }
      : {})
  };

  const concepts = await prisma.concept.findMany({
    where,
    include: conceptInclude,
    orderBy: [{ updatedAt: 'desc' }]
  });

  if (!filters?.jurisdiction) return concepts;
  return concepts.filter((concept: any) => concept.sourceLinks.some((link: any) => (link.source.jurisdiction || '').toLowerCase().includes(filters.jurisdiction!.toLowerCase())));
}
