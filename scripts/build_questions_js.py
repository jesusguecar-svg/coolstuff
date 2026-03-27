#!/usr/bin/env python3
"""
Bundle validated question batches into a single JS file for the web app.

Reads the manifest, loads all approved batches, strips metadata fields
not needed by the frontend, and writes web/js/questions.js.

Usage:
    python scripts/build_questions_js.py
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "questions_validated"
MANIFEST_FILE = DATA_DIR / "validated_batches_manifest.json"
OUTPUT_FILE = ROOT / "web" / "js" / "questions.js"

# Fields to keep per question (everything the web app needs)
KEEP_FIELDS = [
    "question_id", "domain", "subdomain", "difficulty",
    "stem", "options", "correct_answer",
    "correct_explanation", "wrong_explanations",
]


def main():
    with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    all_questions = []
    for entry in manifest["batches"]:
        if entry.get("status") != "approved":
            continue
        filepath = DATA_DIR / entry["file"]
        with open(filepath, "r", encoding="utf-8") as f:
            batch = json.load(f)
        for q in batch["questions"]:
            stripped = {k: q[k] for k in KEEP_FIELDS if k in q}
            all_questions.append(stripped)

    # Write as JS module
    js_data = json.dumps(all_questions, ensure_ascii=False, indent=2)
    js_content = (
        "// Auto-generated from data/questions_validated/ — do not edit manually\n"
        f"// Generated: {__import__('datetime').date.today().isoformat()}\n"
        f"// Total questions: {len(all_questions)}\n"
        f"const QUESTION_BANK = {js_data};\n"
    )

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(js_content)

    print(f"Wrote {len(all_questions)} questions to {OUTPUT_FILE}")
    print(f"File size: {OUTPUT_FILE.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
