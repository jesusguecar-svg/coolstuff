#!/usr/bin/env python3
"""
Job Application Helper CLI

A command-line tool to help paralegals manage and track high-volume
job applications efficiently. Supports categorization, resume templating,
and progress tracking.

Usage:
    python app.py dashboard
    python app.py add
    python app.py list
    python app.py apply <job_id>
    python app.py batch
    python app.py import-email
    python app.py resume <category>
"""

import os
import re
import sys
import click
import yaml
from datetime import datetime

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import BarColumn, Progress, TextColumn, TaskProgressColumn
from rich.columns import Columns
from rich.text import Text
from rich import box

from tracker import JobTracker
from categorizer import (
    categorize_job,
    get_category_display_name,
    get_all_categories,
    match_keywords,
    load_config,
)
from resume_builder import (
    fill_template,
    generate_cover_letter_points,
    export_text,
    get_available_categories,
)

console = Console()

# Load config for data_dir and daily_goal
APP_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(APP_DIR, "config.yaml")


def get_config():
    """Load the application config."""
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)


def get_tracker():
    """Create a JobTracker with the configured data directory."""
    config = get_config()
    data_dir = config.get("data_dir", "./data")
    if not os.path.isabs(data_dir):
        data_dir = os.path.join(APP_DIR, data_dir)
    return JobTracker(data_dir)


def get_daily_goal():
    """Get the daily application goal from config."""
    config = get_config()
    return config.get("daily_goal", 25)


# ---- CLI Group ----

@click.group()
def cli():
    """Job Application Helper - Track and manage paralegal job applications."""
    pass


# ---- ADD Command ----

@cli.command()
def add():
    """Add a new job to apply to."""
    console.print(Panel("[bold cyan]Add New Job[/bold cyan]", expand=False))

    title = click.prompt("Job Title")
    company = click.prompt("Company")
    url = click.prompt("Job URL (optional)", default="", show_default=False)
    location = click.prompt("Location")
    salary = click.prompt("Salary (optional)", default="", show_default=False)

    console.print(
        "\n[dim]Paste the job description below. "
        "Press Enter twice on an empty line to finish.[/dim]"
    )
    desc_lines = []
    empty_count = 0
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line == "":
            empty_count += 1
            if empty_count >= 2:
                break
            desc_lines.append(line)
        else:
            empty_count = 0
            desc_lines.append(line)
    description = "\n".join(desc_lines).strip()

    # Auto-categorize
    suggested = categorize_job(title, description, location, company)
    categories = get_all_categories()

    if suggested:
        display = get_category_display_name(suggested)
        console.print(f"\n[green]Suggested category:[/green] {display}")
        if not click.confirm("Accept this category?", default=True):
            suggested = None

    if not suggested:
        console.print("\n[yellow]Choose a category:[/yellow]")
        for i, cat in enumerate(categories, 1):
            display = get_category_display_name(cat)
            console.print(f"  {i}. {display}")
        choice = click.prompt(
            "Category number", type=click.IntRange(1, len(categories))
        )
        suggested = categories[choice - 1]

    tracker = get_tracker()
    job = tracker.add_job(
        title=title,
        company=company,
        url=url,
        description=description,
        location=location,
        salary=salary,
        category=suggested,
    )

    console.print(
        f"\n[bold green]Job #{job['id']} added![/bold green] "
        f"[dim]({get_category_display_name(suggested)})[/dim]"
    )


# ---- APPLY Command ----

