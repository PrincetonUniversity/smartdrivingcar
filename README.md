# SmartDrivingCar (Jekyll)

Static refactor of the former WordPress (Divi) landing page for hosting on GitHub Pages.

## What Was Migrated
- Global header & navigation recreated in `_includes/header.html`.
- Footer copyright moved to `_includes/footer.html`.
- Hero slider content (4 original slides) reproduced with a lightweight CSS/JS slider in `index.html`.
- Embedded media (Spotify + YouTube playlist) preserved.
- Key images reused from the original `wp-content/uploads` directory (left in place for now).
- Basic brand typography (Open Sans Google Font) and simplified styling (`assets/css/site.css`).

## Project Structure
```
_config.yml        # Jekyll site configuration
Gemfile            # GitHub Pages gem
_layouts/default.html
_includes/header.html
_includes/footer.html
assets/css/site.css
index.html         # New Jekyll front page with front matter
wp-content/        # Legacy WP assets (images, etc.) kept for now
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

## To Do / Next Steps
- Migrate additional WordPress pages/posts (create markdown files with front matter under root or collections).
- Replace direct external links (newsletter/podcast/papers) with internal pages if those will also migrate.
- Optimize images (WebP, resizing) and move only used assets to an `assets/img` folder.
- Add a proper sitemap (`jekyll-sitemap` plugin) and analytics if needed.
- Consider accessibility & performance pass (contrast, alt text completeness, defer non-critical JS).
- Move inline slider script into a separate JS file under `assets/js/` if more scripting is added.

## Slider Notes
Simple interval-based rotation (7s). No controls yet; add pause/prev/next if user interaction required.

## License / Attribution
Original content & media remain © SmartDrivingCar.com. The refactor code (layout & CSS simplification) can be MIT licensed if desired—add a LICENSE file to formalize.

## Removed Legacy Directories
The previous `wp-content` (and nested uploads) hierarchy has been flattened. After confirming no references remain, the `wp-content` directory may be deleted (it is safe now given images live under `assets/img/`).

---
Feel free to request expansion (blog import, pagination, feeds, categories) and I can scaffold it.
