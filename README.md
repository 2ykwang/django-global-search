# Django Global Search

[![PyPI Download](https://img.shields.io/pypi/v/django-global-search.svg)](https://pypi.python.org/pypi/django-global-search)
[![Test](https://github.com/2ykwang/django-global-search/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/2ykwang/django-global-search/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/2ykwang/django-global-search/branch/main/graph/badge.svg?token=0YSa3UCGaU)](https://codecov.io/gh/2ykwang/django-global-search)
[![PyPI Python Versions](https://img.shields.io/pypi/pyversions/django-global-search.svg)](https://pypi.python.org/pypi/django-global-search)
[![Supported Django versions](https://img.shields.io/pypi/djversions/django-global-search.svg)](https://pypi.python.org/pypi/django-global-search)


A global search extension for Django Admin that allows searching across multiple models from a single page. Search through all registered models with permission handling and respect for existing `search_fields` configurations.

Documentation can be found at https://django-global-search.readthedocs.io/
 
## Installation

Install using pip:

```bash
pip install django-global-search
```

Or using uv:

```bash
uv add django-global-search
```

## Usage

### Setup
 
```python
# settings.py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django_global_search',  # Add after admin
    # ... other apps
]
```
 
### Adding a Navigation Button (Optional)

```html
{% extends "admin/base_site.html" %}

{% block userlinks %}
    {{ block.super }}
    {% include 'global_search/button.html' %}
{% endblock %}
```

This adds a convenient "Global Search" button in the admin header.

### Advanced Setup

If you're using a custom admin site class, you can explicitly inherit from the mixin:

```python
# admin.py
from django.contrib.admin import AdminSite
from django_global_search.admin import GlobalSearchAdminSiteMixin

class MyAdminSite(GlobalSearchAdminSiteMixin, AdminSite):
    site_header = "My Custom Admin"

# Replace the default admin site
admin_site = MyAdminSite(name='myadmin')
```

## Screenshots

### Global Search Interface
![Global Search Interface](./docs/media/admin_search_page.png)

*Search across all models with permission-based filtering and model selection*

### Search Results
![Search Results](./docs/media/admin_search_result_page.png)

*Results grouped by app and model with direct links to detail and changelist views*

## Requirements

- Python 3.9+
- Django 4.2+

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- Email: me@youngkwang.dev
- Issues: [GitHub Issues](https://github.com/2ykwang/django-global-search/issues)
- Documentation: [Read the Docs](https://django-global-search.readthedocs.io/)

