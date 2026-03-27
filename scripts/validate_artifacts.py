#!/usr/bin/env python3
"""
Validate all question batch artifacts against the schema and manifest.

Checks:
  1. Manifest exists and is valid JSON
  2. All batch files listed in manifest exist
  3. All validation report files listed in manifest exist
  4. Each batch file is valid JSON with correct structure
  5. Each question has required fields and correct explanation model
  6. No raw (non-validated) files are referenced
  7. Question counts match manifest declarations
  8. No duplicate question IDs across all batches

Usage:
    python scripts/validate_artifacts.py
"""

import json
import sys
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "questions_validated"
MANIFEST_FILE = DATA_DIR / "validated_batches_manifest.json"

REQUIRED_QUESTION_FIELDS = [
    "question_id", "rule_ids", "domain", "subdomain", "difficulty",
    "format", "stem", "options", "correct_answer",
    "correct_explanation", "wrong_explanations",
    "source_confidence", "review_status", "status_history",
]

VALID_ANSWERS = {"A", "B", "C", "D"}
VALID_DIFFICULTIES = {"easy", "medium", "hard"}

errors = []
warnings = []


def error(msg):
    errors.append(msg)
    print(f"  ERROR: {msg}")


def warn(msg):
    warnings.append(msg)
    print(f"  WARN:  {msg}")


def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        error(f"Invalid JSON in {path.name}: {e}")
        return None
    except FileNotFoundError:
        error(f"File not found: {path}")
        return None


def validate_question(q, batch_id):
    """Validate a single question dict."""
    qid = q.get("question_id", "UNKNOWN")
    prefix = f"[{qid}]"

    # Required fields
    for field in REQUIRED_QUESTION_FIELDS:
        if field not in q:
            error(f"{prefix} Missing required field: {field}")

    # correct_answer
    if q.get("correct_answer") not in VALID_ANSWERS:
        error(f"{prefix} Invalid correct_answer: {q.get('correct_answer')}")

    # difficulty
    if q.get("difficulty") not in VALID_DIFFICULTIES:
        error(f"{prefix} Invalid difficulty: {q.get('difficulty')}")

    # options: must be array of 4 {label, text}
    options = q.get("options", [])
    if not isinstance(options, list) or len(options) != 4:
        error(f"{prefix} Options must be array of 4 items, got {len(options) if isinstance(options, list) else type(options)}")
    else:
        labels = {o.get("label") for o in options}
        if labels != VALID_ANSWERS:
            error(f"{prefix} Option labels must be A,B,C,D; got {labels}")

    # Explanation model: correct_explanation + wrong_explanations (NOT rationale_by_choice)
    if "rationale_by_choice" in q:
        error(f"{prefix} Contains forbidden 'rationale_by_choice' field; must use correct_explanation + wrong_explanations")

    if "correct_explanation" in q:
        if not isinstance(q["correct_explanation"], str) or len(q["correct_explanation"]) < 10:
            error(f"{prefix} correct_explanation must be a string of at least 10 chars")

    if "wrong_explanations" in q:
        we = q["wrong_explanations"]
        if not isinstance(we, dict):
            error(f"{prefix} wrong_explanations must be an object")
        else:
            correct = q.get("correct_answer", "")
            expected_keys = VALID_ANSWERS - {correct}
            actual_keys = set(we.keys())
            # Accept 3 keys (wrong only) or 4 keys (all options including correct)
            if actual_keys != expected_keys and actual_keys != VALID_ANSWERS:
                error(f"{prefix} wrong_explanations keys should be {expected_keys} or A/B/C/D, got {actual_keys}")

    # stem length
    stem = q.get("stem", "")
    if isinstance(stem, str) and len(stem) < 10:
        error(f"{prefix} Stem is too short ({len(stem)} chars)")

    return qid


def main():
    print()
    print("=" * 60)
    print("  Validated Artifacts Checker")
    print("=" * 60)
    print()

    # 1. Load manifest
    print("  [1/5] Loading manifest...")
    manifest = load_json(MANIFEST_FILE)
    if manifest is None:
        print(f"\n  FATAL: Cannot proceed without manifest.\n")
        sys.exit(1)
    print(f"         {manifest['total_batches']} batches, {manifest['total_questions']} questions declared")

    # 2. Check batch and report files exist
    print("  [2/5] Checking file presence...")
    for entry in manifest["batches"]:
        batch_path = DATA_DIR / entry["file"]
        report_path = DATA_DIR / entry["report"]
        if not batch_path.exists():
            error(f"Batch file missing: {entry['file']}")
        if not report_path.exists():
            error(f"Report file missing: {entry['report']}")

    # Check for raw files
    for f in DATA_DIR.glob("*raw*"):
        error(f"Raw file found in validated directory: {f.name}")

    # 3. Validate each batch
    print("  [3/5] Validating batch contents...")
    all_question_ids = set()
    actual_total = 0

    for entry in manifest["batches"]:
        batch_path = DATA_DIR / entry["file"]
        batch_data = load_json(batch_path)
        if batch_data is None:
            continue

        questions = batch_data.get("questions", [])
        declared_count = entry.get("question_count", 0)
        if len(questions) != declared_count:
            error(f"Batch {entry['batch_id']}: manifest declares {declared_count} questions, file has {len(questions)}")

        for q in questions:
            qid = validate_question(q, entry["batch_id"])
            if qid in all_question_ids:
                error(f"Duplicate question ID across batches: {qid}")
            all_question_ids.add(qid)

        actual_total += len(questions)
        print(f"         Batch {entry['batch_id']}: {len(questions)} questions OK")

    # 4. Validate reports parse as JSON
    print("  [4/5] Validating report files...")
    for entry in manifest["batches"]:
        report_path = DATA_DIR / entry["report"]
        report = load_json(report_path)
        if report is not None:
            print(f"         Report {entry['batch_id']}: valid JSON")

    # 5. Cross-checks
    print("  [5/5] Cross-checks...")
    if actual_total != manifest["total_questions"]:
        error(f"Manifest total_questions ({manifest['total_questions']}) != actual ({actual_total})")
    else:
        print(f"         Total questions: {actual_total} (matches manifest)")

    print(f"         Unique question IDs: {len(all_question_ids)}")

    # Summary
    print()
    print("=" * 60)
    if errors:
        print(f"  FAILED: {len(errors)} error(s), {len(warnings)} warning(s)")
        for e in errors:
            print(f"    - {e}")
        print("=" * 60)
        sys.exit(1)
    else:
        print(f"  PASSED: 0 errors, {len(warnings)} warning(s)")
        print("=" * 60)
        sys.exit(0)


if __name__ == "__main__":
    main()