@cli.command()
@click.argument("job_id", type=int)
def apply(job_id):
    """Process an application for a specific job."""
    tracker = get_tracker()
    job = tracker.get_job(job_id)

    if not job:
        console.print(f"[red]Job #{job_id} not found.[/red]")
        sys.exit(1)

    # Show job details
    console.print(
        Panel(
            f"[bold]{job['title']}[/bold]\n"
            f"[cyan]{job['company']}[/cyan]\n"
            f"Location: {job.get('location', 'N/A')}\n"
            f"Salary: {job.get('salary', 'N/A') or 'N/A'}\n"
            f"Category: {get_category_display_name(job.get('category', ''))}\n"
            f"Status: {job.get('status', 'pending')}",
            title=f"Job #{job_id}",
            expand=False,
        )
    )

    if job.get("description"):
        console.print(
            Panel(
                job["description"][:500]
                + ("..." if len(job.get("description", "")) > 500 else ""),
                title="Description Preview",
                expand=False,
            )
        )

    category = job.get("category", "remote")

    # Generate tailored resume
    resume = fill_template(category, job["company"], job["title"])

    if resume:
        console.print(
            Panel(
                f"[bold]Tailored Objective:[/bold]\n{resume.get('objective', '')}",
                title="Resume Preview",
                border_style="green",
                expand=False,
            )
        )

        # Cover letter points
        points = generate_cover_letter_points(
            job.get("description", ""), resume.get("skills", [])
        )
        points_text = "\n".join(f"  [green]*[/green] {p}" for p in points)
        console.print(
            Panel(
                points_text,
                title="Cover Letter Key Points",
                border_style="cyan",
                expand=False,
            )
        )

    # Application checklist
    console.print("\n[bold yellow]Application Checklist:[/bold yellow]")
    steps = [
        f"Open job URL: {job.get('url', 'N/A') or 'N/A'}",
        "Review job requirements against your experience",
        f"Upload resume (template: [bold]{category}.yaml[/bold])",
        "Write cover letter using key points above",
        "Double-check all fields and attachments",
        "Submit application",
    ]
    for i, step in enumerate(steps, 1):
        console.print(f"  [{i}] {step}")

    console.print()
    if click.confirm("Mark this job as applied?", default=True):
        notes = click.prompt("Any notes? (optional)", default="", show_default=False)
        tracker.update_status(job_id, "applied", notes)
        console.print(f"[bold green]Job #{job_id} marked as applied![/bold green]")

        # Show daily progress
        stats = tracker.get_daily_stats()
        goal = get_daily_goal()
        applied = stats["applied_today"]
        console.print(
            f"\n[cyan]Daily progress: {applied}/{goal} applications[/cyan]"
        )
    else:
        console.print("[dim]Job status unchanged.[/dim]")


# ---- BATCH Command ----

@cli.command()
def batch():
    """Batch mode - process pending applications quickly."""
    tracker = get_tracker()
    pending = tracker.get_jobs(status="pending")

    if not pending:
        console.print("[yellow]No pending jobs to process.[/yellow]")
        return

    # Sort by category
    pending.sort(key=lambda j: j.get("category", ""))

    stats = tracker.get_daily_stats()
    goal = get_daily_goal()
    applied_count = stats["applied_today"]

    console.print(
        Panel(
            f"[bold]Pending: {len(pending)} jobs[/bold]\n"
            f"Today's progress: {applied_count}/{goal}",
            title="Batch Mode",
            border_style="cyan",
        )
    )

    current_category = None
    for job in pending:
        cat = job.get("category", "uncategorized")
        if cat != current_category:
            current_category = cat
            console.print(
                f"\n[bold magenta]--- {get_category_display_name(cat)} ---"
                f"[/bold magenta]"
            )

        console.print(
            f"\n[bold]#{job['id']}[/bold] {job['title']} @ "
            f"[cyan]{job['company']}[/cyan]"
        )
        console.print(
            f"  Location: {job.get('location', 'N/A')} | "
            f"Salary: {job.get('salary', 'N/A') or 'N/A'}"
        )
        if job.get("url"):
            console.print(f"  URL: {job['url']}")

        # Quick resume info
        resume = fill_template(cat, job["company"], job["title"])
        if resume:
            points = generate_cover_letter_points(
                job.get("description", ""), resume.get("skills", [])
            )
            if points:
                console.print(f"  [dim]Key point: {points[0]}[/dim]")

        console.print()
        action = click.prompt(
            "  [a]pply / [s]kip / [r]eject / [q]uit",
            type=click.Choice(["a", "s", "r", "q"], case_sensitive=False),
            default="s",
            show_default=True,
        )

        if action == "a":
            notes = click.prompt(
                "  Notes (optional)", default="", show_default=False
            )
            tracker.update_status(job["id"], "applied", notes)
            applied_count += 1
            console.print(
                f"  [green]Applied! ({applied_count}/{goal} today)[/green]"
            )
        elif action == "r":
            tracker.update_status(job["id"], "rejected")
            console.print("  [red]Marked as rejected.[/red]")
        elif action == "q":
            console.print(
                f"\n[cyan]Session complete. {applied_count}/{goal} "
                f"applications today.[/cyan]"
            )
            return
        # 's' = skip, do nothing

        if applied_count >= goal:
            console.print(
                f"\n[bold green]Daily goal of {goal} reached![/bold green]"
            )
            if not click.confirm("Continue processing?", default=False):
                return

    console.print(
        f"\n[cyan]All pending jobs processed. "
        f"{applied_count}/{goal} applications today.[/cyan]"
    )


