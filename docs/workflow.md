# Workflow: Batch Validation & Ingestion

## Pipeline Overview

```
Raw questions → Validation review → Validated batch files → Manifest → Loader → Runtime
```

## 1. Validated Batch Files

Each batch file (`question_bank_validated_batch_NN.json`) contains 25 questions that have been through validation review. Validation reports (`validation_report_batch_NN.json`) document corrections and dispositions.

## 2. Filename Normalization

Files may arrive with variant names (e.g., `*_complete.json`). These are normalized to the standard naming convention:

- `question_bank_validated_batch_NN.json`
- `validation_report_batch_NN.json`

Normalization actions are recorded in `validated_batches_manifest.json` under `normalization_log`.

## 3. Manifest Registration

All approved batches are registered in `validated_batches_manifest.json`. The manifest is the single source of truth for the loader.

To add a new batch:
1. Place the batch file and validation report in `data/questions_validated/`
2. Add an entry to the `batches` array in the manifest
3. Update `total_batches` and `total_questions`
4. Run `python scripts/validate_artifacts.py`

## 4. Validation Checks

Run before any commit:

```bash
python scripts/validate_artifacts.py
```

This validates:
- Manifest JSON integrity
- All declared files exist on disk
- No raw files in the validated directory
- Each question has required fields
- Correct explanation model (`correct_explanation` + `wrong_explanations`)
- No duplicate question IDs across batches
- Question counts match manifest declarations

## 5. Runtime Loading

The loader (`app/src/core/loader.py`) reads the manifest and loads all approved batches into a flat question list. The session engine (`app/src/core/session.py`) then draws from this pool to run one-question-at-a-time practice sessions.

## Constraints

- Only validated files are used; raw files are excluded
- Question text is never rewritten during ingestion
- The explanation model must be `correct_explanation` + `wrong_explanations`
- `rationale_by_choice` is forbidden
