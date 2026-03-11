#!/usr/bin/env python3
"""
AI-powered post-processing for newsletter markdown files.

Cleans formatting artifacts from converted newsletter markdown: inline CSS
fragments, excessive whitespace, broken URLs, URL-encoded display text, and
Listserv macros.

Supports two client backends (tried in order):
  1. portkey-ai with AI_SANDBOX_KEY env var
  2. openai with OPENAI_API_KEY (+ optional OPENAI_BASE_URL for gateways)

Fully optional — gracefully skips if no usable client is available.

Usage:
  python scripts/ai_post_process.py _newsletters/<slug>/index.md [--dry-run] [--model MODEL] [--verbose]
  python scripts/ai_post_process.py _newsletters/*/index.md
"""
import argparse
import logging
import os
import re
import sys
from urllib.parse import unquote, urlparse, parse_qs

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
You are a markdown formatting cleanup tool. Your ONLY job is to fix formatting \
artifacts in newsletter markdown that was converted from HTML email. You must \
NEVER rewrite, summarize, or change the meaning of any content.

Fix these specific issues:
1. Remove inline CSS fragments (e.g., `color: rgb(...);`, `text-decoration: none;`, \
`font-family: ...;`, `font-size: ...;`, `background-color: ...;`)
2. Normalize excessive whitespace — collapse runs of 3+ spaces to single space, \
remove leading indentation of 4+ spaces that isn't code, remove excessive blank lines (3+ → 2)
3. Fix broken URLs — `ttp://` → `http://`, `ttps://` → `https://`
4. Decode URL-encoded display text in links (e.g., `%20` → space in link labels, \
NOT in the URL itself)
5. Remove Listserv macros and artifacts (e.g., `[LOG IN TO UNMASK]`, \
`<mailto:LISTSERV@...>`, subscription footer blocks)
6. Remove empty links (links where the display text is empty or whitespace-only)
7. Remove HTML tags that survived the markdown conversion (e.g., `<span>`, \
`<div>`, `<font>`, `<br>`)