# ---- DASHBOARD Command ----

@cli.command()
def dashboard():
    """Show daily dashboard with stats and progress."""
    tracker = get_tracker()
    goal = get_daily_goal()

    daily = tracker.get_daily_stats()
    weekly = tracker.get_weekly_stats()
    total = tracker.get_total_stats()

    # Header
    console.print()
    console.print(
        Panel(
            f"[bold]Job Application Dashboard[/bold]\n"
            f"[dim]{datetime.now().strftime('%A, %B %d, %Y')}[/dim]",
            border_style="cyan",
            expand=False,
        )
    )

    # Daily progress bar
    applied_today = daily["applied_today"]
    pending = daily["pending"]
    pct = min(applied_today / goal, 1.0) if goal > 0 else 0

    bar_width = 30
    filled = int(pct * bar_width)
    bar = "[green]" + "#" * filled + "[/green]" + "[dim]" + "-" * (bar_width - filled) + "[/dim]"

    if applied_today >= goal:
        status_color = "bold green"
        status_text = "GOAL REACHED!"
    elif applied_today >= goal * 0.5:
        status_color = "yellow"
        status_text = "Keep going!"
    else:
        status_color = "red"
        status_text = "Get started!"

    console.print(
        Panel(
            f"Applied Today:  [bold]{applied_today}[/bold] / {goal}  "
            f"[{bar}]  [{status_color}]{status_text}[/{status_color}]\n"
            f"Pending:        [bold]{pending}[/bold] jobs waiting\n"
            f"Remaining:      [bold]{max(0, goal - applied_today)}[/bold] to reach goal",
            title="Today's Progress",
            border_style="green" if applied_today >= goal else "yellow",
        )
    )

    # Category breakdown for today
    if daily["by_category"]:
        cat_table = Table(
            title="Today by Category",
            box=box.SIMPLE,
            show_header=True,
            header_style="bold",
        )
        cat_table.add_column("Category", style="cyan")
        cat_table.add_column("Applied", justify="right", style="green")

        for cat, count in sorted(daily["by_category"].items()):
            cat_table.add_row(get_category_display_name(cat), str(count))
        console.print(cat_table)

    # Weekly stats
    week_applied = weekly["applied_this_week"]
    console.print(
        Panel(
            f"Applications this week: [bold]{week_applied}[/bold]\n"
            + (
                "\n".join(
                    f"  {day}: {count} applied"
                    for day, count in sorted(weekly.get("by_day", {}).items())
                )
                if weekly.get("by_day")
                else "  [dim]No applications yet this week.[/dim]"
            ),
            title="This Week",
            border_style="blue",
        )
    )

    # All-time totals
    total_jobs = total["total"]
    by_status = total.get("by_status", {})
    status_line = " | ".join(
        f"{status}: [bold]{count}[/bold]"
        for status, count in sorted(by_status.items())
    )

    console.print(
        Panel(
            f"Total jobs tracked: [bold]{total_jobs}[/bold]\n"
            f"{status_line if status_line else '[dim]No jobs tracked yet.[/dim]'}",
            title="All Time",
            border_style="magenta",
        )
    )
    console.print()


# ---- LIST Command ----

