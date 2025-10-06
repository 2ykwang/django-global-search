"""django-global-search settings."""

from dataclasses import dataclass

from django.conf import settings
from django.contrib.admin.sites import AdminSite


@dataclass(frozen=True)
class GlobalSearchAdminSiteSettings:
    """Global Search admin site settings."""

    min_query_length: int
    """Minimum query length."""
    max_results_per_model: int
    """Maximum results per model."""
    search_timeout_ms: int
    """Search timeout in milliseconds."""
    excluded_models: list[str]
    """Excluded models.

    example: ['auth.user', 'auth.group']
    """

    @classmethod
    def from_admin_site(cls, admin_site: AdminSite):
        """Create GlobalSearchAdminSiteSettings from AdminSite."""
        min_query_length = getattr(settings, "GLOBAL_SEARCH_MIN_QUERY_LENGTH", 2)
        max_results_per_model = getattr(settings, "GLOBAL_SEARCH_MAX_RESULTS_PER_MODEL", 10)
        search_timeout_ms = getattr(settings, "GLOBAL_SEARCH_TIMEOUT_MS", 20000)
        excluded_models = getattr(settings, "GLOBAL_SEARCH_EXCLUDED_MODELS", [])

        defaults = {
            "min_query_length": min_query_length,
            "max_results_per_model": max_results_per_model,
            "search_timeout_ms": search_timeout_ms,
            "excluded_models": excluded_models,
        }

        if hasattr(admin_site, "global_search_settings"):
            defaults.update(admin_site.global_search_settings)

        return cls(**defaults)


@dataclass(frozen=True)
class GlobalSearchSettings:
    """Global Search settings."""

    inject_default_admin_site_enabled: bool
    """Inject default admin site."""

    @classmethod
    def from_settings(cls):
        """Create GlobalSearchSettings from settings."""
        inject_default_admin_site_enabled = getattr(
            settings, "GLOBAL_SEARCH_INJECT_DEFAULT_ADMIN_SITE_ENABLED", True
        )

        return cls(inject_default_admin_site_enabled=inject_default_admin_site_enabled)


global_search_settings = GlobalSearchSettings.from_settings()
