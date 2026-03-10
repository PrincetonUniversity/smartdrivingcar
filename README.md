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

The workflow auto-selects production config if a `CNAME` file exists; otherwise preview config is used.

Both workflows share a concurrency group (`pages-deploy`) to prevent race conditions during deployment.

## Newsletter Workflow

The site includes an automated system for processing email newsletters.

### Automated Processing

Two input directories are supported:

- **`inbox/`** - For `.eml` files (complete emails with headers)
- **`import/`** - For `.html` files (raw HTML body only, no email headers)

1. Drop files into the appropriate directory.
2. Commit and push to `main`.
3. The `Process Newsletters` workflow will:
   - Extract and clean HTML content
   - Convert to markdown
   - Create newsletter posts in `_newsletters/`
   - Remove processed files from the source directory

### Manual Processing

```bash
python3 scripts/import_newsletter.py --date 2025-08-22 --title "Newsletter Title" --input path/to/email.eml
```

Or from clipboard (HTML):
```bash
pbpaste | python3 scripts/import_newsletter.py --date 2025-08-22 --title "Newsletter Title" --raw-html
```

### Azure Auto-Publishing Pipeline

For fully automated publishing (no manual steps after setup), the Azure pipeline processes newsletters as soon as Listserv delivers them:

```
Listserv → orfe-lists@princeton.edu (O365)
  → "SmartDrivingCars Newsletters for Processing" folder
  → Azure Logic App (polls every 5 min)
  → Azure Function (cleans HTML, converts to markdown)
  → GitHub repository_dispatch
  → receive-newsletter.yml (writes file, commits, pushes)
  → build.yml (deploys to GitHub Pages)
```

**Deduplication** is enforced at two levels:
- The Azure Function can check against a list of known slugs (optional `known_slugs` parameter)
- The GitHub Actions workflow checks if `_newsletters/{slug}/index.md` already exists and skips if so

**Deploy / Update / Teardown:**

```bash
# Initial deployment (interactive, prompts for Azure config)
./azure/deploy/deploy.sh

# Update Function App code or Logic App workflow after changes
./azure/deploy/update.sh                # update everything
./azure/deploy/update.sh --function-only # republish function code only

# Remove all Azure resources
./azure/deploy/teardown.sh
```

All scripts support `--help` for usage details. OAuth connections require one-time browser authorization during initial deploy.

**After teardown**, the OAuth tokens in Azure are destroyed, but authorized app entries may remain on the connected accounts. To fully revoke access:
- **GitHub**: Bot account > Settings > Applications > Authorized OAuth Apps — revoke "Microsoft Azure Logic Apps"
- **O365**: Admin portal for the mailbox account — revoke consent for "Microsoft Azure Logic Apps"

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
