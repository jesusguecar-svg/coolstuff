# Job Application Helper CLI

A command-line tool for paralegals to manage and track high-volume job applications.

## Setup

```bash
pip install -r requirements.txt
# Edit resumes/*.yaml with your actual information
# Edit config.yaml to customize categories and settings
python app.py dashboard
```

## Commands

```bash
python app.py dashboard        # Daily stats and progress
python app.py add              # Add a new job
python app.py list             # List all jobs (use --status, --category, --today filters)
python app.py apply <job_id>   # Process a specific application
python app.py batch            # Process pending jobs one by one
python app.py import-email     # Import jobs from pasted Indeed email
python app.py resume <category> # Preview resume (use --job-id to customize, --export to save)
```

## Categories

- `immigration_paralegal_dallas` - Immigration Paralegal in Dallas
- `family_law_paralegal_dallas` - Family Law Litigation Paralegal in Dallas
- `remote` - Remote paralegal opportunities
- `premium` - Premium opportunities (major companies)

## File Structure

- `app.py` - Main CLI application
- `tracker.py` - Job data management
- `categorizer.py` - Auto-categorization by keywords
- `resume_builder.py` - Resume template rendering
- `config.yaml` - Settings and keyword definitions
- `resumes/` - Resume YAML templates per category
- `data/` - Job tracking data (auto-created)
