# Lightweight Jekyll build & serve for local development
# Uses official GitHub Pages gem to match Pages environment
FROM ruby:3.3-alpine

# Install build dependencies required by github-pages & native gems
RUN apk add --no-cache build-base libffi-dev git

# Install gems in a layer not shadowed by bind mounts
WORKDIR /app
COPY Gemfile Gemfile.lock* ./
RUN bundle install

# Source code will be mounted at runtime into /site
WORKDIR /site

EXPOSE 4000
ENV JEKYLL_ENV=development

# Default command builds & serves mounted source
CMD bundle exec jekyll serve --config _config.yml,_config_local.yml --source /site --host 0.0.0.0 --port 4000 --livereload --force_polling
