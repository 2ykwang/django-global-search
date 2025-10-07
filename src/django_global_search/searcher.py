"""Global Search - Search logic."""

from __future__ import annotations

import logging
import time
from collections import defaultdict
from dataclasses import dataclass
from typing import TYPE_CHECKING
from urllib.parse import urlencode

from django.apps import apps
from django.contrib.admin.sites import AdminSite
from django.contrib.contenttypes.models import ContentType
from django.db.models import Model
from django.urls import reverse
from django.utils.translation import gettext as _

from django_global_search.admin import GlobalSearchAdminSiteMixin
from django_global_search.permissions import filter_searchable_models
from django_global_search.settings import GlobalSearchAdminSiteSettings

if TYPE_CHECKING:
    from django.contrib.admin import ModelAdmin
    from django.http import HttpRequest

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SearchResultItem:
    """Search result item."""

    url: str
    display_text: str


@dataclass(frozen=True)
class ModelSearchResult:
    """Search results for a specific model."""

    content_type_id: int
    model_name: str
    verbose_name: str
    verbose_name_plural: str
    items: list[SearchResultItem]
    has_more: bool
    changelist_url: str | None = None


@dataclass(frozen=True)
class AppSearchResult:
    """Search results for an app."""

    app_label: str
    app_verbose_name: str
    models: list[ModelSearchResult]


@dataclass(frozen=True)
class GlobalSearchResult:
    """Global search result container."""

    apps: list[AppSearchResult]
    elapsed_time_ms: int
    is_timeout: bool = False


