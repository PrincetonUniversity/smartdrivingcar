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
├── inbox/                   # Drop .eml files here for processing
├── newsletter/
│   └── index.md             # Newsletter archive listing page
├── scripts/
│   ├── import_newsletter.py # Convert .eml to Jekyll markdown
│   ├── clean_newsletter.py  # HTML cleaning utilities
│   └── process_inbox.py     # Batch process inbox emails
├── tests/                   # Unit tests for scripts
├── .github/workflows/
│   ├── build.yml            # Build and deploy to GitHub Pages
│   └── process-newsletters.yml # Auto-process emails in inbox
├── index.md                 # Homepage
├── subscribe.md             # Newsletter subscription page
└── podcast/                 # Podcast content
```

## Run Locally

Requires Ruby (>= 3 recommended).

```bash
gem install bundler
bundle install
bundle exec jekyll serve
```
Then open: http://localhost:4000/

### Run with Docker

Build image (only needed when Gem dependencies change):

```bash
docker build -t smartdrivingcar-site .
```

Run container, mapping port 4000 and mounting source for live edits:

```bash
docker run --rm -it -p 4000:4000 -v "$(pwd)":/site smartdrivingcar-site
```

Visit: http://localhost:4000/

## Deployment (GitHub Pages)

This site uses GitHub Actions for deployment instead of the default GitHub Pages build.

1. Push repository to GitHub.
2. Go to **Settings → Pages**.
3. Under **Build and deployment**, set **Source** to **GitHub Actions**.
4. The `build.yml` workflow will automatically build and deploy on push to `main`.

The workflow auto-selects production config if a `CNAME` file exists; otherwise preview config is used.

## Newsletter Workflow

The site includes an automated system for processing email newsletters.

### Automated Processing

1. Drop `.eml` files into the `inbox/` directory.
2. Commit and push to `main`.
3. The `process-newsletters.yml` workflow will:
   - Extract HTML from emails
   - Convert to markdown
   - Create newsletter posts in `_newsletters/`
   - Remove processed files from inbox

### Manual Processing

```bash
python3 scripts/import_newsletter.py --date 2025-08-22 --title "Newsletter Title" --input path/to/email.eml
```

Or from clipboard (HTML):
```bash
pbpaste | python3 scripts/import_newsletter.py --date 2025-08-22 --title "Newsletter Title" --raw-html
```

### Configuration

Newsletter processing can be configured via environment variables or `config/newsletter_config.yml`. See `SHARED_TASK_NOTES.md` for details.

## Modes & Makefile

Three run/build modes:

| Mode | Purpose | Config Files | Base URL | Make Serve |
|------|---------|--------------|----------|------------|
| Local | Develop at `http://localhost:4000/` | `_config.yml,_config_local.yml` | (empty) | `make serve-local` |
| Preview | Simulate project site path | `_config.yml,_config_preview.yml` | `/smartdrivingcar` | `make serve-preview` |
| Production | Custom domain (smartdrivingcar.com) | `_config.yml,_config_prod.yml` | (empty) | `make serve-prod` |

Build only:
```bash
make build-preview
make build-prod
```

Docker (image: `smartdrivingcar-site`):
```bash
make docker-local
make docker-preview
make docker-prod
```
