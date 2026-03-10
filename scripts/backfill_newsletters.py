#!/usr/bin/env python3
"""
Backfill old newsletters from Listserv GETPOST wrapper emails.

Listserv's GETPOST command returns wrapper .eml emails containing the original
newsletter as a nested message/rfc822 attachment. This script unwraps those
and feeds the inner emails through the existing import pipeline.

Usage:
  python scripts/backfill_newsletters.py [--dir backfill/] [--dry-run] [--limit N] [--verbose]
"""
import argparse
import email
import glob
import os
import re
import subprocess
import sys
import tempfile
import unicodedata
from email import policy
from email.parser import BytesParser


def extract_inner_messages(eml_path):
    """Parse a wrapper .eml and extract nested message/rfc822 attachments.

    Returns a list of email.message.Message objects (the inner emails).
    """
    with open(eml_path, 'rb') as f:
        msg = BytesParser(policy=policy.default).parse(f)

    inner_messages = []
    for part in msg.walk():
        if part.get_content_type() == 'message/rfc822':
            # The payload of a message/rfc822 part is a list containing the inner message
            payload = part.get_payload()
            if isinstance(payload, list):
                inner_messages.extend(payload)
            else:
                inner_messages.append(payload)

    return inner_messages


def _get_part_content(part):
    """Get text content from an email part, handling both legacy and new-style APIs."""
    if hasattr(part, 'get_content') and callable(part.get_content):
        try:
            return part.get_content()
        except Exception:
            pass
    # Legacy MIMEText / Message objects
    payload = part.get_payload(decode=True)
    if payload:
        charset = part.get_content_charset() or 'utf-8'
        return payload.decode(charset, errors='replace')
    return ''


def extract_html_from_message(msg):
    """Extract HTML body from an email message object.

    Mirrors the logic in import_newsletter.py:extract_body_from_eml but works
    on an already-parsed message object instead of a file path.
    """
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == 'text/html':
                return _get_part_content(part)
        for part in msg.walk():
            if part.get_content_type() == 'text/plain':
                return _get_part_content(part)
    else:
        return _get_part_content(msg)
    return ''


def predict_slug(html_body):
    """Predict the newsletter slug from HTML body content.

    Uses the same logic as import_newsletter.py to determine what slug
    would be generated, for dedup checking.

    Returns the predicted slug string, or None if prediction fails.
    """
    # Import slug-related functions from import_newsletter
    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, scripts_dir)
    try:
        from import_newsletter import extract_first_date, extract_author_slug, slugify
    finally:
        sys.path.pop(0)

    author_slug = extract_author_slug(html_body)
    if author_slug:
        return author_slug

    # Fall back to date-based slug
    first_date = extract_first_date(html_body)
    if first_date:
        # Parse the date the same way import_newsletter.py does
        month_map = {
            'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
            'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12,
        }
        date_match = re.search(r'([A-Za-z]+)\.\s*(\d{1,2}),\s*(\d{4})', first_date)
        if date_match:
            month_str = date_match.group(1).lower()
            month_num = month_map.get(month_str, 1)
            day = int(date_match.group(2))
            year = int(date_match.group(3))
            iso_date = f"{year}-{month_num:02d}-{day:02d}"
            title_slug = slugify(first_date)
            return f"{iso_date}-{title_slug}"

    return None


def newsletter_exists(slug):
    """Check if a newsletter with the given slug already exists."""
    if not slug:
        return False
    newsletter_path = os.path.join('_newsletters', slug, 'index.md')
    return os.path.exists(newsletter_path)


def write_message_to_tempfile(msg):
    """Write an email message object to a temporary .eml file.

    Returns the path to the temp file. Caller is responsible for cleanup.
    """
    fd, tmp_path = tempfile.mkstemp(suffix='.eml')
    try:
        with os.fdopen(fd, 'wb') as f:
            f.write(msg.as_bytes())
    except Exception:
        os.close(fd)
        raise
    return tmp_path


