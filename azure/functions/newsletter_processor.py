"""Pure processing logic for newsletter HTML → Jekyll markdown.

No Azure Functions dependency — importable for both the Function handler and tests.
"""
import re
import sys
import os
import datetime

# Import processing functions from lib/ (deployed copies) or scripts/ (dev/test fallback)
_lib_dir = os.path.join(os.path.dirname(__file__), 'lib')
_scripts_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'scripts')

if os.path.isdir(_lib_dir):
    if _lib_dir not in sys.path:
        sys.path.insert(0, _lib_dir)
else:
    _abs_scripts = os.path.abspath(_scripts_dir)
    if _abs_scripts not in sys.path:
        sys.path.insert(0, _abs_scripts)

from clean_newsletter import clean_newsletter_html
from import_newsletter import (
    extract_first_date,
    extract_author_slug,
    remove_first_date_and_link,
    remove_sdc_line,
    html_to_markdown,
    add_margins_to_markdown,
    slugify,
)

MONTH_MAP = {
    'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6,
    'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12,
    'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'jun': 6,
    'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12,
}


def parse_date_to_iso(date_str: str) -> str:
    """Convert a date string (text or ISO) to YYYY-MM-DD format."""
    # Try abbreviated month format: "Aug. 14, 2025"
    date_match = re.search(r'([A-Za-z]+)\.\s*(\d{1,2}),\s*(\d{4})', date_str)
    if date_match:
        month_str = date_match.group(1).lower()
        month_num = MONTH_MAP.get(month_str, 1)
        day = int(date_match.group(2))
        year = int(date_match.group(3))
        return f"{year}-{month_num:02d}-{day:02d}"

    # Check if already ISO format
    try:
        datetime.datetime.strptime(date_str, "%Y-%m-%d")
        return date_str
    except (ValueError, TypeError):
        pass

    # Fallback to today
    return datetime.date.today().isoformat()


def build_display_name(author_slug: str) -> str:
    """Create display title from author slug (e.g., '13.17 Irene' from '13.17-Irene-11.14.25')."""
    display_slug = re.sub(r'-\d{1,2}[.-]\d{1,2}[.-]\d{2,4}$', '', author_slug)
    return display_slug.replace('-', ' ')


def process(body_html: str, subject: str, received_date: str,
            known_slugs: list | None = None) -> dict:
    """Process newsletter HTML into Jekyll markdown with front matter.

    Returns dict with: slug, title, date, markdown, display_name, is_duplicate.
    If known_slugs is provided, sets is_duplicate=True when the computed slug
    matches an existing entry. The GitHub Actions workflow also performs its own
    filesystem-level dedup check as the authoritative gate.
    """
    # Step 1: Clean HTML
    cleaned_html = clean_newsletter_html(body_html)

    # Step 2: Extract date from content
    first_date = extract_first_date(cleaned_html)

    # Step 3: Extract author slug
    author_slug = extract_author_slug(cleaned_html)

    # Step 4: Determine date for YAML
    if first_date:
        date_for_yaml = first_date
    elif received_date:
        date_for_yaml = received_date
    else:
        date_for_yaml = datetime.date.today().isoformat()

    # Step 5: Set title
    title_for_yaml = subject if subject else date_for_yaml

    # Step 6: Remove first date and link if present
    if first_date:
        cleaned_html = remove_first_date_and_link(cleaned_html, first_date)

    # Step 7: Remove SmartDrivingCar.com self-links
    cleaned_html = remove_sdc_line(cleaned_html)

    # Step 8: Convert to markdown
    md = html_to_markdown(cleaned_html)
    md = add_margins_to_markdown(md)

    # Step 9: Parse date to ISO
    iso_date = parse_date_to_iso(date_for_yaml)

    # Step 10: Build slug
    slug_text = slugify(title_for_yaml)
    if author_slug:
        filename_base = author_slug
    else:
        filename_base = f"{iso_date}-{slug_text}"

    # Step 11: Build display name
    display_name = build_display_name(author_slug) if author_slug else ""

    # Step 12: Clean title for YAML
    clean_title = ' '.join(title_for_yaml.split())
    permalink = f"/{filename_base}/"

    # Step 13: Build front matter
    front_matter = (
        f"---\n"
        f"layout: newsletter\n"
        f'title: "{clean_title}"\n'
        f"date: {iso_date}\n"
        f"permalink: {permalink}\n"
    )
    if display_name:
        front_matter += f'display_name: "{display_name}"\n'
    front_matter += "---\n\n"

    markdown = front_matter + md

    # Check against known slugs if provided
    is_duplicate = filename_base in (known_slugs or [])

    return {
        "slug": filename_base,
        "title": clean_title,
        "date": iso_date,
        "markdown": markdown,
        "display_name": display_name,
        "is_duplicate": is_duplicate,
    }
