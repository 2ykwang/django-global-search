# Configuration

Customize Django Global Search behavior through Django settings or per-AdminSite configuration.

## Django Settings

Add these settings to your `settings.py` file:

### GLOBAL_SEARCH_MIN_QUERY_LENGTH

Minimum number of characters required for a search query.

**Default:** `2`

```python
GLOBAL_SEARCH_MIN_QUERY_LENGTH = 3
```

### GLOBAL_SEARCH_MAX_RESULTS_PER_MODEL

Maximum number of results to display per model.

**Default:** `10`

```python
GLOBAL_SEARCH_MAX_RESULTS_PER_MODEL = 20
```


### GLOBAL_SEARCH_TIMEOUT_MS

Search timeout in milliseconds. Prevents slow queries from blocking the interface.

**Default:** `20000` (20 seconds)

```python
GLOBAL_SEARCH_TIMEOUT_MS = 30000  # 30 seconds
```

When timeout is reached, an empty result set is returned with a timeout warning.

### GLOBAL_SEARCH_EXCLUDED_MODELS

List of models to exclude from global search, in `'app_label.model_name'` format.

**Default:** `[]`

```python
GLOBAL_SEARCH_EXCLUDED_MODELS = [
    'admin.logentry',
    'auth.permission',
    'contenttypes.contenttype',
    'sessions.session',
]
```

### GLOBAL_SEARCH_INJECT_DEFAULT_ADMIN_SITE_ENABLED

Enable automatic injection into Django's default admin site.

**Default:** `True`

```python
GLOBAL_SEARCH_INJECT_DEFAULT_ADMIN_SITE_ENABLED = False
```

Set to `False` if you're using a custom AdminSite and want to manually integrate the mixin.

## Per-AdminSite Configuration

For custom admin sites, you can override settings at the AdminSite level:

```python
# admin.py
from django.contrib import admin
from django_global_search.admin import GlobalSearchAdminSiteMixin

class MyAdminSite(GlobalSearchAdminSiteMixin, admin.AdminSite):
    site_header = "My Admin"

    global_search_settings = {
        'min_query_length': 3,
        'max_results_per_model': 15,
        'search_timeout_ms': 25000,
        'excluded_models': ['myapp.sensitivemodel'],
    }

admin_site = MyAdminSite(name='myadmin')
```

!!! note
    Per-AdminSite settings override Django settings for that specific admin site.

## Model Admin Configuration

Global search uses your existing `ModelAdmin` configuration:

### search_fields

Defines which fields are searchable. Uses Django's standard `search_fields` syntax:

```python
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    search_fields = [
        'title',           # Exact field
        'content',         # Text field
        'author__name',    # Related field
        '=status',         # Exact match
        '^slug',           # Starts-with
    ]
```

### get_search_results

Custom search logic is automatically respected:

```python
class ArticleAdmin(admin.ModelAdmin):
    search_fields = ['title', 'content']

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(
            request, queryset, search_term
        )
        # Add custom filtering
        if search_term.startswith('#'):
            queryset = queryset.filter(tags__name=search_term[1:])
        return queryset, use_distinct
```

### Permissions

Global search respects these permission methods:

```python
class ArticleAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        # Control whether model appears in search
        return request.user.is_staff

    def has_view_permission(self, request, obj=None):
        # Control model-level and object-level access
        if obj is None:
            return request.user.has_perm('myapp.view_article')
        return obj.is_public or request.user == obj.author
```
