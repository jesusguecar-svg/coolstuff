# Texas General Lines Life, Accident, Health & HMO — Practice Engine

Interactive practice exam engine for the Texas General Lines insurance licensing exam. Built with a schema-first, manifest-driven architecture using validated question batches.

## Web App

Open `web/index.html` in your browser — no server needed.

Or deploy to GitHub Pages:
1. Go to your repo **Settings → Pages**
2. Set source to **Deploy from a branch**
3. Set branch to `main`, folder to `/web`
4. Your app will be live at `https://<username>.github.io/coolstuff/`

### Features
- Choose how many questions (1–250)
- One question at a time with A/B/C/D answer buttons
- Immediate feedback with correct + wrong explanations
- Scored summary with domain breakdown
- Keyboard shortcuts (A/B/C/D or 1/2/3/4 to answer, Enter to continue)
- Mobile-friendly responsive design

## CLI (alternative)

```bash
python app/src/main/cli.py
```

## Project Structure

```
├── app/src/
│   ├── core/
│   │   ├── loader.py          # Manifest-driven question loader
│   │   └── session.py         # Practice session engine
│   ├── components/
│   │   ├── display.py         # Question/result/summary rendering
│   │   └── input_handler.py   # User input handling
│   └── main/
│       └── cli.py             # CLI entry point
├── data/questions_validated/
│   ├── validated_batches_manifest.json
│   ├── question_bank_validated_batch_01..10.json
│   └── validation_report_batch_01..10.json
├── schemas/
│   ├── question_item.schema.json
│   └── question_batch.schema.json
├── web/                           # Static web app
│   ├── index.html
│   ├── css/style.css
│   └── js/ (questions.js, session.js, app.js)
├── scripts/
│   ├── validate_artifacts.py  # Batch/schema validation
│   └── build_questions_js.py  # Bundle JSON → web/js/questions.js
└── docs/
    ├── data-contracts.md
    └── workflow.md
```

## Question Bank

- **250 questions** across 10 validated batches (25 each)
- Covers: Policy Provisions, Agent Duties, Licensing, Regulations, Ethics, and more
- Three difficulty levels: easy, medium, hard
- Each question includes `correct_explanation` and per-option `wrong_explanations`

## Validation

```bash
python scripts/validate_artifacts.py
```

Checks manifest integrity, file presence, schema compliance, duplicate IDs, and explanation model correctness.

## Data Constraints

- Only files in `data/questions_validated/` are used at runtime
- Raw (`*_raw_*`) files are excluded from the pipeline
- Question text is never rewritten; only validated artifacts are loaded
- Explanation model: `correct_explanation` + `wrong_explanations` (no `rationale_by_choice`)

## Docs

- [Data Contracts](docs/data-contracts.md) — Schema and manifest specification
- [Workflow](docs/workflow.md) — Batch validation and ingestion pipeline
