# Justfile for django-global-search

# List all available commands
default:
    @just --list

# Run ruff linter
lint:
    uv run ruff check .

# Run ruff formatter
format:
    uv run ruff check --fix .
    uv run ruff format .

