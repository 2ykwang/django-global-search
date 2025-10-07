# Justfile for django-global-search

# List all available commands
default:
    @just --list

build:
    rm -rf dist
    uv build

# Run ruff linter
lint:
    uv run ruff check .

# Run ruff formatter
format:
    uv run ruff check --fix-only .
    uv run ruff format .

# Install pre-commit hooks
pre-commit-install:
    uv run pre-commit install

# Serve documentation locally
docs-serve:
    uv run mkdocs serve

# Build documentation
docs-build:
    uv run mkdocs build

# Deploy documentation to GitHub Pages
docs-deploy:
    uv run mkdocs gh-deploy --force

# Export documentation dependencies to requirements.txt for Read the Docs
docs-requirements:
    #!/usr/bin/env bash
    echo "# Auto-generated from pyproject.toml via 'just docs-export'" > docs/requirements.txt
    echo "# Do not edit manually - edit pyproject.toml instead" >> docs/requirements.txt
    uv export --no-hashes >> docs/requirements.txt

# Generate translation message files
makemessages:
    cd src/ && django-admin makemessages --add-location=file -a --ignore=__pycache__ --ignore=migrations

# Compile translation message files
compilemessages:
    cd src/ && django-admin compilemessages

# Generate and compile translation messages
i18n: makemessages compilemessages

# Create translation files for a specific language
create-locale lang:
    cd src/ && django-admin makemessages --add-location=file -l {{ lang }} --ignore=__pycache__ --ignore=migrations
