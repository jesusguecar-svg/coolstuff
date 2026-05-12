#!/usr/bin/env python3
"""
Convert domain markdown files into a single JS file for the course app.

Reads each domain .md file, converts to HTML sections, and writes
docs/js/lessons.js with structured lesson data.

Usage:
    python scripts/build_lessons_js.py
"""

import json
import re
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_FILE = ROOT / "docs" / "js" / "lessons.js"

# Unit definitions: order, id, title, exam_weight, source file(s)
UNITS = [
    {
        "unit_id": "N1",
        "title": "Types of Policies (Life)",
        "exam_weight": "16%",
        "order": 1,
        "source": "Domain I – Types of Policies (Life).md",
    },
    {
        "unit_id": "N2",
        "title": "Policy Riders, Provisions, Options & Exclusions",
        "exam_weight": "15%",
        "order": 2,
        "source": "DOMAIN II. POLICY RIDERS, PROVISIONS, OPTIONS, AND EXCLUSIONS (Weight_ 15).docx.md",
    },
    {
        "unit_id": "N5",
        "title": "Types of Policies (Health)",
        "exam_weight": "15%",
        "order": 3,
        "source": "DOMAIN V. TYPES OF POLICIES (HEALTH).md",
    },
    {
        "unit_id": "N6",
        "title": "Health Provisions, Clauses & Riders",
        "exam_weight": "16%",
        "order": 4,
        "source": "Domain VI-Policy-Provisions-Clauses-And-Riders.md",
    },
    {
        "unit_id": "N3",
        "title": "Application, Underwriting & Delivery",
        "exam_weight": "12%",
        "order": 5,
        "source": "DOMAIN III. COMPLETING THE APPLICATION, UNDERWRITING, AND DELIVERING THE POLICIES (Weight_ 12).docx.md",
    },
    {
        "unit_id": "N4",
        "title": "Retirement & Other Insurance Concepts",
        "exam_weight": "8%",
        "order": 6,
        "source": "DOMAIN IV. RETIREMENT AND OTHER INSURANCE CONCEPTS (Weight_ 8).md",
    },
    {
        "unit_id": "N7",
        "title": "Social Insurance",
        "exam_weight": "5%",
        "order": 7,
        "source": "DOMAIN VII- Social-Insurance.md",
    },
    {
        "unit_id": "N8",
        "title": "Other Concepts & Field Underwriting",
        "exam_weight": "5%",
        "order": 8,
        "sources": [
            "DOMAIN VIII. OTHER INSURANCE CONCEPTS (Weight_ 5).docx.md",
            "DOMAIN-IX tx-domain-ix-field-underwriting.md",
        ],
    },
    {
        "unit_id": "TX1",
        "title": "TX Common Life & Health Rules",
        "exam_weight": "14%",
        "order": 9,
        "source": "TEXAS DOMAIN I Texas State-Specific Domain I_ Texas Statutes and Rules Common to Life and Health Insurance.md",
    },
    {
        "unit_id": "TX2",
        "title": "TX Life Insurance Only",
        "exam_weight": "6%",
        "order": 10,
        "source": "TEXAS DOMAIN II TEXAS STATUTES AND RULES PERTINENT TO LIFE INSURANCE ONLY (Weight_ 6).md",
    },
    {
        "unit_id": "TX3",
        "title": "TX Accident & Health Only",
        "exam_weight": "4%",
        "order": 11,
        "source": "TEXAS DOMAIN III Texas State-Specific Domain III_ Texas Statutes and Rules Pertinent to Accident and Health Insurance Only.md",
    },
    {
        "unit_id": "TX4",
        "title": "TX HMO Rules",
        "exam_weight": "3%",
        "order": 12,
        "source": "TEXAS DOMAIN IV TEXAS STATUTES AND RULES PERTINENT TO HMOs (Weight_ 3).md",
    },
]

md = markdown.Markdown(extensions=["tables", "fenced_code"])


def read_source(unit):
    """Read and concatenate source markdown file(s) for a unit."""
    sources = unit.get("sources", [unit["source"]] if "source" in unit else [])
    parts = []
    for src in sources:
        path = ROOT / src
        if path.exists():
            parts.append(path.read_text(encoding="utf-8"))
        else:
            print(f"  WARNING: {src} not found, skipping")
    return "\n\n---\n\n".join(parts)


def strip_footnotes(text):
    """Remove markdown footnote references like [^1] and definitions."""
    text = re.sub(r"\[\^\d+\]", "", text)
    text = re.sub(r"^\[\^\d+\]:.*$", "", text, flags=re.MULTILINE)
    return text


def extract_sections(md_text):
    """Split markdown into sections based on ## headings and convert each to HTML."""
    sections = []
    # Split on ## headings (level 2)
    parts = re.split(r"^(#{1,3})\s+(.+)$", md_text, flags=re.MULTILINE)

    # parts[0] is content before first heading (intro)
    if parts[0].strip():
        md.reset()
        sections.append({
            "heading": "Introduction",
            "level": 2,
            "content_html": md.convert(parts[0].strip()),
        })

    # Process heading groups: parts come in triples (hashes, title, content)
    i = 1
    while i < len(parts) - 2:
        hashes = parts[i]
        title = parts[i + 1].strip()
        content = parts[i + 2] if i + 2 < len(parts) else ""
        level = len(hashes)

        md.reset()
        content_html = md.convert(content.strip()) if content.strip() else ""

        sections.append({
            "heading": title,
            "level": level,
            "content_html": content_html,
        })
        i += 3

    return sections


def estimate_reading_time(text):
    """Estimate reading time in minutes based on word count."""
    words = len(text.split())
    return max(1, round(words / 200))


def build_lesson(unit):
    """Build a single lesson object from a unit definition."""
    print(f"  Processing {unit['unit_id']}: {unit['title']}...")
    raw_md = read_source(unit)
    if not raw_md:
        print(f"    No source content found!")
        return None

    cleaned = strip_footnotes(raw_md)
    sections = extract_sections(cleaned)
    reading_time = estimate_reading_time(cleaned)

    return {
        "unit_id": unit["unit_id"],
        "title": unit["title"],
        "exam_weight": unit["exam_weight"],
        "order": unit["order"],
        "sections": sections,
        "reading_time_min": reading_time,
    }


def main():
    print("Building lessons.js...")
    lessons = []
    for unit in UNITS:
        lesson = build_lesson(unit)
        if lesson:
            lessons.append(lesson)
            print(f"    {len(lesson['sections'])} sections, ~{lesson['reading_time_min']} min read")

    js_data = json.dumps(lessons, ensure_ascii=False, indent=2)
    js_content = (
        "// Auto-generated from domain markdown files — do not edit manually\n"
        f"// Generated: {__import__('datetime').date.today().isoformat()}\n"
        f"// Total units: {len(lessons)}\n"
        f"const LESSONS = {js_data};\n"
    )

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(js_content, encoding="utf-8")

    print(f"\nWrote {len(lessons)} lessons to {OUTPUT_FILE}")
    print(f"File size: {OUTPUT_FILE.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
