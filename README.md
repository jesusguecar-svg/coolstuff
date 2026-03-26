# Texas General Lines Life, Accident, Health & HMO — Practice Engine

Interactive practice exam engine for the Texas General Lines insurance licensing exam. Built with a schema-first, manifest-driven architecture using validated question batches.

## Quick Start

```bash
python app/src/main/cli.py
```

This launches an interactive CLI session:
1. Choose how many questions (1–250)
2. Answer one question at a time (A/B/C/D)
3. See immediate feedback with correct + wrong explanations
4. Get a scored summary with domain breakdown at the end

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
├── scripts/
│   └── validate_artifacts.py  # Batch/schema validation
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
