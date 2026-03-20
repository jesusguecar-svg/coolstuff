#!/usr/bin/env python3
"""
Job Application Helper - Web Dashboard

Run with: python web.py
Opens at: http://localhost:5000
"""

import os
import re
from datetime import datetime

import yaml
from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
    jsonify,
)

from tracker import JobTracker
from categorizer import (
    categorize_job,
    get_category_display_name,
    get_all_categories,
    match_keywords,
)
from resume_builder import (
    fill_template,
    generate_cover_letter_points,
    export_text,
    get_available_categories,
)

app = Flask(__name__)
app.secret_key = "job-tracker-local-dev-key"

APP_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(APP_DIR, "config.yaml")


def get_config():
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)


def get_tracker():
    config = get_config()
    data_dir = config.get("data_dir", "./data")
    if not os.path.isabs(data_dir):
        data_dir = os.path.join(APP_DIR, data_dir)
    return JobTracker(data_dir)


def get_daily_goal():
    return get_config().get("daily_goal", 25)


def parse_indeed_email(content):
    """Parse job listings from Indeed email text."""
    jobs = []
    lines = content.split("\n")

    title_company_pattern = re.compile(
        r"^(.+?)\s+[-\u2013\u2014|]\s+(.+?)(?:\s+[-\u2013\u2014|]\s+(.+))?$"
    )
    at_pattern = re.compile(
        r"^(.+?)\s+at\s+(.+?)(?:\s+in\s+(.+))?$", re.IGNORECASE
    )
    url_pattern = re.compile(r"(https?://[^\s]*indeed[^\s]*)")

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line or len(line) < 5:
            i += 1
            continue

        job = {}
        match = title_company_pattern.match(line)
        if match and len(match.group(1)) > 3 and len(match.group(2)) > 1:
            job["title"] = match.group(1).strip()
            job["company"] = match.group(2).strip()
            job["location"] = (match.group(3) or "").strip()
        else:
            match = at_pattern.match(line)
            if match and len(match.group(1)) > 3:
                job["title"] = match.group(1).strip()
                job["company"] = match.group(2).strip()
                job["location"] = (match.group(3) or "").strip()

        if job:
            url = ""
            for j in range(max(0, i - 1), min(len(lines), i + 3)):
                url_match = url_pattern.search(lines[j])
                if url_match:
                    url = url_match.group(1)
                    break
            job["url"] = url

            skip_words = [
                "indeed", "unsubscribe", "view all", "sign in",
                "job alert", "email", "privacy", "terms",
            ]
            title_lower = job["title"].lower()
            if not any(sw in title_lower for sw in skip_words):
                jobs.append(job)
        i += 1

    seen = set()
    unique_jobs = []
    for job in jobs:
        key = (job.get("title", "").lower(), job.get("company", "").lower())
        if key not in seen:
            seen.add(key)
            unique_jobs.append(job)
    return unique_jobs


# ---- Routes ----

@app.route("/")
def dashboard():
    tracker = get_tracker()
    goal = get_daily_goal()
    daily = tracker.get_daily_stats()
    weekly = tracker.get_weekly_stats()
    total = tracker.get_total_stats()

    applied_today = daily["applied_today"]
    pct = min(applied_today / goal, 1.0) if goal > 0 else 0

    categories = {
        cat: get_category_display_name(cat)
        for cat in get_all_categories()
    }

    return render_template(
        "dashboard.html",
        daily=daily,
        weekly=weekly,
        total=total,
        goal=goal,
        pct=int(pct * 100),
        applied_today=applied_today,
        categories=categories,
        now=datetime.now(),
    )


@app.route("/jobs")
def jobs_list():
    tracker = get_tracker()
    status = request.args.get("status")
    category = request.args.get("category")
    today_only = request.args.get("today") == "1"

    jobs = tracker.get_jobs(status=status or None, category=category or None, today_only=today_only)
    categories = {cat: get_category_display_name(cat) for cat in get_all_categories()}

    return render_template(
        "jobs.html",
        jobs=jobs,
        categories=categories,
        current_status=status or "",
        current_category=category or "",
        today_only=today_only,
    )


@app.route("/jobs/<int:job_id>")
def job_detail(job_id):
    tracker = get_tracker()
    job = tracker.get_job(job_id)
    if not job:
        flash("Job not found.", "error")
        return redirect(url_for("jobs_list"))

    category = job.get("category", "remote")
    resume = fill_template(category, job["company"], job["title"])
    points = []
    if resume:
        points = generate_cover_letter_points(
            job.get("description", ""), resume.get("skills", [])
        )

    matched_keywords = []
    if job.get("description"):
        matched_keywords = match_keywords(job["description"], category)

    categories = {cat: get_category_display_name(cat) for cat in get_all_categories()}

    return render_template(
        "job_detail.html",
        job=job,
        resume=resume,
        points=points,
        matched_keywords=matched_keywords,
        categories=categories,
    )


