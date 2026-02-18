# LexBridge

LexBridge is a full-stack TypeScript web app for comparing legal concepts between U.S. common-law systems and Venezuela's civil-law framework.

## Features

- Concept Comparisons catalog with equivalence labels (Equivalent / Analogous / No direct equivalent).
- Legal Phrases & Equivalents dictionary.
- Jurisdiction-aware authority storage (US court/jurisdiction + Venezuela TSJ metadata fields).
- Learning mode MVP with lesson exercises, XP, streak, mastery, and spaced repetition scheduling.
- Admin panel for content CRUD and JSON import/export.
- Safety/accuracy UX rules:
  - Disclaimer banner: **Educational tool; not legal advice; consult licensed counsel.**
  - Sources warnings when authority records are missing.
  - "Not yet in catalog" behavior for missing concept lookups (catalog detail route returns not found state).

## Stack

- Next.js 14 App Router
- React + TypeScript
- Tailwind CSS
- Prisma ORM
- SQLite (local dev)
- Cookie sessions + bcrypt password auth

## Run

```bash
npm install
npm run prisma:generate
npm run db:push
npm run db:seed
npm run dev
```

Open http://localhost:3000

## Build + Start

```bash
npm run build
npm run start
```

## Admin setup

1. Visit `/admin`.
2. Register with email + password (min 8 chars).
3. First registered user is a normal user by default. To grant admin role manually in SQLite:

```bash
npx prisma studio
```

Set `User.role` to `ADMIN`.

## JSON import format

`POST /api/admin/import` expects a JSON array in textarea payload. Example object:

```json
{
  "globalId": "lexbridge-custom-1",
  "slug": "consideration-vs-causa",
  "subjectSlug": "contracts-obligations",
  "tags": ["contracts", "comparison"],
  "us": {
    "title_en": "Consideration",
    "definition_en": "Bargained-for exchange required in most US contract formation.",
    "jurisdiction_scope": "state common law"
  },
  "ve": {
    "title_es": "Causa",
    "definition_es": "Elemento funcional de la obligación en doctrina civil."
  },
  "mapping": {
    "equivalence_type": "ANALOGOUS",
    "mapping_rationale": "Functional overlap but doctrinal differences.",
    "key_differences": ["..."],
    "pitfalls": ["..."]
  },
  "example": {
    "scenario_text_en": "...",
    "scenario_text_es": "..."
  }
}
```

## Spaced repetition (MVP)

- Mastery increases on lesson completion (0→5 cap).
- Next review date uses a simple SM-2-inspired interval ladder: 1, 2, 4, 7, 14, 30 days.
- Lapses reduce interval via penalty in `lib/srs.ts`.
- Daily streak increments when study occurs on consecutive days; resets otherwise.

## Notes on legal sources

- Seed data intentionally avoids fabricated legal citations.
- Some seeded entries are marked **Sources needed** placeholders to prompt source curation.
