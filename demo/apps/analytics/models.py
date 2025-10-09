from django.contrib.auth.models import User
from django.db import models


class Event(models.Model):
    """Event tracking model (1M rows - outlier with searchable text fields)."""

    EVENT_TYPE_CHOICES = [
        ("page_view", "Page View"),
        ("click", "Click"),
        ("form_submit", "Form Submit"),
        ("purchase", "Purchase"),
        ("signup", "Sign Up"),
        ("login", "Login"),
        ("logout", "Logout"),
        ("search", "Search"),
        ("download", "Download"),
        ("share", "Share"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="events",
    )
    session_id = models.CharField(max_length=100, db_index=True)
    event_type = models.CharField(max_length=50, choices=EVENT_TYPE_CHOICES)
    event_name = models.CharField(max_length=300)  # Searchable text
    event_description = models.TextField(blank=True)  # Searchable text
    user_agent = models.CharField(max_length=500, blank=True)  # Searchable text
    referrer_url = models.CharField(max_length=1000, blank=True)  # Searchable text
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    device_type = models.CharField(max_length=50, blank=True)  # mobile, desktop, tablet
    browser_name = models.CharField(max_length=100, blank=True)
    os_name = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "events"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["session_id", "-created_at"]),
            models.Index(fields=["event_type", "-created_at"]),
            models.Index(fields=["event_name"]),  # For search performance
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.event_type} - {self.event_name}"


class PageView(models.Model):
    """Page view tracking (subset of events)."""

    event = models.OneToOneField(Event, on_delete=models.CASCADE, related_name="page_view")
    page_url = models.CharField(max_length=1000)  # Searchable text
    page_title = models.CharField(max_length=300)  # Searchable text
    page_description = models.TextField(blank=True)  # Searchable text
    page_path = models.CharField(max_length=500)
    query_string = models.CharField(max_length=500, blank=True)
    time_on_page = models.IntegerField(default=0)  # in seconds
    scroll_depth = models.IntegerField(default=0)  # percentage
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "page_views"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["event", "-created_at"]),
            models.Index(fields=["page_path", "-created_at"]),
            models.Index(fields=["page_title"]),  # For search performance
        ]

    def __str__(self):
        return f"{self.page_title} - {self.page_url}"


class Conversion(models.Model):
    """Conversion tracking (500K rows)."""

    CONVERSION_TYPE_CHOICES = [
        ("signup", "Sign Up"),
        ("purchase", "Purchase"),
        ("subscribe", "Subscribe"),
        ("download", "Download"),
        ("contact", "Contact Form"),
        ("trial", "Start Trial"),
        ("upgrade", "Upgrade"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="conversions",
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="conversions",
    )
    conversion_type = models.CharField(max_length=50, choices=CONVERSION_TYPE_CHOICES)
    conversion_description = models.TextField(blank=True)  # Searchable text
    campaign_name = models.CharField(max_length=300, blank=True)  # Searchable text
    campaign_source = models.CharField(max_length=200, blank=True)  # e.g., google, facebook
    campaign_medium = models.CharField(max_length=200, blank=True)  # e.g., cpc, email
    conversion_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=10, default="USD")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "conversions"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["conversion_type", "-created_at"]),
            models.Index(fields=["campaign_name"]),  # For search performance
            models.Index(fields=["campaign_source", "campaign_medium"]),
        ]

    def __str__(self):
        return f"{self.conversion_type} - {self.campaign_name or 'Direct'}"


class SessionData(models.Model):
    """Session data tracking (1M rows)."""

    session_id = models.CharField(max_length=100, unique=True, db_index=True)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sessions",
    )
    device_info = models.CharField(max_length=500, blank=True)  # Searchable text
    browser_info = models.CharField(max_length=500, blank=True)  # Searchable text
    screen_resolution = models.CharField(max_length=50, blank=True)
    language = models.CharField(max_length=50, blank=True)
    timezone = models.CharField(max_length=100, blank=True)
    landing_page = models.CharField(max_length=1000, blank=True)
    exit_page = models.CharField(max_length=1000, blank=True)
    total_page_views = models.IntegerField(default=0)
    total_events = models.IntegerField(default=0)
    session_duration = models.IntegerField(default=0)  # in seconds
    is_bounce = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "session_data"
        ordering = ["-started_at"]
        indexes = [
            models.Index(fields=["session_id"]),
            models.Index(fields=["user", "-started_at"]),
            models.Index(fields=["is_bounce", "-started_at"]),
            models.Index(fields=["device_info"]),  # For search performance
        ]

    def __str__(self):
        return f"Session {self.session_id} - {self.user.username if self.user else 'Anonymous'}"
