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
OUTPUT_FILE = ROOT / "docs" / "js" / "questions.js"

# Fields to keep per question (everything the web app needs)
KEEP_FIELDS = [
    "question_id", "domain", "subdomain", "difficulty",
    "stem", "options", "correct_answer",
    "correct_explanation", "wrong_explanations",
]

# Map question domain strings to course unit IDs
DOMAIN_TO_UNIT = {
    "Types of Policies": "N1",
    "Life Insurance": "N1",
    "Policy Riders, Provisions, Options, and Exclusions": "N2",
    "Policy Provisions": "N2",
    "Health Insurance": "N5",
    "Completing the Application, Underwriting, and Delivering the Policy": "N3",
    "Underwriting and Delivery": "N3",
    "Taxes, Retirement, and Other Insurance Concepts": "N4",
    "Unfair Trade Practices": "N4",
    "Agent Duties": "N3",
    "Texas State Statutes Common to All Lines": "TX1",
    "Texas Statutes": "TX1",
    "Texas State Statutes Pertaining to Life, Health, and HMOs": "TX1",
}


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
            stripped["unit_id"] = DOMAIN_TO_UNIT.get(q.get("domain", ""), "N1")
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