Rules:
- Return ONLY the cleaned markdown, nothing else
- Do NOT add any commentary, explanations, or markdown code fences
- Do NOT rewrite sentences or change wording
- Do NOT remove or modify actual content, links, or images
- Preserve all markdown structure (headings, lists, links, images, blockquotes)
- Preserve line breaks that separate logical sections
"""

DEFAULT_MODEL = "gpt-4o-mini"
CHUNK_THRESHOLD = 100000  # ~25K tokens
REQUEST_TIMEOUT = 300  # seconds per API call


def split_front_matter(content):
    """Split Jekyll front matter from body content.

    Returns (front_matter, body) where front_matter includes the --- delimiters.
    If no valid front matter is found, returns ('', content).
    """
    if not content.startswith('---'):
        return '', content

    # Find the closing ---
    end_idx = content.find('---', 3)
    if end_idx == -1:
        return '', content

    # Include the closing --- and the newline after it
    end_idx = content.find('\n', end_idx)
    if end_idx == -1:
        # Front matter takes up the entire file
        return content, ''

    front_matter = content[:end_idx + 1]
    body = content[end_idx + 1:]
    return front_matter, body


def _unwrap_safelinks(url):
    """Extract the real URL from a Microsoft Safe Links wrapper.

    Safe Links format:
      https://nam12.safelinks.protection.outlook.com/?url=<encoded>&data=...&sdata=...&reserved=0
    Returns the unwrapped URL, or the original if not a Safe Link.
    """
    try:
        parsed = urlparse(url)
        if 'safelinks.protection.outlook.com' not in parsed.hostname:
            return url
        qs = parse_qs(parsed.query)
        real_url = qs.get('url', [None])[0]
        return real_url if real_url else url
    except Exception:
        return url


def sanitize_body(body):
    """Apply deterministic (non-AI) fixes to newsletter markdown body.

    Handles mechanical cleanup that doesn't need AI judgment:
    1. Unwrap Microsoft Safe Links to their real URLs
    2. Join multi-line markdown link text [foo\\n   bar](url) → [foo bar](url)
    3. Fix broken URL schemes: ttp:// → http://, ttps:// → https://
    4. Collapse runs of 3+ spaces to single space (outside code blocks)
    5. Remove excessive blank lines (3+ → 2)
    6. Remove empty markdown links [](url) and [ ](url)
    7. Remove Listserv footer lines
    8. Strip <code></code> tags (keep inner content)
    """
    # 1. Unwrap Safe Links — match full URLs in markdown link syntax ](url)
    def _replace_safelink(m):
        return _unwrap_safelinks(m.group(0))

    body = re.sub(
        r'https?://[a-z0-9]+\.safelinks\.protection\.outlook\.com/\?[^\s\)]+',
        _replace_safelink, body
    )

    # 2. Join multi-line link text: [text\n   more text](url)
    #    Repeatedly apply until stable (handles deeply wrapped links)
    for _ in range(10):
        prev = body
        body = re.sub(
            r'\[([^\]]*?)\n\s+([^\]]*?)\]',
            lambda m: '[' + m.group(1).rstrip() + ' ' + m.group(2).lstrip() + ']',
            body
        )
        if body == prev:
            break

    # 3. Fix broken URL schemes
    body = re.sub(r'(?<!\w)ttp://', 'http://', body)
    body = re.sub(r'(?<!\w)ttps://', 'https://', body)

    # 4. Collapse excessive inline whitespace (3+ spaces → single)
    #    but preserve lines that start with 4 spaces (code blocks)
    lines = body.split('\n')
    for i, line in enumerate(lines):
        if not line.startswith('    '):
            lines[i] = re.sub(r'  {2,}', ' ', line)
    body = '\n'.join(lines)

    # 5. Collapse 3+ consecutive blank lines → 2
    body = re.sub(r'\n{4,}', '\n\n\n', body)

    # 6. Remove empty links: [](url) or [ ](url)
    body = re.sub(r'\[\s*\]\([^\)]+\)', '', body)

    # 7. Remove Listserv footer lines (with or without markdown links)
    body = re.sub(
        r'\n*This list is maintained by.*?hosted by.*?LISTSERV.*?\.?\s*$',
        '', body, flags=re.MULTILINE
    )

    # 8. Strip <code></code> tags, keeping inner content
    body = re.sub(r'</?code>', '', body, flags=re.IGNORECASE)

    return body


def get_client():
    """Create an OpenAI-compatible chat client.

    Tries backends in order:
      1. portkey-ai with AI_SANDBOX_KEY
      2. openai with OPENAI_API_KEY (+ optional OPENAI_BASE_URL)

    Returns a client with a chat.completions.create() interface, or None.
    """
    # Try Portkey first
    api_key = os.environ.get('AI_SANDBOX_KEY')
    if api_key:
        try:
            from portkey_ai import Portkey
            logger.info("Using Portkey AI client")
            return Portkey(api_key=api_key)
        except ImportError:
            logger.debug("portkey-ai not installed, trying openai fallback")

    # Try OpenAI (works with any OpenAI-compatible endpoint via OPENAI_BASE_URL)
    openai_key = os.environ.get('OPENAI_API_KEY')
    if openai_key:
        try:
            from openai import OpenAI
            base_url = os.environ.get('OPENAI_BASE_URL')
            kwargs = {'api_key': openai_key}
            if base_url:
                kwargs['base_url'] = base_url
                logger.info(f"Using OpenAI client → {base_url}")
            else:
                logger.info("Using OpenAI client")
            return OpenAI(**kwargs)
        except ImportError:
            logger.info("openai not installed — skipping AI post-processing")
            return None

    logger.info("No AI API key set (AI_SANDBOX_KEY or OPENAI_API_KEY) — skipping")
    return None


def _chunk_body(body, threshold=CHUNK_THRESHOLD):
    """Split body into chunks at paragraph boundaries if it exceeds threshold.

    Returns a list of strings.
    """
    if len(body) <= threshold:
        return [body]

    chunks = []
    paragraphs = body.split('\n\n')
    current = []
    current_len = 0

    for para in paragraphs:
        para_len = len(para) + 2  # account for the \n\n separator
        if current_len + para_len > threshold and current:
            chunks.append('\n\n'.join(current))
            current = [para]
            current_len = para_len
        else:
            current.append(para)
            current_len += para_len

    if current:
        chunks.append('\n\n'.join(current))

    return chunks


def process_body(body, client, model=None, verbose=False):
    """Send body text through the AI for cleanup.

    Handles chunking for very long content. Returns cleaned body text.
    """
    model = model or os.environ.get('NEWSLETTER_AI_MODEL', DEFAULT_MODEL)
    chunks = _chunk_body(body)

    if verbose and len(chunks) > 1:
        logger.info(f"  Content split into {len(chunks)} chunks")

    cleaned_chunks = []
    for i, chunk in enumerate(chunks):
        if verbose and len(chunks) > 1:
            logger.info(f"  Processing chunk {i + 1}/{len(chunks)}")

        response = client.chat.completions.create(
            model=model,
            temperature=0.0,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": chunk},
            ],
            timeout=REQUEST_TIMEOUT,
        )
        cleaned_chunks.append(response.choices[0].message.content)

    return '\n\n'.join(cleaned_chunks)


def process_file(filepath, dry_run=False, model=None, verbose=False, client=None,
                 sanitize_only=False):
    """Process a single newsletter markdown file.

    Runs deterministic sanitize_body() first, then optionally AI cleanup.

    Args:
        filepath: Path to the newsletter markdown file.
        dry_run: If True, don't modify the file.
        model: AI model to use (default from env or DEFAULT_MODEL).
        verbose: Print detailed progress.
        client: Pre-created AI client. If None and not sanitize_only, creates one.
        sanitize_only: If True, only run mechanical fixes (no AI).

    Returns True if the file was processed (or would be in dry-run), False if skipped.
    """
    if not sanitize_only:
        if client is None:
            client = get_client()
        if client is None:
            return False

    if not os.path.exists(filepath):
        logger.warning(f"File not found: {filepath}")
        return False

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    front_matter, body = split_front_matter(content)

    if not body.strip():
        if verbose:
            logger.info(f"  Skipping — empty body")
        return False

    # Always run deterministic fixes first
    cleaned_body = sanitize_body(body)

    # Optionally run AI cleanup on the sanitized body
    if not sanitize_only and client is not None:
        cleaned_body = process_body(cleaned_body, client, model=model, verbose=verbose)

    if cleaned_body == body:
        if verbose:
            logger.info(f"  No changes")
        return False

    if dry_run:
        logger.info(f"  [DRY RUN] Would update")
        if verbose:
            print("--- Cleaned body preview (first 500 chars) ---")
            print(cleaned_body[:500])
            print("---")
        return True

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(front_matter + cleaned_body)

    logger.info(f"  Updated")
    return True


def main():
    parser = argparse.ArgumentParser(
        description='AI-powered post-processing for newsletter markdown'
    )
    parser.add_argument('files', nargs='+', help='Newsletter markdown file(s) to process')
    parser.add_argument('--dry-run', action='store_true',
                        help='Preview changes without modifying files')
    parser.add_argument('--model', default=None,
                        help=f'AI model to use (default: {DEFAULT_MODEL}, or NEWSLETTER_AI_MODEL env var)')
    parser.add_argument('--verbose', action='store_true',
                        help='Print detailed progress')
    parser.add_argument('--sanitize-only', action='store_true',
                        help='Only run mechanical fixes (no AI). No API key needed.')
    args = parser.parse_args()

    # Configure logging — force unbuffered output
    level = logging.DEBUG if args.verbose else logging.INFO
    handler = logging.StreamHandler(sys.stdout)
    handler.flush = lambda: sys.stdout.flush()
    logging.basicConfig(level=level, format='%(message)s', handlers=[handler])

    # Suppress noisy HTTP request logging from openai/httpx
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    # Create client once (skip if sanitize-only)
    client = None
    if not args.sanitize_only:
        client = get_client()
        if client is None:
            sys.exit(0)

    success = 0
    failed = 0
    total = len(args.files)

    for i, filepath in enumerate(args.files, 1):
        if total > 1:
            logger.info(f"[{i}/{total}] {filepath}")
            sys.stdout.flush()
        try:
            result = process_file(filepath, dry_run=args.dry_run,
                                  model=args.model, verbose=args.verbose,
                                  client=client,
                                  sanitize_only=args.sanitize_only)
            if result:
                success += 1
        except Exception as e:
            logger.error(f"  ERROR: {e}")
            failed += 1
        sys.stdout.flush()

    if total > 1:
        logger.info(f"\nProcessed: {success}, Failed: {failed}, Total: {total}")

    if failed > 0:
        sys.exit(1)


if __name__ == '__main__':
    main()
