"""Job categorizer module - classifies jobs based on keyword matching."""

import yaml
import os

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.yaml")


def load_config():
    """Load configuration from config.yaml."""
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)


def categorize_job(title, description, location, company):
    """
    Categorize a job based on keywords from config.

    Priority:
    1. Premium company match
    2. Remote keyword match
    3. Immigration + Dallas area
    4. Family law + Dallas area
    5. Practice area keywords regardless of location
    6. Default to None (ask user)
    """
    config = load_config()
    title_lower = (title or "").lower()
    desc_lower = (description or "").lower()
    location_lower = (location or "").lower()
    company_lower = (company or "").lower()
    combined_text = f"{title_lower} {desc_lower}"

    # 1. Check premium companies
    for premium_co in config.get("premium_companies", []):
        if premium_co.lower() in company_lower:
            return "premium"

    # 2. Check remote keywords
    remote_keywords = config["categories"].get("remote", {}).get("keywords", [])
    for kw in remote_keywords:
        if kw.lower() in combined_text or kw.lower() in location_lower:
            return "remote"

    # Check if location is Dallas area
    dallas_keywords = config.get("dallas_keywords", [])
    is_dallas = any(dk.lower() in location_lower for dk in dallas_keywords)

    # 3. Immigration + Dallas
    immigration_keywords = config["categories"].get(
        "immigration_paralegal_dallas", {}
    ).get("keywords", [])
    has_immigration = any(kw.lower() in combined_text for kw in immigration_keywords)

    if has_immigration and is_dallas:
        return "immigration_paralegal_dallas"

    # 4. Family law + Dallas
    family_keywords = config["categories"].get(
        "family_law_paralegal_dallas", {}
    ).get("keywords", [])
    has_family = any(kw.lower() in combined_text for kw in family_keywords)

    if has_family and is_dallas:
        return "family_law_paralegal_dallas"

    # 5. Practice area keywords regardless of location
    if has_immigration:
        return "immigration_paralegal_dallas"
    if has_family:
        return "family_law_paralegal_dallas"

    # 6. Check if it's a paralegal job at all
    if "paralegal" in combined_text or "legal assistant" in combined_text:
        if is_dallas:
            return "family_law_paralegal_dallas"  # default Dallas category
        return "remote"  # default generic

    return None


def get_category_display_name(category):
    """Get the display name for a category."""
    config = load_config()
    cat_config = config.get("categories", {}).get(category, {})
    return cat_config.get("display_name", category)


def get_all_categories():
    """Return list of all category keys."""
    config = load_config()
    return list(config.get("categories", {}).keys())


def match_keywords(text, category):
    """Return list of keywords from a category that match the given text."""
    config = load_config()
    cat_config = config.get("categories", {}).get(category, {})
    keywords = cat_config.get("keywords", [])
    text_lower = text.lower()
    return [kw for kw in keywords if kw.lower() in text_lower]
