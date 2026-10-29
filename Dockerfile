# Lightweight Jekyll build & serve for local development
# Uses official GitHub Pages gem to match Pages environment
FROM ruby:3.3.10-slim-bookworm@sha256:5e91410f3dd304de860361dbb7f1eb0347b9675dc4e21036c1d36a309da25b82

# Install build dependencies required by github-pages & native gems
RUN apt-get update && apt-get install -y --no-install-recommends build-essential libffi-dev git \
    && rm -rf /var/lib/apt/lists/*

# Install gems in a layer not shadowed by bind mounts
WORKDIR /app
COPY Gemfile Gemfile.lock ./
RUN gem install bundler -v 4.0.23 --no-document && bundle install

# Source code will be mounted at runtime into /site
WORKDIR /site

EXPOSE 4000
ENV JEKYLL_ENV=development

# Default command builds & serves mounted source
CMD ["bundle", "exec", "jekyll", "serve", "--config", "_config.yml,_config_local.yml", "--source", "/site", "--host", "0.0.0.0", "--port", "4000", "--livereload", "--force_polling"]
