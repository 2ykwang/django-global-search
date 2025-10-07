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

