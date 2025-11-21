#!/usr/bin/env python3
"""Import a raw email (MIME .eml or pasted body) into a Jekyll newsletter markdown file.
Usage:
  python scripts/import_newsletter.py --date 2025-08-22 --title "My Issue Title" --input email.eml
If --input omitted, reads stdin.
Extracts simple HTML -> Markdown (very naive) and writes to _newsletters/YYYY-MM-DD-slug.md
Dependencies: only Python stdlib.
"""
import argparse, re, sys, os, datetime, email, unicodedata
from importlib.util import spec_from_file_location, module_from_spec
from email import policy
from email.parser import BytesParser

RE_TAGS = re.compile(r'<(script|style)[^>]*>.*?</\1>', re.I | re.S)
RE_HTML_TAG = re.compile(r'<[^>]+>')


def slugify(text: str) -> str:
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    # Preserve dots, replace other non-alphanum (except dot) with dash
    text = re.sub(r'[^a-zA-Z0-9.]+', '-', text).strip('-').lower()
    return text or 'issue'


def html_to_markdown(html: str) -> str:
    html = RE_TAGS.sub('', html)
    # Replace <br> and paragraphs with line breaks
    html = re.sub(r'<\s*br\s*/?>', '\n', html, flags=re.I)
    html = re.sub(r'</p>', '\n\n', html, flags=re.I)
    html = re.sub(r'<p[^>]*>', '', html, flags=re.I)
    # Headings
    for i in range(6, 0, -1):
        html = re.sub(fr'<h{i}[^>]*>(.*?)</h{i}>', lambda m: '\n' + '#' * i + ' ' + m.group(1).strip() + '\n\n', html, flags=re.I | re.S)
    # Links
    html = re.sub(r'<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', lambda m: f'[{m.group(2).strip()}]({m.group(1)})', html, flags=re.I | re.S)
    # Lists
    html = re.sub(r'<li[^>]*>(.*?)</li>', lambda m: f'* {m.group(1).strip()}\n', html, flags=re.I | re.S)
    html = re.sub(r'</ul>|</ol>', '\n', html, flags=re.I)
    html = RE_HTML_TAG.sub('', html)
    # Unescape basic entities
    html = html.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    # Collapse whitespace
    lines = [l.rstrip() for l in html.splitlines()]
    out_lines = []
    for line in lines:
        if line.strip():
            out_lines.append(line)
        elif out_lines and out_lines[-1] != '':
            out_lines.append('')
    return '\n'.join(out_lines).strip() + '\n'


def extract_body_from_eml(path: str) -> str:
    with open(path, 'rb') as f:
        msg = BytesParser(policy=policy.default).parse(f)
    # Prefer HTML part
    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            if ctype == 'text/html':
                return part.get_content()
        for part in msg.walk():
            if part.get_content_type() == 'text/plain':
                return part.get_content()
    else:
        return msg.get_content()
    return ''


def extract_first_date(text):
    # Match formats like "Thursday, Aug. 28, 2025" or similar
    date_regex = re.compile(r'(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),?\s+[A-Z][a-z]+\.\s+\d{1,2},\s+\d{4}', re.IGNORECASE)
    match = date_regex.search(text)
    if match:
        return match.group(0)
    return None

def remove_first_date_and_link(html, date_str):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    # Remove link from first date occurrence
    found = False
    for tag in soup.find_all(string=True):
        if not found and date_str in tag:
            parent = tag.parent
            if parent.name == 'a':
                # Replace <a> with just the text
                parent.replace_with(date_str)
                found = True
            else:
                tag.replace_with(tag.replace(date_str, ''))
                found = True
    # Remove any remaining date_str
    html = str(soup)
    html = html.replace(date_str, '')
    return html

def remove_sdc_line(text):
    lines = text.splitlines()
    new_lines = []
    for line in lines:
        # Remove any line that links to smartdrivingcar.com (markdown or HTML)
        if re.search(r'(\[.*?\]\(https?://smartdrivingcar\.com.*?\))|(<a[^>]*href=["\']https?://smartdrivingcar\.com.*?>.*?</a>)|smartdrivingcar\.com', line, re.IGNORECASE):
            continue
        new_lines.append(line)
    return '\n'.join(new_lines)

