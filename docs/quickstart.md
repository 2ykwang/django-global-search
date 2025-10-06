# Quick Start

## Project Status

!!! warning "Development"
    This project is in development and may introduce breaking changes in future releases.
    
## Basic Setup

### 1. Install the Package

```bash
uv add django-global-search
```

### 2. Add to INSTALLED_APPS

```python
# settings.py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django_global_search',  # Add this line
    # ... other apps
]
```

### 3. Access Global Search

Start your development server:

```bash
python manage.py runserver
```

Navigate to: `http://localhost:8000/admin/global-search/`

## Adding a Navigation Button (Optional)

Instead of typing the URL directly, you can add a search button to the Django Admin interface.

Create `templates/admin/base_site.html` in your project:

```html
{% extends "admin/base_site.html" %}

{% block userlinks %}
    {{ block.super }}
    {% include 'global_search/button.html' %}
{% endblock %}
```

This adds a "Global Search" button next to the user links in the admin header.

!!! tip "Template Location"
    Make sure your `templates/` directory is configured in `TEMPLATES` settings:
    ```python
    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [BASE_DIR / 'templates'],  # Add this
            'APP_DIRS': True,
            # ...
        },
    ]
    ```


## How It Works

### Automatic Model Detection

Django Global Search automatically includes all models that:

1. Are registered in Django Admin
2. Have `search_fields` defined in their ModelAdmin
3. The current user has view permission for

### Example ModelAdmin

```python
# admin.py
from django.contrib import admin
from .models import Article, Author

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    search_fields = ['title', 'content', 'author__name']
    list_display = ['title', 'author', 'published_date']

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    search_fields = ['name', 'email', 'bio']
    list_display = ['name', 'email']
```

With the above configuration, global search will automatically search across both `Article` and `Author` models using their respective `search_fields`.

## Using the Search Interface

### Search Across All Models

1. Visit `/admin/global-search/`
2. Enter your search query (minimum 2 characters by default)
3. Press Enter or click Search
4. Results are grouped by app and model

### Filter by Specific Models

Use the sidebar to select specific models to search:

1. Check/uncheck models you want to include
2. Results will only show from selected models
3. Selections persist during your session

### View Full Results

Click "View all results" link under any model to see the full changelist with your search query applied.

## Understanding Results

Results are organized hierarchically:

```
App Name
  └─ Model Name (5 results)
     ├─ Result 1
     ├─ Result 2
     └─ ...
```

## Permissions

Global search respects Django's permission system:

- Users only see models they have `view` permission for
- Object-level permissions are checked before displaying results
- Models without `has_module_permission` are excluded

## Next Steps

- [Configuration](configuration.md) - Customize search behavior, timeouts, and result limits
- Learn about [custom AdminSite integration](#) (coming soon)
