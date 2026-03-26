"""
Manifest-driven question loader for the Texas General Lines Practice Engine.

Reads validated_batches_manifest.json and loads question batches from
data/questions_validated/. All questions are returned in a flat list
ready for session consumption.
"""

import json
import os
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[3] / "data" / "questions_validated"
MANIFEST_FILE = DATA_DIR / "validated_batches_manifest.json"


def load_manifest():
    """Load and return the validated batches manifest."""
    if not MANIFEST_FILE.exists():
        raise FileNotFoundError(f"Manifest not found: {MANIFEST_FILE}")
    with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def load_batch(batch_entry):
    """Load a single batch file referenced by a manifest entry."""
    filepath = DATA_DIR / batch_entry["file"]
    if not filepath.exists():
        raise FileNotFoundError(f"Batch file not found: {filepath}")
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["questions"]


def load_all_questions():
    """
    Load all questions from every approved batch in the manifest.
    Returns a flat list of question dicts.
    """
    manifest = load_manifest()
    all_questions = []
    for entry in manifest["batches"]:
        if entry.get("status") != "approved":
            continue
        questions = load_batch(entry)
        all_questions.extend(questions)
    return all_questions


def load_questions_by_batch(batch_id):
    """Load questions from a specific batch by its batch_id."""
    manifest = load_manifest()
    for entry in manifest["batches"]:
        if entry["batch_id"] == batch_id:
            return load_batch(entry)
    raise ValueError(f"Batch '{batch_id}' not found in manifest")


def get_batch_ids():
    """Return list of all approved batch IDs."""
    manifest = load_manifest()
    return [e["batch_id"] for e in manifest["batches"] if e.get("status") == "approved"]


def get_question_stats():
    """Return summary statistics about the loaded question bank."""
    manifest = load_manifest()
    questions = load_all_questions()

    domains = {}
    difficulties = {"easy": 0, "medium": 0, "hard": 0}
    for q in questions:
        d = q.get("domain", "Unknown")
        domains[d] = domains.get(d, 0) + 1
        diff = q.get("difficulty", "medium")
        difficulties[diff] = difficulties.get(diff, 0) + 1

    return {
        "total_batches": manifest["total_batches"],
        "total_questions": len(questions),
        "domains": domains,
        "difficulties": difficulties,
    }