@app.route("/jobs/add", methods=["GET", "POST"])
def add_job():
    categories = {cat: get_category_display_name(cat) for cat in get_all_categories()}

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        company = request.form.get("company", "").strip()
        url = request.form.get("url", "").strip()
        location = request.form.get("location", "").strip()
        salary = request.form.get("salary", "").strip()
        description = request.form.get("description", "").strip()
        category = request.form.get("category", "").strip()

        if not title or not company:
            flash("Title and Company are required.", "error")
            return render_template("add_job.html", categories=categories)

        if not category:
            category = categorize_job(title, description, location, company)
            if not category:
                category = "remote"

        tracker = get_tracker()
        job = tracker.add_job(
            title=title,
            company=company,
            url=url,
            description=description,
            location=location,
            salary=salary,
            category=category,
        )

        flash(f"Job #{job['id']} added — {get_category_display_name(category)}", "success")
        return redirect(url_for("job_detail", job_id=job["id"]))

    return render_template("add_job.html", categories=categories)


@app.route("/jobs/<int:job_id>/status", methods=["POST"])
def update_status(job_id):
    tracker = get_tracker()
    status = request.form.get("status", "applied")
    notes = request.form.get("notes", "").strip()

    job = tracker.update_status(job_id, status, notes)
    if job:
        flash(f"Job #{job_id} marked as {status}.", "success")
    else:
        flash("Job not found.", "error")

    return redirect(request.form.get("redirect", url_for("job_detail", job_id=job_id)))


@app.route("/jobs/<int:job_id>/delete", methods=["POST"])
def delete_job(job_id):
    tracker = get_tracker()
    tracker.delete_job(job_id)
    flash(f"Job #{job_id} deleted.", "success")
    return redirect(url_for("jobs_list"))


@app.route("/import", methods=["GET", "POST"])
def import_email():
    if request.method == "POST":
        content = request.form.get("email_content", "").strip()
        if not content:
            flash("No content provided.", "error")
            return redirect(url_for("import_email"))

        jobs_found = parse_indeed_email(content)
        if not jobs_found:
            flash("No job listings found in the pasted content.", "warning")
            return redirect(url_for("import_email"))

        tracker = get_tracker()
        imported = 0
        for job_data in jobs_found:
            title = job_data.get("title", "Unknown Position")
            company = job_data.get("company", "Unknown Company")
            location = job_data.get("location", "")
            url = job_data.get("url", "")

            category = categorize_job(title, "", location, company)
            if not category:
                category = "remote"

            tracker.add_job(
                title=title, company=company, url=url,
                location=location, category=category,
            )
            imported += 1

        flash(f"Imported {imported} job(s)!", "success")
        return redirect(url_for("jobs_list"))

    return render_template("import.html")


@app.route("/resume")
@app.route("/resume/<category>")
def resume_preview(category=None):
    available = get_available_categories()
    if not category:
        category = available[0] if available else None

    job_id = request.args.get("job_id", type=int)
    company_name = ""
    position_title = ""
    job = None

    if job_id:
        tracker = get_tracker()
        job = tracker.get_job(job_id)
        if job:
            company_name = job.get("company", "")
            position_title = job.get("title", "")

    resume_data = fill_template(category, company_name, position_title) if category else None
    resume_text = export_text(resume_data) if resume_data else ""

    categories = {cat: get_category_display_name(cat) for cat in available}

    return render_template(
        "resume_preview.html",
        resume_data=resume_data,
        resume_text=resume_text,
        current_category=category,
        categories=categories,
        job=job,
        job_id=job_id,
    )


@app.route("/resume/<category>/export")
def resume_export(category):
    job_id = request.args.get("job_id", type=int)
    company_name = ""
    position_title = ""

    if job_id:
        tracker = get_tracker()
        job = tracker.get_job(job_id)
        if job:
            company_name = job.get("company", "")
            position_title = job.get("title", "")

    resume_data = fill_template(category, company_name, position_title)
    if not resume_data:
        flash("Resume template not found.", "error")
        return redirect(url_for("resume_preview"))

    text = export_text(resume_data)
    filename = f"resume_{category}"
    if job_id:
        filename += f"_job{job_id}"
    filename += ".txt"

    export_path = os.path.join(APP_DIR, "data", filename)
    os.makedirs(os.path.dirname(export_path), exist_ok=True)
    with open(export_path, "w") as f:
        f.write(text)

    return send_file(export_path, as_attachment=True, download_name=filename)


@app.route("/api/stats")
def api_stats():
    tracker = get_tracker()
    return jsonify({
        "daily": tracker.get_daily_stats(),
        "weekly": tracker.get_weekly_stats(),
        "total": tracker.get_total_stats(),
        "goal": get_daily_goal(),
    })


@app.template_filter("category_name")
def category_name_filter(category):
    return get_category_display_name(category)


if __name__ == "__main__":
    print("\n  Job Application Helper Dashboard")
    print("  https://localhost:5000\n")
    app.run(debug=True, port=5000, ssl_context="adhoc")
