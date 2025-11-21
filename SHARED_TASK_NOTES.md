# Shared Task Notes

## Current State

Tests created in `tests/` for `import_newsletter.py` and `clean_newsletter.py`. Run with `python3 -m pytest tests/ -v` (requires pytest).

## Next Actions (Priority Order)

1. **Create GitHub Actions workflow for email processing** - Missing the core automation
   - Watch a configurable inbox directory for `.eml` files
   - Trigger processing when new emails arrive
   - Use `import_newsletter.py` and `clean_newsletter.py`

2. **Implement inbox cleanup and git history scrubbing**
   - After successful processing, delete source `.eml`
   - Remove from git history (use `git filter-branch` or BFG)
   - Log success/failure

3. **Add example-email folder** with sample `.eml` files for testing

4. **Create configuration file** for:
   - Inbox directory path
   - Custom markdown transformations
   - Footer removal patterns

## Architecture Notes

- `import_newsletter.py`: Extracts HTML from .eml, converts to markdown, creates Jekyll post
- `clean_newsletter.py`: HTML cleaning (removes styles, comments, footers, normalizes quotes)
- Extensibility for transformations is partially there via `--htmlsrc` flag but needs formalization

## Gaps vs. Goal

- No workflow to auto-process emails on arrival
- No inbox directory configuration
- No git history scrubbing
- No processing logs
- No example emails for testing
