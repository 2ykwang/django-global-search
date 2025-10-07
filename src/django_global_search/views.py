"""Global Search Views."""

from __future__ import annotations

import logging
from collections import defaultdict
from dataclasses import asdict, dataclass

from django.apps import apps
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.contenttypes.models import ContentType
from django.http import HttpRequest
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views import View

from django_global_search.searcher import GlobalSearch, GlobalSearchResult, ModelSearchResult

logger = logging.getLogger(__name__)


@method_decorator(staff_member_required, name="dispatch")
class GlobalSearchView(View):
    """Global Search View."""

    template_name = "global_search/search.html"
    admin_site = None

    @dataclass
    class SearchItemContext:
        """Search result item for template context."""

        url: str
        display_text: str

    @dataclass
    class ModelResultContext:
        """Model search result for template context."""

        content_type_id: int
        model_name: str
        verbose_name: str
        verbose_name_plural: str
        has_more: bool
        changelist_url: str | None
        items: list[GlobalSearchView.SearchItemContext]

    @dataclass
    class AppResultContext:
        """App search result for template context."""

        app_label: str
        app_verbose_name: str
        models: list[GlobalSearchView.ModelResultContext]

    @dataclass
    class SearchContext:
        """Template context for search view."""

        query: str
        apps_data: dict
        selected_content_type_ids: list[int]
        search_results: list[GlobalSearchView.AppResultContext]
        elapsed_time: float | None
        error_message: str | None

    def get(self, request, *args, **kwargs):
        """Handle GET request."""
        query = request.GET.get("q", "").strip()
        admin_site = self.admin_site
        searcher = GlobalSearch(admin_site)
        selected_ct_ids = self._get_selected_content_type_ids(request, searcher)

        # Build context
        context = self.SearchContext(
            query=query,
            apps_data=self._get_apps_data(request, searcher),
            selected_content_type_ids=selected_ct_ids,
            search_results=[],
            elapsed_time=None,
            error_message=None,
        )

        # Execute search if query is provided
        if query:
            try:
                result = searcher.search(
                    request=request,
                    query=query,
                    content_type_ids=selected_ct_ids or None,
                )

                context.search_results = self._convert_search_results(result)
                context.elapsed_time = result.elapsed_time_ms / 1000.0

                if result.is_timeout:
                    context.error_message = _("Search timeout exceeded. Please refine your query.")

            except ValueError:
                logger.exception("Invalid search query: %s", query)
                context.error_message = _("Invalid query")
            except Exception:
                logger.exception("Search error occurred for query: %s", query)
                context.error_message = _("Search error")

        # Merge with admin site context for proper URL resolution
        template_context = {
            **self.admin_site.each_context(request),
            **asdict(context),
        }
        return render(request, self.template_name, template_context)

    def _convert_search_results(self, result: GlobalSearchResult) -> list[AppResultContext]:
        return [
            self.AppResultContext(
                app_label=app_result.app_label,
                app_verbose_name=app_result.app_verbose_name,
                models=[
                    self._convert_model_result(model_result) for model_result in app_result.models
                ],
            )
            for app_result in result.apps
        ]

    def _convert_model_result(self, model_result: ModelSearchResult) -> ModelResultContext:
        return self.ModelResultContext(
            content_type_id=model_result.content_type_id,
            model_name=model_result.model_name,
            verbose_name=model_result.verbose_name,
            verbose_name_plural=model_result.verbose_name_plural,
            has_more=model_result.has_more,
            changelist_url=model_result.changelist_url,
            items=[
                self.SearchItemContext(url=item.url, display_text=item.display_text)
                for item in model_result.items
            ],
        )

    def _get_selected_content_type_ids(self, request: HttpRequest, searcher: GlobalSearch):
        content_type_ids = set()

        # Process 'apps' parameter (select all models in the app)
        apps_param = request.GET.get("apps", "")
        if apps_param:
            app_labels = [a.strip() for a in apps_param.split(",") if a.strip()]
            for app_label in app_labels:
                content_type_ids.update(
                    self._get_content_type_ids_for_app(request, app_label, searcher)
                )

        # Process 'content_type' parameter (individual model selection)
        content_types_param = request.GET.get("content_type", "")
        if content_types_param:
            try:
                ids = [int(cid) for cid in content_types_param.split(",") if cid]
                content_type_ids.update(ids)
            except ValueError:
                pass

        return list(content_type_ids) if content_type_ids else []

    def _get_content_type_ids_for_app(
        self, request: HttpRequest, app_label: str, searcher: GlobalSearch
    ) -> list[int]:
        """Get all searchable content type IDs for a given app."""
        searchable_admins = searcher.get_searchable_model_admins(request)

        # Filter models for the specific app
        app_models = [
            model_admin.model
            for model_admin in searchable_admins
            if model_admin.model._meta.app_label == app_label
        ]

        if not app_models:
            return []

        # Bulk fetch ContentTypes to avoid N+1 queries
        content_types = ContentType.objects.get_for_models(*app_models, for_concrete_models=False)
        return [ct.id for ct in content_types.values()]

    def _get_apps_data(self, request: HttpRequest, searcher: GlobalSearch):
        """Get apps and models data for sidebar."""
        searchable_admins = searcher.get_searchable_model_admins(request)

        if not searchable_admins:
            return {}

        models = [model_admin.model for model_admin in searchable_admins]
        content_types = ContentType.objects.get_for_models(*models, for_concrete_models=False)

        # Build apps data from searchable models
        # {app_label: {"verbose_name": "", "models": []}}
        apps_data = defaultdict(lambda: {"verbose_name": "", "models": []})

        for model_admin in searchable_admins:
            model = model_admin.model
            app_label = model._meta.app_label
            app_config = apps.get_app_config(app_label)

            content_type = content_types[model]

            if not apps_data[app_label]["verbose_name"]:
                apps_data[app_label]["verbose_name"] = app_config.verbose_name

            apps_data[app_label]["models"].append(
                {
                    "content_type_id": content_type.id,
                    "verbose_name_plural": model._meta.verbose_name_plural,
                    "model_name": model._meta.model_name,
                }
            )

        # Return in app_label alphabetical order
        return dict(sorted(apps_data.items()))