@cli.command(name="list")
@click.option(
    "--status", "-s",
    type=click.Choice(
        ["pending", "applied", "rejected", "interview"], case_sensitive=False
    ),
    default=None,
    help="Filter by status",
)
@click.option(
    "--category", "-c",
    default=None,
    help="Filter by category",
)
@click.option(
    "--today", "-t",
    is_flag=True,
    default=False,
    help="Show only today's jobs",
)
def list_jobs(status, category, today):
    """List jobs with optional filters."""
    tracker = get_tracker()
    jobs = tracker.get_jobs(status=status, category=category, today_only=today)

    if not jobs:
        console.print("[yellow]No jobs found matching filters.[/yellow]")
        return

    table = Table(
        title="Job Applications",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan",
    )
    table.add_column("ID", justify="right", style="bold", width=5)
    table.add_column("Title", max_width=30)
    table.add_column("Company", style="cyan", max_width=20)
    table.add_column("Location", max_width=15)
    table.add_column("Category", style="magenta", max_width=20)
    table.add_column("Status", justify="center", width=10)
    table.add_column("Date", width=12)

    status_styles = {
        "pending": "[yellow]pending[/yellow]",
        "applied": "[green]applied[/green]",
        "rejected": "[red]rejected[/red]",
        "interview": "[bold green]INTERVIEW[/bold green]",
    }

    for job in jobs:
        job_status = job.get("status", "pending")
        styled_status = status_styles.get(job_status, job_status)
        date_str = (
            job.get("date_applied", "")[:10]
            if job.get("date_applied")
            else job.get("date_added", "")[:10]
        )
        table.add_row(
            str(job.get("id", "")),
            job.get("title", ""),
            job.get("company", ""),
            job.get("location", ""),
            get_category_display_name(job.get("category", "")),
            styled_status,
            date_str,
        )

    console.print(table)
    console.print(f"\n[dim]Total: {len(jobs)} jobs[/dim]")


# ---- IMPORT-EMAIL Command ----

@cli.command(name="import-email")
def import_email():
    """Import jobs from pasted Indeed email content."""
    console.print(
        Panel(
            "[bold cyan]Import from Indeed Email[/bold cyan]\n"
            "[dim]Paste the email content below. "
            "Press Enter twice on an empty line to finish.[/dim]",
            expand=False,
        )
    )

    lines = []
    empty_count = 0
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line == "":
            empty_count += 1
            if empty_count >= 2:
                break
            lines.append(line)
        else:
            empty_count = 0
            lines.append(line)

    content = "\n".join(lines).strip()
    if not content:
        console.print("[red]No content provided.[/red]")
        return

    # Parse jobs from email content
    jobs_found = _parse_indeed_email(content)

    if not jobs_found:
        console.print(
            "[yellow]No job listings found in the pasted content.[/yellow]\n"
            "[dim]Tip: Make sure you paste the full email text including "
            "job titles and company names.[/dim]"
        )
        return

    tracker = get_tracker()
    imported = 0
    category_counts = {}

    console.print(f"\n[bold]Found {len(jobs_found)} potential job(s):[/bold]\n")

    for job_data in jobs_found:
        title = job_data.get("title", "Unknown Position")
        company = job_data.get("company", "Unknown Company")
        location = job_data.get("location", "")
        url = job_data.get("url", "")

        category = categorize_job(title, "", location, company)
        if not category:
            category = "remote"  # default

        cat_display = get_category_display_name(category)
        console.print(
            f"  [green]+[/green] {title} @ [cyan]{company}[/cyan] "
            f"({location}) -> [magenta]{cat_display}[/magenta]"
        )

        tracker.add_job(
            title=title,
            company=company,
            url=url,
            location=location,
            category=category,
        )
        imported += 1
        category_counts[category] = category_counts.get(category, 0) + 1

    console.print(f"\n[bold green]Imported {imported} job(s)![/bold green]")
    for cat, count in sorted(category_counts.items()):
        console.print(
            f"  {get_category_display_name(cat)}: {count}"
        )


