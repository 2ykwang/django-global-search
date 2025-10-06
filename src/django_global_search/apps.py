"""Django Global Search AppConfig."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

from django_global_search.admin import inject_default_admin_site


class DjangoGlobalSearchConfig(AppConfig):  # noqa: D101
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_global_search"
    verbose_name = _("Django Global Search")

    def ready(self):  # noqa: D102
        from django_global_search.settings import global_search_settings

        if not global_search_settings.inject_default_admin_site_enabled:
            return

        inject_default_admin_site()
