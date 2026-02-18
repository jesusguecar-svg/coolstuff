import { EquivalenceType, PrismaClient, QuizType, SourceType } from '@prisma/client';

const prisma = new PrismaClient();

const subjects = [
  ['constitutional-law', 'Constitutional Law', 'Derecho Constitucional'],
  ['contracts-obligations', 'Contracts & Obligations', 'Contratos y Obligaciones'],
  ['torts', 'Torts', 'Responsabilidad Civil Extracontractual'],
  ['property', 'Property', 'Bienes y Derechos Reales'],
  ['civil-procedure', 'Civil Procedure', 'Procedimiento Civil'],
  ['criminal-law', 'Criminal Law', 'Derecho Penal'],
  ['evidence', 'Evidence', 'Derecho Probatorio'],
  ['business-commercial', 'Business & Commercial', 'Mercantil y Societario']
] as const;

const conceptSeeds = Array.from({ length: 12 }).map((_, i) => ({
  globalId: `lexbridge-c-${i + 1}`,
  slug: `concept-${i + 1}`,
  subjectSlug: subjects[i % subjects.length][0],
  tags: ['comparison', 'sources-needed'],
  usTitle: `US Concept ${i + 1}`,
  usDefinition: `Plain-language U.S. definition for concept ${i + 1}.`,
  veTitle: `Concepto VE ${i + 1}`,
  veDefinition: `Definición en lenguaje simple para concepto ${i + 1}.`,
  equivalenceType: [EquivalenceType.EQUIVALENT, EquivalenceType.ANALOGOUS, EquivalenceType.NO_DIRECT_EQUIVALENT][i % 3],
  rationale: 'Functional mapping for educational comparison. Validate with counsel and official sources.',
  differences: ['Different procedural posture.', 'Terminology may diverge from literal translation.'],
  pitfalls: ['Assuming same burden of proof.', 'Ignoring jurisdiction-specific exceptions.'],
  scenarioEn: `Scenario EN for concept ${i + 1}.`,
  scenarioEs: `Escenario ES para concepto ${i + 1}.`
}));

const phrases = Array.from({ length: 30 }).map((_, i) => ({
  phraseEn: `Phrase EN ${i + 1}`,
  phraseEs: `Frase ES ${i + 1}`,
  literalTranslation: i % 2 === 0 ? `Literal ${i + 1}` : null,
  explanation: 'Functional equivalent used in comparative legal writing; not always literal.',
  contextTagsJson: JSON.stringify(['contracts', 'pleadings', i % 2 === 0 ? 'criminal' : 'civil'])
}));

async function main() {
  await prisma.conceptSourceLink.deleteMany();
  await prisma.flashcard.deleteMany();
  await prisma.quizItem.deleteMany();
  await prisma.example.deleteMany();
  await prisma.mapping.deleteMany();
  await prisma.conceptUS.deleteMany();
  await prisma.conceptVE.deleteMany();
  await prisma.concept.deleteMany();
  await prisma.phraseExample.deleteMany();
  await prisma.phrase.deleteMany();
  await prisma.source.deleteMany();
  await prisma.subject.deleteMany();

  for (const [slug, nameEn, nameEs] of subjects) {
    await prisma.subject.create({ data: { slug, nameEn, nameEs } });
  }

  for (const c of conceptSeeds) {
    const subject = await prisma.subject.findUniqueOrThrow({ where: { slug: c.subjectSlug } });
    const concept = await prisma.concept.create({
      data: {
        globalId: c.globalId,
        slug: c.slug,
        subjectId: subject.id,
        tags: JSON.stringify(c.tags),
        us: { create: { titleEn: c.usTitle, definitionEn: c.usDefinition, jurisdictionScope: 'federal/common' } },
        ve: { create: { titleEs: c.veTitle, definitionEs: c.veDefinition } },
        mapping: { create: { equivalenceType: c.equivalenceType, rationale: c.rationale, differencesJson: JSON.stringify(c.differences), pitfallsJson: JSON.stringify(c.pitfalls) } },
        example: { create: { scenarioEn: c.scenarioEn, scenarioEs: c.scenarioEs } }
      }
    });

    await prisma.flashcard.createMany({
      data: [
        { conceptId: concept.id, front: `Define ${c.usTitle}`, back: c.usDefinition, lang: 'en' },
        { conceptId: concept.id, front: `Define ${c.veTitle}`, back: c.veDefinition, lang: 'es' }
      ]
    });

    await prisma.quizItem.createMany({
      data: [
        { conceptId: concept.id, type: QuizType.MULTIPLE_CHOICE, prompt: `Choose equivalence type for ${c.usTitle}`, optionsJson: JSON.stringify(['Equivalent', 'Analogous', 'No direct equivalent']), answerJson: JSON.stringify(c.equivalenceType), explanation: 'Pick based on legal function overlap.', difficulty: 1 },
        { conceptId: concept.id, type: QuizType.TRUE_FALSE, prompt: `${c.usTitle} always translates literally into Spanish.`, optionsJson: JSON.stringify(['True', 'False']), answerJson: JSON.stringify('False'), explanation: 'Legal terms can be functional equivalents.', difficulty: 1 },
        { conceptId: concept.id, type: QuizType.FILL_BLANK, prompt: `Fill key term in definition of ${c.usTitle}.`, optionsJson: JSON.stringify([]), answerJson: JSON.stringify('jurisdiction'), explanation: 'Jurisdiction sensitivity is required.', difficulty: 2 },
        { conceptId: concept.id, type: QuizType.ISSUE_SPOTTER, prompt: `Mini-hypo for ${c.usTitle}`, optionsJson: JSON.stringify(['A', 'B', 'C']), answerJson: JSON.stringify('A'), explanation: 'Best mapping based on authority hierarchy.', difficulty: 3 }
      ]
    });

    if (Number(c.globalId.split('-').pop()) % 2 === 0) {
      const usSource = await prisma.source.create({
        data: {
          sourceType: SourceType.OTHER,
          title: 'Sources needed',
          citation: 'Sources needed — no authority entered yet.',
          extraJson: JSON.stringify({ note: 'Do not rely without verifying' }),
          jurisdiction: 'Unspecified US'
        }
      });
      await prisma.conceptSourceLink.create({ data: { conceptId: concept.id, side: 'US', sourceId: usSource.id, summary: 'Placeholder indicating authoritative source must be added.' } });
    }
  }

  for (const phrase of phrases) {
    const created = await prisma.phrase.create({ data: { ...phrase, authorityRefs: null } });
    await prisma.phraseExample.create({ data: { phraseId: created.id, sentenceEn: `${phrase.phraseEn} appears in a filing.`, sentenceEs: `${phrase.phraseEs} aparece en un escrito.` } });
  }
}

main().finally(() => prisma.$disconnect());
