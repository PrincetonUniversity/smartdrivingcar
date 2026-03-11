.PHONY: help serve-local serve-preview serve-prod build-preview build-prod clean docker-local docker-preview docker-prod backfill backfill-dry-run ai-cleanup ai-cleanup-dry-run sanitize sanitize-dry-run

JEKYLL?=bundle exec jekyll
PYTHON?=.venv/bin/python
PORT?=4040
HOST?=0.0.0.0

# Default help
help:
	@echo "Available targets:"
	@echo "  serve-local     - Serve with local overrides (_config.yml,_config_local.yml) baseurl=''"
	@echo "  serve-preview   - Serve project preview (_config.yml,_config_preview.yml) baseurl='/smartdrivingcar'"
	@echo "  serve-prod      - Serve production (just _config.yml or plus _config_prod.yml)"
	@echo "  build-preview   - Build into _site (preview overrides)"
	@echo "  build-prod      - Build into _site (production)"
	@echo "  docker-local    - Run container (local mode)"
	@echo "  docker-preview  - Run container forcing preview mode inside container"
	@echo "  docker-prod     - Run container forcing prod mode inside container"

serve-local:
	$(JEKYLL) serve --config _config.yml,_config_local.yml --host $(HOST) --port $(PORT) --livereload --force_polling

serve-preview:
	$(JEKYLL) serve --config _config.yml,_config_preview.yml --host $(HOST) --port $(PORT) --livereload --force_polling

serve-prod:
	$(JEKYLL) serve --config _config.yml,_config_prod.yml --host $(HOST) --port $(PORT) --livereload --force_polling

build-preview:
	$(JEKYLL) build --config _config.yml,_config_preview.yml

build-prod:
	$(JEKYLL) build --config _config.yml,_config_prod.yml

clean:
	rm -rf _site .jekyll-cache

# Docker helpers assume image already built as smartdrivingcar-site
# Override PORT if needed: make docker-local PORT=4100

docker-local:
	docker run --rm -it -p $(PORT):4000 -v "$(PWD)":/site smartdrivingcar-site bundle exec jekyll serve --config _config.yml,_config_local.yml --host 0.0.0.0 --port 4000 --livereload --force_polling

docker-preview:
	docker run --rm -it -p $(PORT):4000 -v "$(PWD)":/site smartdrivingcar-site bundle exec jekyll serve --config _config.yml,_config_preview.yml --host 0.0.0.0 --port 4000 --livereload --force_polling

docker-prod:
	docker run --rm -it -p $(PORT):4000 -v "$(PWD)":/site smartdrivingcar-site bundle exec jekyll serve --config _config.yml,_config_prod.yml --host 0.0.0.0 --port 4000 --livereload --force_polling

# Backfill old newsletters from Listserv GETPOST wrapper emails
backfill:
	$(PYTHON) scripts/backfill_newsletters.py --dir backfill/

backfill-dry-run:
	$(PYTHON) scripts/backfill_newsletters.py --dir backfill/ --dry-run

# AI post-processing (requires AI_SANDBOX_KEY env var and portkey-ai)
ai-cleanup:
	$(PYTHON) scripts/ai_post_process.py _newsletters/*/index.md

ai-cleanup-dry-run:
	$(PYTHON) scripts/ai_post_process.py _newsletters/*/index.md --dry-run

# Second-pass sanitize (deterministic fixes only, no API key needed)
sanitize:
	$(PYTHON) scripts/ai_post_process.py --sanitize-only _newsletters/*/index.md

sanitize-dry-run:
	$(PYTHON) scripts/ai_post_process.py --sanitize-only --dry-run _newsletters/*/index.md