class GlobalSearch:
    """Global Search class."""

    def __init__(self, admin_site: AdminSite):
        """Initialize global search.

        :param admin_site: AdminSite instance with GlobalSearchAdminSiteMixin
        :raises TypeError: If admin_site doesn't inherit GlobalSearchAdminSiteMixin
        """
        if not isinstance(admin_site, GlobalSearchAdminSiteMixin):
            raise TypeError(  # noqa: TRY003
                f"admin_site must inherit GlobalSearchAdminSiteMixin, got {type(admin_site)}"
            )

        self.admin_site = admin_site
        self.settings: GlobalSearchAdminSiteSettings = admin_site.get_global_search_settings()

    def search(
        self,
        request: HttpRequest,
        query: str,
        content_type_ids: list[int] | None = None,
    ) -> GlobalSearchResult:
        """Execute search.

        :param request: Request object
        :param query: Search query string
        :param content_type_ids: Optional list of content type IDs to filter
        :raises ValueError: If query is too short
        """
        # Validate and normalize query
        query = query.strip()
        min_query_length = self.settings.min_query_length
        if len(query) < min_query_length:
            raise ValueError(
                _("Query must be at least %(min_length)d characters")
                % {"min_length": min_query_length}
            )  # noqa: TRY003

        start_time = time.perf_counter()
        timeout_seconds = self.settings.search_timeout_ms / 1000.0

        # Get searchable model admins
        model_admins = self.get_searchable_model_admins(request, content_type_ids)

        # Group results by app_label
        search_results_by_app_label: dict[str, list[ModelSearchResult]] = defaultdict(list)

        for model_admin in model_admins:
            # Check timeout
            elapsed = time.perf_counter() - start_time
            if elapsed > timeout_seconds:
                # Return empty result on timeout for accuracy
                elapsed_ms = int(elapsed * 1000)
                return GlobalSearchResult(
                    apps=[],
                    elapsed_time_ms=elapsed_ms,
                    is_timeout=True,
                )

            model_query_start_time = time.perf_counter()
            model = model_admin.model
            content_type = ContentType.objects.get_for_model(model)
            model_search_result = self._search_model(request, model_admin, content_type, query)

            if model_search_result:
                app_label = model._meta.app_label
                search_results_by_app_label[app_label].append(model_search_result)

            logger.debug(
                "model_admin: %s - query elapsed: %s",
                model_admin,
                time.perf_counter() - model_query_start_time,
            )

        # Build app results
        app_results = []
        for app_label in sorted(search_results_by_app_label.keys()):
            models = search_results_by_app_label[app_label]
            app_config = apps.get_app_config(app_label)
            app_results.append(
                AppSearchResult(
                    app_label=app_label,
                    app_verbose_name=app_config.verbose_name,
                    models=models,
                )
            )

        elapsed_ms = int((time.perf_counter() - start_time) * 1000)

        return GlobalSearchResult(
            apps=app_results,
            elapsed_time_ms=elapsed_ms,
            is_timeout=False,
        )

    def get_searchable_model_admins(
        self, request: HttpRequest, content_type_ids: list[int] | None = None
    ) -> list[ModelAdmin]:
        """Get list of searchable ModelAdmin instances."""
        model_admins = list(self.admin_site._registry.values())

        return filter_searchable_models(
            request=request,
            model_admins=model_admins,
            excluded_models=self.settings.excluded_models,
            content_type_ids=content_type_ids,
        )

    def _search_model(
        self,
        request: HttpRequest,
        model_admin: ModelAdmin,
        ct: ContentType,
        query: str,
    ) -> ModelSearchResult | None:
        """Search in a specific model using ModelAdmin's search configuration."""
        model = model_admin.model

        # Get base queryset with permissions applied
        queryset = model_admin.get_queryset(request)

        # Use Django admin's built-in search
        queryset, use_distinct = model_admin.get_search_results(request, queryset, query)

        # Apply distinct if needed
        if use_distinct:
            queryset = queryset.distinct()

        # Apply ordering for consistent results
        ordering = model_admin.get_ordering(request)
        if ordering:
            queryset = queryset.order_by(*ordering)

        max_results = self.settings.max_results_per_model

        # Fetch only primary keys to check result count efficiently
        primary_keys = list(queryset.values_list("pk", flat=True)[: max_results + 1])

        if not primary_keys:
            return None

        has_more = len(primary_keys) > max_results
        if has_more:
            primary_keys = primary_keys[:max_results]

        # Create a mapping to preserve the original search result order
        pk_to_position = {pk: position for position, pk in enumerate(primary_keys)}

        # Fetch actual instances
        # - select_related(None): Clear any default select_related, avoid unnecessary JOINs
        # - order_by(): Clear ordering, sort in Python using pk_to_position
        optimized_queryset = (
            model._default_manager.using(queryset.db)
            .filter(pk__in=primary_keys)
            .select_related(None)
            .order_by()
        )

        # Sort instances to match the original search result order
        results = sorted(
            optimized_queryset,
            key=lambda instance: pk_to_position[instance.pk],
        )

        # Build result items with permission check
        result_items = []
        for obj in results:
            # Check object level view permission
            if not model_admin.has_view_permission(request, obj):
                continue

            url = self._get_object_url(obj)
            display_text = str(obj)
            result_items.append(SearchResultItem(url=url, display_text=display_text))

        if not result_items:
            return None

        # Get changelist URL
        changelist_url = self._get_changelist_url(model_admin, query)

        return ModelSearchResult(
            content_type_id=ct.id,
            model_name=model._meta.model_name,
            verbose_name=str(model._meta.verbose_name),
            verbose_name_plural=str(model._meta.verbose_name_plural),
            items=result_items,
            has_more=has_more,
            changelist_url=changelist_url,
        )

    def _get_object_url(self, obj: Model) -> str:
        """Get admin change URL for object."""
        admin_site_name = self.admin_site.name
        app_label = obj._meta.app_label
        model_name = obj._meta.model_name

        return reverse(
            f"admin:{app_label}_{model_name}_change",
            args=[obj.pk],
            current_app=admin_site_name,
        )

    def _get_changelist_url(self, model_admin: ModelAdmin, query: str) -> str | None:
        """Get admin changelist URL with search query."""
        model = model_admin.model

        admin_site_name = self.admin_site.name
        app_label = model._meta.app_label
        model_name = model._meta.model_name
        viewname = f"admin:{app_label}_{model_name}_changelist"

        try:
            base_url = reverse(viewname, current_app=admin_site_name)
        except Exception:
            return None
        else:
            query_string = urlencode({"q": query})
            return f"{base_url}?{query_string}"
