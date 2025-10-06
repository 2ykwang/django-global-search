"""Global Search Views."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict, dataclass

from django.apps import apps
from django.contrib.admin.sites import AdminSite
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.contenttypes.models import ContentType
from django.http import HttpRequest
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View

from django_global_search.searcher import GlobalSearch, GlobalSearchResult, ModelSearchResult


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
        selected_ct_ids = self._get_selected_content_type_ids(request)
        admin_site = self.admin_site

        # Build context
        context = self.SearchContext(
            query=query,
            apps_data=self._get_apps_data(request, admin_site),
            selected_content_type_ids=selected_ct_ids,
            search_results=[],
            elapsed_time=None,
            error_message=None,
        )

        # Execute search if query is provided
        if query:
            try:
                searcher = GlobalSearch(admin_site)
                result = searcher.search(
                    request=request,
                    query=query,
                    content_type_ids=selected_ct_ids or None,
                )

                context.search_results = self._convert_search_results(result)
                context.elapsed_time = result.elapsed_time_ms / 1000.0

                if result.is_timeout:
                    context.error_message = "Search timeout exceeded. Please refine your query."

            except ValueError:
                context.error_message = "Invalid query"
            except Exception:
                context.error_message = "Search error"

        return render(request, self.template_name, asdict(context))

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

    def _get_selected_content_type_ids(self, request: HttpRequest):
        content_types_param = request.GET.get("content_type", "")
        if not content_types_param:
            return []

        try:
            return [int(cid) for cid in content_types_param.split(",") if cid]
        except ValueError:
            return []

    def _get_apps_data(self, request: HttpRequest, admin_site: AdminSite):
        """Get apps and models data for sidebar."""
        searcher = GlobalSearch(admin_site)
        searchable_admins = searcher.get_searchable_model_admins(request)

        # Build apps data from searchable models
        # {app_label: {"verbose_name": "", "models": []}}
        apps_data = defaultdict(lambda: {"verbose_name": "", "models": []})

        for model_admin in searchable_admins:
            model = model_admin.model
            app_label = model._meta.app_label
            app_config = apps.get_app_config(app_label)

            content_type = ContentType.objects.get_for_model(model)

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
