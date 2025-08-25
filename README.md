# SmartDrivingCar Site

Static refactor of the former WordPress (Divi theme) landing page for Prof. Alain Kornhauser's [smartdrivingcar.com](https://smartdrivingcar.com).

## Migration
- Global header & navigation recreated in `_includes/header.html`.
- Footer copyright moved to `_includes/footer.html`.
- Hero slider (4 original slides) reproduced with a lightweight CSS/JS slider in `index.html`.
- Images reused from the original `wp-content/uploads` directory. 
- Basic brand typography (Open Sans Google Font) and simplified styling (`assets/css/site.css`).

## Structure
```
_config.yml        # Jekyll site configuration
Gemfile            # GitHub Pages gem
_layouts/default.html
_includes/header.html
_includes/footer.html
assets/css/site.css # Styling
index.html         # New Jekyll front page with front matter
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

For faster incremental rebuilds you can append `--incremental` to the serve command in the Dockerfile or override the command:

```bash
docker run --rm -it -p 4000:4000 -v "$(pwd)":/site smartdrivingcar-site \
	bundle exec jekyll serve --source /site --host 0.0.0.0 --port 4000 --livereload --force_polling --incremental

Gem layer note: Gems are installed in the image (/app) so mounting the project at /site does not hide installed executables.
```

## Deployment (GitHub Pages)

1. Push repository to GitHub (e.g. `smartdrivingcar/smartdrivingcar.github.io` or any repo with Pages enabled).
2. If using a project (not user) site, set `url` and `baseurl` in `_config.yml` accordingly.
3. Enable GitHub Pages with the `GitHub Pages` build (default) using the branch (usually `main`).

## Newsletter Workflow

Site now supports a `newsletters` collection for the weekly SmartDrivingCars email.

### Add a New Newsletter Issue 
1. Save the email as `.eml` (or copy raw HTML to clipboard).
2. Run the import script:
	```bash
	python3 scripts/import_newsletter.py --date 2025-08-22 --title "Automated Vehicles Update" --input path/to/email.eml
	# or from clipboard (HTML)
	pbpaste | python3 scripts/import_newsletter.py --date 2025-08-22 --title "Automated Vehicles Update" --raw-html
	```
3. Open the generated file in `_newsletters/` to spot‑fix formatting.
4. Commit & push. The archive at `/newsletter/` updates automatically.

### File Naming & URLs
`_newsletters/YYYY-MM-DD-slug.md` -> `/newsletter/YYYY/MM/DD/slug/` (configurable in `_config.yml`).

## Modes & Makefile

Three run/build modes:

| Mode | Purpose | Config Files | Base URL | Make Serve |
|------|---------|--------------|----------|------------|
| Local | Develop at `http://localhost:4000/` | `_config.yml,_config_local.yml` | (empty) | `make serve-local` |
| Preview | Simulate project site path on org pages | `_config.yml` | `/smartdrivingcar` | `make serve-preview` |
| Production | Custom domain build (smartdrivingcar.com) | `_config.yml,_config_prod.yml` | (empty) | `make serve-prod` |

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

The GitHub Action auto-selects production if a `CNAME` file exists; otherwise preview config is used. Use preview mode locally only when you need to replicate the repository path routing.
