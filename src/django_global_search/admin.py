"""Global Search Admin."""

from django.contrib import admin
from django.urls import path

from django_global_search.settings import GlobalSearchAdminSiteSettings


class GlobalSearchAdminSiteMixin:
    """Global Search Admin Site Mixin."""

    def get_global_search_settings(self):
        """Get Global Search Settings."""
        return GlobalSearchAdminSiteSettings.from_admin_site(self)

    def get_urls(self):
        """Get admin URLs with global search."""
        from django_global_search.views import GlobalSearchView

        urls = super().get_urls()

        custom_urls = [
            path(
                "global-search/",
                self.admin_view(GlobalSearchView.as_view(admin_site=self)),
                name="global_search",
            ),
        ]
        return custom_urls + urls


def inject_default_admin_site():
    """Inject GlobalSearchAdminSiteMixin into default AdminSite."""
    # Check if AdminSite already has the mixin
    if issubclass(admin.site.__class__, GlobalSearchAdminSiteMixin):
        return

    # Create a new class based on the current class
    current_class = admin.site.__class__
    new_class = type(
        f"{current_class.__name__}WithGlobalSearch",
        (GlobalSearchAdminSiteMixin, current_class),
        {},
    )

    # Replace admin.site.__class__ with the new class
    admin.site.__class__ = new_class
