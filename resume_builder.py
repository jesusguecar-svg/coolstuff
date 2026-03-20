"""Resume builder module - loads templates and generates tailored resumes."""

import os
import yaml


RESUMES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resumes")


def load_template(category):
    """Load a resume YAML template for the given category."""
    path = os.path.join(RESUMES_DIR, f"{category}.yaml")
    if not os.path.exists(path):
        return None
    with open(path, "r") as f:
        return yaml.safe_load(f)


def fill_template(category, company_name="", position_title=""):
    """Load and fill a resume template with company/position details."""
    template = load_template(category)
    if not template:
        return None

    # Fill placeholders in objective
    if template.get("objective"):
        template["objective"] = template["objective"].format(
            company_name=company_name or "[Company]",
            position_title=position_title or "[Position]",
        )

    return template


def generate_cover_letter_points(job_description, resume_skills):
    """
    Generate cover letter talking points by matching job description
    keywords against resume skills.

    Returns a list of strings (talking points).
    """
    if not job_description or not resume_skills:
        return ["Highlight your relevant paralegal experience and skills."]

    desc_lower = job_description.lower()
    points = []

    # Find matching skills
    matched_skills = []
    for skill in resume_skills:
        # Check if any significant word from the skill appears in the description
        skill_words = [w for w in skill.lower().split() if len(w) > 3]
        if any(word in desc_lower for word in skill_words):
            matched_skills.append(skill)

    if matched_skills:
        # Group into talking points
        if len(matched_skills) >= 3:
            top_skills = matched_skills[:3]
            points.append(
                f"Emphasize your direct experience with: {', '.join(top_skills)}"
            )
        if len(matched_skills) > 3:
            remaining = matched_skills[3:6]
            points.append(
                f"Also highlight proficiency in: {', '.join(remaining)}"
            )
        points.append(
            f"You match {len(matched_skills)} of the listed requirements - "
            f"mention this breadth of experience."
        )
    else:
        points.append(
            "Focus on transferable paralegal skills and eagerness to learn."
        )

    # Check for specific keywords in description
    keyword_points = {
        "bilingual": "Mention bilingual capabilities (English/Spanish).",
        "spanish": "Highlight Spanish language proficiency.",
        "remote": "Emphasize proven remote work track record and tech proficiency.",
        "deadline": "Stress your track record of meeting all filing deadlines.",
        "client": "Highlight client communication and relationship management skills.",
        "research": "Mention legal research proficiency (Westlaw, LexisNexis).",
        "filing": "Reference e-filing experience across state and federal courts.",
        "trial": "Emphasize trial preparation and litigation support experience.",
        "compliance": "Highlight compliance and regulatory experience.",
        "corporate": "Stress corporate governance and entity management experience.",
    }

    for keyword, point in keyword_points.items():
        if keyword in desc_lower and point not in points:
            points.append(point)

    # Always add a closing point
    points.append(
        "Express genuine enthusiasm for the company and this specific role."
    )

    return points


def export_text(resume_dict):
    """Export a resume dictionary as formatted plain text."""
    if not resume_dict:
        return "No resume data available."

    lines = []

    # Contact info
    contact = resume_dict.get("contact", {})
    lines.append(contact.get("name", "[YOUR NAME]").upper())
    contact_parts = []
    if contact.get("email"):
        contact_parts.append(contact["email"])
    if contact.get("phone"):
        contact_parts.append(contact["phone"])
    if contact.get("location"):
        contact_parts.append(contact["location"])
    if contact_parts:
        lines.append(" | ".join(contact_parts))
    if contact.get("linkedin"):
        lines.append(contact["linkedin"])
    lines.append("")

    # Objective
    if resume_dict.get("objective"):
        lines.append("OBJECTIVE")
        lines.append("-" * 60)
        lines.append(resume_dict["objective"])
        lines.append("")

    # Summary
    if resume_dict.get("summary"):
        lines.append("PROFESSIONAL SUMMARY")
        lines.append("-" * 60)
        lines.append(resume_dict["summary"])
        lines.append("")

    # Skills
    skills = resume_dict.get("skills", [])
    if skills:
        lines.append("SKILLS")
        lines.append("-" * 60)
        # Display in two columns
        for i in range(0, len(skills), 2):
            if i + 1 < len(skills):
                lines.append(f"  * {skills[i]:<40s}  * {skills[i+1]}")
            else:
                lines.append(f"  * {skills[i]}")
        lines.append("")

    # Experience
    experience = resume_dict.get("experience", [])
    if experience:
        lines.append("EXPERIENCE")
        lines.append("-" * 60)
        for exp in experience:
            lines.append(f"{exp.get('title', '')} | {exp.get('company', '')}")
            lines.append(f"{exp.get('dates', '')}")
            for bullet in exp.get("bullets", []):
                lines.append(f"  - {bullet}")
            lines.append("")

    # Education
    education = resume_dict.get("education", [])
    if education:
        lines.append("EDUCATION")
        lines.append("-" * 60)
        for edu in education:
            lines.append(
                f"{edu.get('degree', '')} - {edu.get('school', '')} "
                f"({edu.get('year', '')})"
            )
        lines.append("")

    # Certifications
    certs = resume_dict.get("certifications", [])
    if certs:
        lines.append("CERTIFICATIONS")
        lines.append("-" * 60)
        for cert in certs:
            lines.append(f"  * {cert}")
        lines.append("")

    return "\n".join(lines)


def get_available_categories():
    """Return list of categories that have resume templates."""
    categories = []
    if os.path.isdir(RESUMES_DIR):
        for f in os.listdir(RESUMES_DIR):
            if f.endswith(".yaml"):
                categories.append(f.replace(".yaml", ""))
    return sorted(categories)
