from django.contrib import admin

from .models import Conversion, Event, PageView, SessionData


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    search_fields = [
        "event_name",
        "event_description",
        "user_agent",
        "referrer_url",
        "user__username",
        "user__email",
        "session_id",
        "device_type",
        "browser_name",
        "country",
        "city",
    ]
    list_display = [
        "event_name",
        "event_type",
        "user",
        "session_id",
        "device_type",
        "country",
        "created_at",
    ]
    list_filter = ["event_type", "device_type", "country", "created_at"]
    raw_id_fields = ["user"]


@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    search_fields = [
        "page_title",
        "page_url",
        "page_description",
        "page_path",
        "event__event_name",
        "event__user__username",
    ]
    list_display = [
        "page_title",
        "page_path",
        "event",
        "time_on_page",
        "scroll_depth",
        "created_at",
    ]
    list_filter = ["created_at"]
    raw_id_fields = ["event"]


@admin.register(Conversion)
class ConversionAdmin(admin.ModelAdmin):
    search_fields = [
        "conversion_description",
        "campaign_name",
        "campaign_source",
        "campaign_medium",
        "user__username",
        "user__email",
        "event__event_name",
    ]
    list_display = [
        "conversion_type",
        "campaign_name",
        "user",
        "conversion_value",
        "currency",
        "created_at",
    ]
    list_filter = ["conversion_type", "campaign_source", "campaign_medium", "created_at"]
    raw_id_fields = ["user", "event"]


@admin.register(SessionData)
class SessionDataAdmin(admin.ModelAdmin):
    search_fields = [
        "session_id",
        "device_info",
        "browser_info",
        "user__username",
        "user__email",
        "landing_page",
        "exit_page",
    ]
    list_display = [
        "session_id",
        "user",
        "total_page_views",
        "total_events",
        "session_duration",
        "is_bounce",
        "started_at",
    ]
    list_filter = ["is_bounce", "language", "started_at"]
    raw_id_fields = ["user"]
