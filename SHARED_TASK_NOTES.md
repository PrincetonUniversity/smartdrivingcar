# Shared Task Notes

## Current State

All core features are now implemented and tested. Run tests with:
```bash
source .venv/bin/activate && python -m pytest tests/ azure/functions/tests/ -v
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
- 49 unit tests for scripts in `tests/`
- 27 unit tests for Azure Function in `azure/functions/tests/`

### 5. Example Email
- **`example-email/sample-newsletter.eml`**: Sample email for testing

### 6. Azure Auto-Publishing Pipeline
- **Azure Function** (`azure/functions/`): HTTP-triggered Python function that cleans newsletter HTML and converts to Jekyll markdown
- **Logic App** (`azure/logic-app/`): ARM templates — polls O365 mail folder, calls Function, dispatches to GitHub
- **Deploy scripts** (`azure/deploy/`):
  - `deploy.sh` — Full interactive deployment (resource group, storage, function app, connections, logic app)
  - `update.sh` — Republish function code or redeploy logic app workflow
  - `teardown.sh` — Remove all Azure resources
- **GitHub workflow** (`.github/workflows/receive-newsletter.yml`): Receives dispatch, writes newsletter file, commits and pushes
- **Deduplication**: Function checks `known_slugs`; workflow checks filesystem for existing `_newsletters/{slug}/index.md`

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

### Manual/Git-Push Pipeline
```
inbox/*.eml → process_inbox.py → import_newsletter.py → clean_newsletter.py → _newsletters/
                     ↓
               logs/newsletter_processing.log
```

### Azure Auto-Publishing Pipeline
```
Listserv → O365 folder → Logic App (5-min poll) → Azure Function (process)
  → GitHub repository_dispatch → receive-newsletter.yml (commit) → build.yml (deploy)
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

## Azure Deploy / Update / Teardown

```bash
# Deploy all Azure resources (interactive)
./azure/deploy/deploy.sh

# Partial deploys
./azure/deploy/deploy.sh --function-only
./azure/deploy/deploy.sh --connections-only
./azure/deploy/deploy.sh --logic-app-only

# Update after code changes
./azure/deploy/update.sh                  # update function + logic app
./azure/deploy/update.sh --function-only   # republish function code only
./azure/deploy/update.sh --logic-app-only  # redeploy workflow only

# Tear down all resources
./azure/deploy/teardown.sh
./azure/deploy/teardown.sh --yes  # skip confirmation
./azure/deploy/teardown.sh --resource-group rg-smartdrivingcar
```

## Future Extension Ideas

1. **Content enrichment**: Auto-extract metadata (author, categories, tags)
2. **Image handling**: Download and host images locally, or convert to base64
3. **RSS feed generation**: Create RSS from processed newsletters
4. **Search indexing**: Add full-text search to the archive
5. **Notification system**: Slack/email alerts on processing success/failure
6. **Preview mode**: Generate preview before committing
7. **Batch processing**: Process multiple emails in single workflow run with summary