def process_inner_message(msg, wrapper_path, dry_run=False, verbose=False):
    """Process a single inner email message through the import pipeline.

    Returns a dict with keys: 'status' ('processed', 'skipped', 'failed'), 'slug', 'reason'.
    """
    html_body = extract_html_from_message(msg)
    if not html_body or not html_body.strip():
        return {
            'status': 'skipped',
            'slug': None,
            'reason': 'no HTML body in inner message'
        }

    # Predict slug for dedup check
    slug = predict_slug(html_body)

    if slug and newsletter_exists(slug):
        return {
            'status': 'skipped',
            'slug': slug,
            'reason': f'already exists: _newsletters/{slug}/index.md'
        }

    if dry_run:
        return {
            'status': 'skipped',
            'slug': slug,
            'reason': 'dry run'
        }

    # Write inner message to temp file and call import_newsletter.py
    tmp_path = None
    try:
        tmp_path = write_message_to_tempfile(msg)
        scripts_dir = os.path.dirname(os.path.abspath(__file__))
        import_script = os.path.join(scripts_dir, 'import_newsletter.py')

        cmd = [
            sys.executable,
            import_script,
            '--input', tmp_path,
            '--htmlsrc'
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())

        if result.returncode == 0:
            if verbose and result.stdout:
                print(f"  {result.stdout.strip()}")
            return {
                'status': 'processed',
                'slug': slug,
                'reason': result.stdout.strip() if result.stdout else 'success'
            }
        else:
            error_msg = result.stderr.strip() if result.stderr else 'unknown error'
            return {
                'status': 'failed',
                'slug': slug,
                'reason': error_msg
            }

    except Exception as e:
        return {
            'status': 'failed',
            'slug': slug,
            'reason': str(e)
        }
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)


def process_wrapper_eml(eml_path, dry_run=False, verbose=False):
    """Process a single wrapper .eml file.

    Returns a list of result dicts from process_inner_message.
    """
    results = []

    try:
        inner_messages = extract_inner_messages(eml_path)
    except Exception as e:
        return [{
            'status': 'failed',
            'slug': None,
            'reason': f'failed to parse wrapper: {e}'
        }]

    if not inner_messages:
        if verbose:
            print(f"  WARNING: no message/rfc822 attachment found in {eml_path}")
        return [{
            'status': 'skipped',
            'slug': None,
            'reason': 'no message/rfc822 attachment'
        }]

    for i, msg in enumerate(inner_messages):
        if verbose and len(inner_messages) > 1:
            print(f"  Inner message {i + 1}/{len(inner_messages)}")
        result = process_inner_message(msg, eml_path, dry_run=dry_run, verbose=verbose)
        results.append(result)

    return results


def main():
    parser = argparse.ArgumentParser(
        description='Backfill newsletters from Listserv GETPOST wrapper emails'
    )
    parser.add_argument('--dir', default='backfill/',
                        help='Directory containing wrapper .eml files (default: backfill/)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be processed without writing files')
    parser.add_argument('--limit', type=int, default=0,
                        help='Process at most N files (0 = unlimited)')
    parser.add_argument('--verbose', action='store_true',
                        help='Print detailed progress')
    args = parser.parse_args()

    backfill_dir = args.dir

    if not os.path.isdir(backfill_dir):
        print(f"ERROR: directory not found: {backfill_dir}")
        sys.exit(1)

    # Glob and sort .eml files for deterministic ordering
    eml_files = sorted(glob.glob(os.path.join(backfill_dir, '*.eml')))

    if not eml_files:
        print(f"No .eml files found in {backfill_dir}")
        sys.exit(0)

    if args.limit > 0:
        eml_files = eml_files[:args.limit]

    if args.dry_run:
        print("DRY RUN — no files will be written\n")

    processed = 0
    skipped = 0
    failed = 0

    for eml_path in eml_files:
        print(f"Processing: {eml_path}")
        results = process_wrapper_eml(eml_path, dry_run=args.dry_run, verbose=args.verbose)

        for result in results:
            status = result['status']
            slug_info = f" [{result['slug']}]" if result['slug'] else ""
            reason = result['reason']

            if status == 'processed':
                processed += 1
                print(f"  OK{slug_info}: {reason}")
            elif status == 'skipped':
                skipped += 1
                print(f"  SKIP{slug_info}: {reason}")
            elif status == 'failed':
                failed += 1
                print(f"  FAIL{slug_info}: {reason}")

    print(f"\nSummary: {processed} processed, {skipped} skipped, {failed} failed")
    print(f"Total wrapper files: {len(eml_files)}")

    if failed > 0:
        sys.exit(1)


if __name__ == '__main__':
    main()
