# Shared Task Notes

## Current State

All core features are now implemented and tested. Run tests with:
```bash
source .venv/bin/activate && python -m pytest tests/ -v
```

## Completed Features

### 1. Email Processing Pipeline
- **`scripts/import_newsletter.py`**: Extracts HTML from .eml files, converts to markdown, creates Jekyll posts
- **`scripts/clean_newsletter.py`**: Cleans HTML (removes styles, comments, footers, normalizes quotes)
- **`scripts/process_inbox.py`**: Orchestrates processing with logging and cleanup

### 2. GitHub Actions Automation
- **`.github/workflows/process-newsletters.yml`**: Triggers on push to `inbox/*.eml`
- Automatically processes emails and commits results
- Removes processed files from inbox
- Uploads processing logs as artifacts

### 3. Configuration
- **`config/newsletter_config.yml`**: Configurable inbox directory, logging, cleaning patterns

### 4. Testing
- 49 unit tests covering all modules
- Tests in `tests/` directory

### 5. Example Email
- **`example-email/sample-newsletter.eml`**: Sample email for testing

## Usage

### Manual Processing
```bash
python scripts/process_inbox.py --config config/newsletter_config.yml
```

### Processing a Single Email
```bash
python scripts/import_newsletter.py --input inbox/newsletter.eml --htmlsrc
```

### Automated Processing
1. Drop `.eml` files into `inbox/` directory
2. Commit and push
3. GitHub Actions will process and commit results

## Architecture

```
inbox/*.eml → process_inbox.py → import_newsletter.py → clean_newsletter.py → _newsletters/
                     ↓
               logs/newsletter_processing.log
```

## Configuration Options

See `config/newsletter_config.yml` for defaults. All settings can be overridden via environment variables:

| Setting | Environment Variable | Description |
|---------|---------------------|-------------|
| `inbox_directory` | `NEWSLETTER_INBOX_DIRECTORY` | Where to watch for .eml files |
| `output_directory` | `NEWSLETTER_OUTPUT_DIRECTORY` | Output for processed newsletters |
| `scrub_git_history` | `NEWSLETTER_SCRUB_GIT_HISTORY` | Remove from git history (destructive) |
| `logging.enabled` | `NEWSLETTER_LOG_ENABLED` | Enable/disable logging |
| `logging.file` | `NEWSLETTER_LOG_FILE` | Log file path |
| `logging.level` | `NEWSLETTER_LOG_LEVEL` | Log level (INFO, DEBUG, etc.) |

Additional config options: `cleaning` (footer patterns, remove patterns, replacements)

## Future Extension Ideas

1. **Content enrichment**: Auto-extract metadata (author, categories, tags)
2. **Image handling**: Download and host images locally, or convert to base64
3. **RSS feed generation**: Create RSS from processed newsletters
4. **Search indexing**: Add full-text search to the archive
5. **Notification system**: Slack/email alerts on processing success/failure
6. **Preview mode**: Generate preview before committing
7. **Batch processing**: Process multiple emails in single workflow run with summary
