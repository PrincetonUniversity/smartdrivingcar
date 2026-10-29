# SmartDrivingCar Site

Static Jekyll site for Prof. Alain Kornhauser's [smartdrivingcar.com](https://smartdrivingcar.com).

## Project Structure

```
smartdrivingcar/
├── _config.yml              # Main Jekyll configuration
├── _config_local.yml        # Local development overrides
├── _config_preview.yml      # Preview/staging overrides
├── _config_prod.yml         # Production overrides
├── _includes/
│   ├── header.html          # Site header and navigation
│   └── footer.html          # Site footer
├── _layouts/
│   ├── default.html         # Base page layout
│   └── newsletter.html      # Newsletter issue layout
├── _newsletters/            # Newsletter collection (markdown files)
├── assets/
│   ├── css/site.css         # Main stylesheet
│   └── img/                  # Site images
├── config/
│   └── newsletter_config.yml # Newsletter processing configuration
├── example-email/           # Sample .eml files for testing
├── inbox/                   # Drop .eml files here for processing (full emails)
├── import/                  # Drop .html files here for processing (HTML body only)
├── newsletter/
│   └── index.md             # Newsletter archive listing page
├── scripts/
│   ├── import_newsletter.py # Convert .eml to Jekyll markdown
│   ├── clean_newsletter.py  # HTML cleaning utilities
│   └── process_inbox.py     # Batch process inbox emails
├── tests/                   # Unit tests for scripts
├── azure/
│   ├── functions/           # Azure Function App (newsletter processing)
│   │   ├── function_app.py  # Entry point
│   │   ├── process_newsletter.py  # HTTP handler
│   │   ├── newsletter_processor.py # Pure processing logic
│   │   └── tests/           # Function tests (27 tests)
│   ├── logic-app/           # ARM templates for Logic App workflow
│   └── deploy/              # Deploy, update, and teardown scripts
├── .github/workflows/
│   ├── build.yml            # Build and deploy to GitHub Pages
│   ├── process-newsletters.yml # Auto-process emails in inbox
│   └── receive-newsletter.yml  # Receive from Azure pipeline
├── index.md                 # Homepage
├── subscribe.md             # Newsletter subscription page
└── podcast/                 # Podcast content
```

## Run Locally (Docker)

Build image (only needed when Gem dependencies change):

```bash
docker build -t smartdrivingcar-site .
```

Run container, mapping port 4040 and mounting source for live edits:

```bash
docker run --rm -it -p 4040:4000 -v "$(pwd)":/site smartdrivingcar-site
```

Visit: http://localhost:4040/

## Deployment (GitHub Pages)

This site uses GitHub Actions for deployment instead of the default GitHub Pages build.

1. Push repository to GitHub.
2. Go to **Settings → Pages**.
3. Under **Build and deployment**, set **Source** to **GitHub Actions**.
4. The `build.yml` workflow will automatically build and deploy on push to `main`.

The publishing workflow builds the production configuration for the custom domain. Local and preview modes remain available through the Makefile.

All publishing entry points share the `pages-deploy` concurrency group and explicitly invoke the reusable deployment workflow.

## Newsletter Workflow

The supported pipeline reuses the existing authorized Azure Outlook and GitHub connections, reconciles retained messages in the configured newsletter folder, and publishes through an explicit, verified GitHub Pages deployment. Prof. Kornhauser continues sending to `smartdrivingcars@princeton.edu` with no extra publishing step.

**Administrator setup is required before enabling the scheduled reconciler.** Follow the [improvement plan and setup runbook](docs/newsletter-publishing.md) for reproducible Bicep adoption, the SDC Testing folder probe and isolated preview, production cutover, recovery, and optional Healthchecks.io and Resend notifications. The normal connector setup needs no new app-only Graph grant. Configuration names and empty credential placeholders are in [`example.env`](example.env).

For local imports, create a per-project virtual environment, install `requirements-dev.lock`, and run the safe renderer:

```zsh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.lock
.venv/bin/python scripts/publish_newsletter.py --eml import/ISSUE.eml --dry-run
.venv/bin/python scripts/publish_newsletter.py --eml import/ISSUE.eml
```

Review and commit only generated files in `_newsletters/` and `newsletter/`. Raw email inputs are ignored by Git. Existing curated issues are never overwritten automatically.

Run CI checks locally with `docker-compose run --build --rm tests` or `./pipeline/test.sh`. The Docker test service has no network access and runs lint, format, type checks, and verbose tests. All Python packages, Ruby gems, container images, and publishing actions are pinned.

Use `azure/connector/deploy.zsh --dry-run` to inspect the existing-resource deployment. Test mode never commits newsletter content or publishes Pages. The original Azure arrival-trigger path is retained as an opt-in fallback. Its trigger-array bug is fixed in the template, and its GitHub receiver now validates payloads and deploys explicitly. See the runbook before enabling `NEWSLETTER_LEGACY_ENABLED`.

### Backfilling Old Newsletters

To bulk-import past newsletters from the Listserv archive using GETPOST wrapper emails:

```bash
# 1. Place Listserv GETPOST .eml files in backfill/
mkdir -p backfill/
# copy .eml files into backfill/

# 2. Preview what would be imported (no files written)
make backfill-dry-run

# 3. Run the import (skips duplicates automatically)
make backfill

# 4. Or use the script directly with options
python scripts/backfill_newsletters.py --dir backfill/ --limit 10 --verbose
```

The script extracts nested `message/rfc822` attachments from wrapper emails and feeds them through the existing `import_newsletter.py` pipeline. Deduplication checks `_newsletters/<slug>/index.md` before processing.

### Configuration

Newsletter processing can be configured via environment variables or `config/newsletter_config.yml`. See `SHARED_TASK_NOTES.md` for details.

## Modes & Makefile

Three run/build modes:

| Mode | Purpose | Config Files | Base URL | Docker Command |
|------|---------|--------------|----------|----------------|
| Local | Develop at `http://localhost:4040/` | `_config.yml,_config_local.yml` | (empty) | `make docker-local` |
| Preview | Simulate project site path | `_config.yml,_config_preview.yml` | `/smartdrivingcar` | `make docker-preview` |
| Production | Custom domain (smartdrivingcar.com) | `_config.yml,_config_prod.yml` | (empty) | `make docker-prod` |

Build only:
```bash
make build-preview
make build-prod
```
