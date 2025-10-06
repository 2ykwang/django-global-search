"""Permission utilities for global search."""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.contenttypes.models import ContentType

if TYPE_CHECKING:
    from django.contrib.admin import ModelAdmin
    from django.db.models import Model
    from django.http import HttpRequest


def has_search_permission(
    request: HttpRequest,
    model_admin: ModelAdmin,
    model: Model,
    excluded_models: set[str],
) -> bool:
    """Check if user has permission to search this model.

    :param request: HTTP request object
    :param model_admin: ModelAdmin instance
    :param model: Django model class
    :param excluded_models: Set of excluded model labels (format: "app_label.model_name")
    :return: True if user can search this model, False otherwise
    """
    # Check if model has search_fields configured
    if not getattr(model_admin, "search_fields", None):
        return False

    # Check module permission (app-level access)
    if not model_admin.has_module_permission(request):
        return False

    # Check view permission (model-level access)
    if not model_admin.has_view_permission(request):
        return False

    # Check if model is in excluded list
    model_label = f"{model._meta.app_label}.{model._meta.model_name}"
    return model_label not in excluded_models


def filter_searchable_models(
    request: HttpRequest,
    admin_registry: dict,
    excluded_models: set[str],
    content_type_ids: list[int] | None = None,
) -> list[ModelAdmin]:
    """Filter admin registry to get searchable ModelAdmin instances.

    :param request: HTTP request object
    :param admin_registry: AdminSite._registry dictionary
    :param excluded_models: Set of excluded model labels
    :param content_type_ids: Optional list of content type IDs to filter
    :return: List of searchable ModelAdmin instances
    """
    searchable_admins = []
    selected_content_type_ids = set(content_type_ids) if content_type_ids else None

    for model, model_admin in admin_registry.items():
        # Check basic search permission
        if not has_search_permission(request, model_admin, model, excluded_models):
            continue

        # Filter by content_type_ids if provided
        if selected_content_type_ids:
            content_type = ContentType.objects.get_for_model(model)
            if content_type.id not in selected_content_type_ids:
                continue

        searchable_admins.append(model_admin)

    return searchable_admins
