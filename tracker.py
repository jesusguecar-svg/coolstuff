"""Application tracker module - manages job data in YAML files."""

import os
import yaml
from datetime import datetime, timedelta


class JobTracker:
    """Manages job application data stored in YAML."""

    def __init__(self, data_dir="./data"):
        self.data_dir = data_dir
        self.jobs_file = os.path.join(data_dir, "jobs.yaml")
        self._ensure_data_dir()

    def _ensure_data_dir(self):
        """Create data directory if it doesn't exist."""
        os.makedirs(self.data_dir, exist_ok=True)

    def _load_jobs(self):
        """Load jobs from YAML file."""
        if not os.path.exists(self.jobs_file):
            return []
        with open(self.jobs_file, "r") as f:
            data = yaml.safe_load(f)
        return data if data else []

    def _save_jobs(self, jobs):
        """Save jobs to YAML file."""
        self._ensure_data_dir()
        with open(self.jobs_file, "w") as f:
            yaml.dump(jobs, f, default_flow_style=False, sort_keys=False)

    def _next_id(self, jobs):
        """Get the next auto-increment ID."""
        if not jobs:
            return 1
        return max(j.get("id", 0) for j in jobs) + 1

    def add_job(self, title, company, url="", description="", location="",
                salary="", category="", notes=""):
        """Add a new job to the tracker."""
        jobs = self._load_jobs()
        job = {
            "id": self._next_id(jobs),
            "title": title,
            "company": company,
            "url": url,
            "description": description,
            "location": location,
            "salary": salary,
            "category": category,
            "status": "pending",
            "date_added": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "date_applied": "",
            "notes": notes,
        }
        jobs.append(job)
        self._save_jobs(jobs)
        return job

    def update_status(self, job_id, status, notes=""):
        """Update the status of a job."""
        jobs = self._load_jobs()
        for job in jobs:
            if job["id"] == job_id:
                job["status"] = status
                if status == "applied":
                    job["date_applied"] = datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                if notes:
                    job["notes"] = notes
                self._save_jobs(jobs)
                return job
        return None

    def get_job(self, job_id):
        """Get a single job by ID."""
        jobs = self._load_jobs()
        for job in jobs:
            if job["id"] == job_id:
                return job
        return None

    def get_jobs(self, status=None, category=None, today_only=False):
        """Get jobs with optional filters."""
        jobs = self._load_jobs()
        today = datetime.now().strftime("%Y-%m-%d")

        filtered = []
        for job in jobs:
            if status and job.get("status") != status:
                continue
            if category and job.get("category") != category:
                continue
            if today_only:
                added = job.get("date_added", "")[:10]
                applied = job.get("date_applied", "")[:10]
                if added != today and applied != today:
                    continue
            filtered.append(job)
        return filtered

    def get_daily_stats(self):
        """Get statistics for today."""
        today = datetime.now().strftime("%Y-%m-%d")
        jobs = self._load_jobs()

        applied_today = 0
        pending = 0
        by_category = {}

        for job in jobs:
            if job.get("status") == "pending":
                pending += 1
            applied_date = job.get("date_applied", "")[:10]
            if applied_date == today and job.get("status") == "applied":
                applied_today += 1
                cat = job.get("category", "uncategorized")
                by_category[cat] = by_category.get(cat, 0) + 1

        return {
            "applied_today": applied_today,
            "pending": pending,
            "by_category": by_category,
        }

    def get_weekly_stats(self):
        """Get statistics for the current week (Monday-Sunday)."""
        today = datetime.now()
        # Start of week (Monday)
        start_of_week = today - timedelta(days=today.weekday())
        start_str = start_of_week.strftime("%Y-%m-%d")

        jobs = self._load_jobs()

        applied_this_week = 0
        by_day = {}
        by_category = {}

        for job in jobs:
            applied_date = job.get("date_applied", "")[:10]
            if applied_date >= start_str and job.get("status") == "applied":
                applied_this_week += 1
                by_day[applied_date] = by_day.get(applied_date, 0) + 1
                cat = job.get("category", "uncategorized")
                by_category[cat] = by_category.get(cat, 0) + 1

        return {
            "applied_this_week": applied_this_week,
            "by_day": by_day,
            "by_category": by_category,
        }

    def get_total_stats(self):
        """Get all-time statistics."""
        jobs = self._load_jobs()

        total = len(jobs)
        by_status = {}
        by_category = {}

        for job in jobs:
            status = job.get("status", "unknown")
            by_status[status] = by_status.get(status, 0) + 1
            cat = job.get("category", "uncategorized")
            by_category[cat] = by_category.get(cat, 0) + 1

        return {
            "total": total,
            "by_status": by_status,
            "by_category": by_category,
        }

    def delete_job(self, job_id):
        """Delete a job by ID."""
        jobs = self._load_jobs()
        jobs = [j for j in jobs if j["id"] != job_id]
        self._save_jobs(jobs)
