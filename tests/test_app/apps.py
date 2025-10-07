"""Test app config."""

from django.apps import AppConfig


class TestAppConfig(AppConfig):
    """Test app configuration."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "tests.test_app"
    verbose_name = "Test Application"
