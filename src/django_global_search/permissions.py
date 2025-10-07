"""Permission utilities for global search."""

from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING

from django.contrib.contenttypes.models import ContentType

if TYPE_CHECKING:
    from django.contrib.admin import ModelAdmin
    from django.http import HttpRequest


def has_search_permission(
    request: HttpRequest,
    model_admin: ModelAdmin,
    excluded_models: Iterable[str],
) -> bool:
    """Check if user has permission to search this model.

    :param request: HTTP request object
    :param model_admin: ModelAdmin instance
    :param excluded_models: Iterable of excluded model labels (format: "app_label.model_name")
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

    excluded_models_set = (
        set(excluded_models) if not isinstance(excluded_models, set) else excluded_models
    )

    model = model_admin.model
    # Check if model is in excluded list
    model_label = f"{model._meta.app_label}.{model._meta.model_name}"
    return model_label not in excluded_models_set


def filter_searchable_models(
    request: HttpRequest,
    model_admins: list[ModelAdmin],
    excluded_models: Iterable[str],
    content_type_ids: list[int] | None = None,
) -> list[ModelAdmin]:
    """Filter ModelAdmin instances to get searchable ones.

    :param request: HTTP request object
    :param model_admins: List of ModelAdmin instances to filter
    :param excluded_models: Iterable of excluded model labels
    :param content_type_ids: Optional list of content type IDs to filter
    :return: List of searchable ModelAdmin instances
    """
    # collect all admins that pass permission check
    permission_checked_admins = []
    for model_admin in model_admins:
        if has_search_permission(request, model_admin, excluded_models):
            permission_checked_admins.append(model_admin)

    # filter by content_type_ids if provided
    if content_type_ids:
        selected_content_type_ids = set(content_type_ids)
        models = [model_admin.model for model_admin in permission_checked_admins]

        content_types = ContentType.objects.get_for_models(*models, for_concrete_models=False)

        searchable_admins = []
        for model_admin in permission_checked_admins:
            content_type = content_types[model_admin.model]
            if content_type.id in selected_content_type_ids:
                searchable_admins.append(model_admin)

        return searchable_admins

    return permission_checked_admins