def add_margins_to_markdown(md):
    # Do not wrap in a div; let layout/CSS handle margins
    return md.strip() + '\n'

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--date', help='Issue date (YYYY-MM-DD). If omitted, extracted from source or today.')
    ap.add_argument('--title', help='Issue title (without date). If omitted, uses date.')
    ap.add_argument('--input', help='Path to .eml or .html or .txt file; else stdin')
    ap.add_argument('--raw-html', action='store_true', help='Treat input as raw HTML even if looks like plain text')
    ap.add_argument('--htmlsrc', action='store_true', help='Clean HTML input using newsletter cleaning logic')
    args = ap.parse_args()

    date = args.date
    if args.input:
        ext = os.path.splitext(args.input)[1].lower()
        if ext == '.eml':
            raw = extract_body_from_eml(args.input)
        else:
            with open(args.input, 'r', encoding='utf-8', errors='ignore') as f:
                raw = f.read()
    else:
        raw = sys.stdin.read()

    # Extract first date from source
    first_date = extract_first_date(raw)

    # Set date value
    if args.date:
        date_for_yaml = args.date
    elif first_date:
        date_for_yaml = first_date
    else:
        date_for_yaml = datetime.date.today().isoformat()

    # Set title value
    if args.title:
        title_for_yaml = args.title
    else:
        title_for_yaml = date_for_yaml

    # Remove first date and link if present
    if first_date:
        raw = remove_first_date_and_link(raw, first_date)

    # Remove SmartDrivingCar.com line from first 10 lines
    raw = remove_sdc_line(raw)

    # If --htmlsrc is set, clean HTML using clean_newsletter.py
    if args.htmlsrc:
        clean_path = os.path.join(os.path.dirname(__file__), 'clean_newsletter.py')
        spec = spec_from_file_location('clean_newsletter', clean_path)
        clean_mod = module_from_spec(spec)
        spec.loader.exec_module(clean_mod)
        raw = clean_mod.clean_newsletter_html(raw)

    if not args.raw_html and '<html' not in raw.lower() and '<p' not in raw.lower():
        md = raw.strip() + '\n'
    else:
        md = html_to_markdown(raw)

    # Add left/right margins for readability
    md = add_margins_to_markdown(md)

    slug = slugify(title_for_yaml)

    # Extract month, day, year from date_for_yaml
    # Try to match "Aug. 14, 2025" or similar
    month_map = {
        'january': '1', 'february': '2', 'march': '3', 'april': '4', 'may': '5', 'june': '6',
        'july': '7', 'august': '8', 'september': '9', 'october': '10', 'november': '11', 'december': '12',
        'jan': '1', 'feb': '2', 'mar': '3', 'apr': '4', 'may': '5', 'jun': '6',
        'jul': '7', 'aug': '8', 'sep': '9', 'oct': '10', 'nov': '11', 'dec': '12',
        'jan.': '1', 'feb.': '2', 'mar.': '3', 'apr.': '4', 'may.': '5', 'jun.': '6',
        'jul.': '7', 'aug.': '8', 'sep.': '9', 'oct.': '10', 'nov.': '11', 'dec.': '12',
    }
    date_match = re.search(r'([A-Za-z]+)\.\s*(\d{1,2}),\s*(\d{4})', date_for_yaml)
    if date_match:
        month_str = date_match.group(1).lower()
        month_num = month_map.get(month_str, month_str)
        day = date_match.group(2)
        year = date_match.group(3)[-2:] # last two digits
        url_date = f"{month_num}.{day}.{year}"
    else:
        # fallback to ISO
        try:
            dt = datetime.datetime.strptime(date_for_yaml, "%Y-%m-%d")
            url_date = f"{dt.month}.{dt.day}.{str(dt.year)[-2:]}"
        except Exception:
            url_date = "unknown"

    # For permalink, use dots in the date portion (e.g., /title-8.14.25/)
    permalink_dir = f"{slug}-{url_date.replace('-', '.')}"
    permalink = f"/{permalink_dir}/"

    # Create directory for newsletter edition
    newsletter_dir = os.path.join("_newsletters", permalink_dir)
    os.makedirs(newsletter_dir, exist_ok=True)
    filename = os.path.join(newsletter_dir, "index.md")

    front_matter = f"---\nlayout: newsletter\ntitle: {title_for_yaml}\ndate: {date_for_yaml}\npermalink: {permalink}\n---\n\n"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(front_matter + md)
    print(f"Created {filename}")

if __name__ == '__main__':
    main()
