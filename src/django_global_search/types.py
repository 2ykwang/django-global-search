"""data class type definitions."""

from __future__ import annotations

from dataclasses import dataclass


class SearchResult:
    """Search result."""

    @dataclass(frozen=True)
    class Item:
        """Individual search result item."""

        url: str
        display_text: str

    @dataclass(frozen=True)
    class Model:
        """Search results for a specific model."""

        content_type_id: int
        model_name: str
        verbose_name: str
        verbose_name_plural: str
        items: list[SearchResult.Item]
        has_more: bool
        changelist_url: str | None = None
        elapsed_time_ms: int = 0

    @dataclass(frozen=True)
    class App:
        """Search results for an app."""

        app_label: str
        app_verbose_name: str
        models: list[SearchResult.Model]

    @dataclass(frozen=True)
    class Global:
        """Global search result container."""

        apps: list[SearchResult.App]
        elapsed_time_ms: int
        is_timeout: bool = False
