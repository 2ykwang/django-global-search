# Installation

## Requirements

**Supported Python version**

[![PyPI Python Versions](https://img.shields.io/pypi/pyversions/django-global-search.svg)](https://pypi.python.org/pypi/django-global-search)

**Supported Django version**

[![Supported Django versions](https://img.shields.io/pypi/djversions/django-global-search.svg)](https://pypi.python.org/pypi/django-global-search)

## Install with uv (Recommended)

[uv](https://github.com/astral-sh/uv) is a fast Python package installer:

```bash
uv add django-global-search
```

## Install with pip

```bash
pip install django-global-search
```

## Install from Source

For development or testing the latest changes:

```bash
# Clone the repository
git clone https://github.com/youngkwang-yang/django-global-search.git
cd django-global-search

# Install in development mode
uv pip install -e .
```

## Add to Django Project

Add `django_global_search` to your `INSTALLED_APPS` in `settings.py`:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django_global_search',  # Add after django.contrib.admin

    # ... your other apps
]
```

!!! tip "Installation Order"
    Place `django_global_search` after `django.contrib.admin` to ensure proper integration.

## Verify Installation

Run the development server and navigate to `/admin/global-search/`:

```bash
python manage.py runserver
```

You should see the global search interface in your Django admin.

## Next Steps

- [Quick Start Guide](quickstart.md) - Start using global search
- [Configuration](configuration.md) - Customize search behavior
