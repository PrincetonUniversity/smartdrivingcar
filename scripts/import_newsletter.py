#!/usr/bin/env python3
"""Import a raw email (MIME .eml or pasted body) into a Jekyll newsletter markdown file.
Usage:
  python scripts/import_newsletter.py --date 2025-08-22 --title "My Issue Title" --input email.eml
If --input omitted, reads stdin.
Extracts simple HTML -> Markdown (very naive) and writes to _newsletters/YYYY-MM-DD-slug.md
Dependencies: only Python stdlib.
"""
import argparse, re, sys, os, datetime, email, unicodedata
from email import policy
from email.parser import BytesParser

RE_TAGS = re.compile(r'<(script|style)[^>]*>.*?</\\1>', re.I | re.S)
RE_HTML_TAG = re.compile(r'<[^>]+>')


def slugify(text: str) -> str:
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'[^a-zA-Z0-9]+', '-', text).strip('-').lower()
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--date', help='Issue date (YYYY-MM-DD). Default: today', default=datetime.date.today().isoformat())
    ap.add_argument('--title', required=True, help='Issue title (without date)')
    ap.add_argument('--input', help='Path to .eml or .html or .txt file; else stdin')
    ap.add_argument('--raw-html', action='store_true', help='Treat input as raw HTML even if looks like plain text')
    args = ap.parse_args()

    date = args.date
    try:
        datetime.date.fromisoformat(date)
    except ValueError:
        ap.error('Invalid --date format, expected YYYY-MM-DD')

    if args.input:
        ext = os.path.splitext(args.input)[1].lower()
        if ext == '.eml':
            raw = extract_body_from_eml(args.input)
        else:
            with open(args.input, 'r', encoding='utf-8', errors='ignore') as f:
                raw = f.read()
    else:
        raw = sys.stdin.read()

    if not args.raw_html and '<html' not in raw.lower() and '<p' not in raw.lower():
        # Assume plain text already roughly Markdown
        md = raw.strip() + '\n'
    else:
        md = html_to_markdown(raw)

    slug = slugify(args.title)
    filename = f"_newsletters/{date}-{slug}.md"
    if os.path.exists(filename):
        print(f"Refusing to overwrite existing file: {filename}", file=sys.stderr)
        sys.exit(1)

    front_matter = f"---\nlayout: newsletter\ntitle: {args.title}\ndate: {date}\n---\n\n"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(front_matter + md)
    print(f"Created {filename}")

if __name__ == '__main__':
    main()