def _parse_indeed_email(content):
    """
    Parse job listings from Indeed email text.

    Looks for patterns like:
    - "Job Title" followed by company name
    - Lines with "at Company" or "- Company"
    - Indeed URLs
    """
    jobs = []
    lines = content.split("\n")

    # Pattern 1: "Title - Company - Location" or "Title at Company in Location"
    # Common Indeed email format
    title_company_pattern = re.compile(
        r"^(.+?)\s+[-\u2013\u2014|]\s+(.+?)(?:\s+[-\u2013\u2014|]\s+(.+))?$"
    )
    at_pattern = re.compile(
        r"^(.+?)\s+at\s+(.+?)(?:\s+in\s+(.+))?$", re.IGNORECASE
    )

    # Pattern 2: Indeed job URLs
    url_pattern = re.compile(r"(https?://[^\s]*indeed[^\s]*)")

    # Try structured parsing
    i = 0
    while i < len(lines):
        line = lines[i].strip()

        if not line or len(line) < 5:
            i += 1
            continue

        job = {}

        # Try "title - company - location" pattern
        match = title_company_pattern.match(line)
        if match and len(match.group(1)) > 3 and len(match.group(2)) > 1:
            job["title"] = match.group(1).strip()
            job["company"] = match.group(2).strip()
            job["location"] = (match.group(3) or "").strip()
        else:
            # Try "title at company in location" pattern
            match = at_pattern.match(line)
            if match and len(match.group(1)) > 3:
                job["title"] = match.group(1).strip()
                job["company"] = match.group(2).strip()
                job["location"] = (match.group(3) or "").strip()

        # Look for URL in nearby lines
        if job:
            url = ""
            for j in range(max(0, i - 1), min(len(lines), i + 3)):
                url_match = url_pattern.search(lines[j])
                if url_match:
                    url = url_match.group(1)
                    break
            job["url"] = url

            # Skip lines that look like headers/footers rather than jobs
            skip_words = [
                "indeed", "unsubscribe", "view all", "sign in",
                "job alert", "email", "privacy", "terms",
            ]
            title_lower = job["title"].lower()
            if not any(sw in title_lower for sw in skip_words):
                jobs.append(job)

        i += 1

    # Deduplicate by title+company
    seen = set()
    unique_jobs = []
    for job in jobs:
        key = (job.get("title", "").lower(), job.get("company", "").lower())
        if key not in seen:
            seen.add(key)
            unique_jobs.append(job)

    return unique_jobs


# ---- RESUME Command ----

@cli.command()
@click.argument("category")
@click.option("--job-id", "-j", type=int, default=None, help="Customize for a specific job")
@click.option("--export", "-e", is_flag=True, help="Export as plain text file")
def resume(category, job_id, export):
    """Preview or export a resume for a category."""
    available = get_available_categories()

    if category not in available:
        console.print(f"[red]Category '{category}' not found.[/red]")
        console.print(f"[dim]Available: {', '.join(available)}[/dim]")
        return

    company_name = ""
    position_title = ""

    if job_id:
        tracker = get_tracker()
        job = tracker.get_job(job_id)
        if job:
            company_name = job.get("company", "")
            position_title = job.get("title", "")
            console.print(
                f"[dim]Customizing for: {position_title} at {company_name}[/dim]\n"
            )
        else:
            console.print(f"[yellow]Job #{job_id} not found, using generic template.[/yellow]\n")

    resume_data = fill_template(category, company_name, position_title)
    if not resume_data:
        console.print(f"[red]Could not load template for '{category}'.[/red]")
        return

    text_output = export_text(resume_data)

    if export:
        filename = f"resume_{category}"
        if job_id:
            filename += f"_job{job_id}"
        filename += ".txt"
        export_path = os.path.join(APP_DIR, "data", filename)
        os.makedirs(os.path.dirname(export_path), exist_ok=True)
        with open(export_path, "w") as f:
            f.write(text_output)
        console.print(f"[green]Resume exported to: {export_path}[/green]")
    else:
        console.print(
            Panel(
                text_output,
                title=f"Resume: {get_category_display_name(category)}",
                border_style="green",
            )
        )

    # Show matched skills if we have a job
    if job_id:
        tracker = get_tracker()
        job = tracker.get_job(job_id)
        if job and job.get("description"):
            matched = match_keywords(job["description"], category)
            if matched:
                console.print(
                    f"\n[cyan]Keywords matched from job description:[/cyan] "
                    f"{', '.join(matched)}"
                )


# ---- Entry Point ----

if __name__ == "__main__":
    cli()
