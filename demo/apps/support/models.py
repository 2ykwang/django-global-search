from django.contrib.auth.models import User
from django.db import models


class TicketCategory(models.Model):
    """Ticket category."""

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ticket_categories"
        ordering = ["name"]
        verbose_name_plural = "Ticket Categories"

    def __str__(self):
        return self.name


class Ticket(models.Model):
    """Support ticket model (50K rows)."""

    STATUS_CHOICES = [
        ("open", "Open"),
        ("in_progress", "In Progress"),
        ("waiting_customer", "Waiting on Customer"),
        ("resolved", "Resolved"),
        ("closed", "Closed"),
    ]

    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("urgent", "Urgent"),
    ]

    ticket_number = models.CharField(max_length=50, unique=True, db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tickets")
    category = models.ForeignKey(
        TicketCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tickets",
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tickets",
    )
    subject = models.CharField(max_length=300)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="open")
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default="medium")
    resolved_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tickets"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["ticket_number"]),
            models.Index(fields=["user", "status"]),
            models.Index(fields=["status", "priority", "-created_at"]),
            models.Index(fields=["assigned_to", "status"]),
            models.Index(fields=["category", "status"]),
        ]

    def __str__(self):
        return f"Ticket {self.ticket_number} - {self.subject}"


class TicketMessage(models.Model):
    """Messages within a ticket (200K rows)."""

    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="messages")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ticket_messages")
    message_text = models.TextField()
    is_staff_reply = models.BooleanField(default=False)
    is_internal_note = models.BooleanField(default=False)  # Only visible to staff
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ticket_messages"
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["ticket", "created_at"]),
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["is_staff_reply", "-created_at"]),
        ]

    def __str__(self):
        return f"Message on {self.ticket.ticket_number} by {self.user.username}"


class FAQ(models.Model):
    """Frequently asked questions."""

    category = models.ForeignKey(
        TicketCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="faqs",
    )
    question = models.CharField(max_length=500)
    answer = models.TextField()
    display_order = models.IntegerField(default=0)
    view_count = models.IntegerField(default=0)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "faqs"
        ordering = ["display_order", "-view_count"]
        indexes = [
            models.Index(fields=["category", "is_published"]),
            models.Index(fields=["is_published", "-view_count"]),
        ]
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"

    def __str__(self):
        return self.question[:100]


class KnowledgeBaseArticle(models.Model):
    """Knowledge base articles for self-service support."""

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("published", "Published"),
        ("archived", "Archived"),
    ]

    category = models.ForeignKey(
        TicketCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="kb_articles",
    )
    title = models.CharField(max_length=300)
    slug = models.SlugField(max_length=300, unique=True)
    content = models.TextField()
    summary = models.CharField(max_length=500, blank=True)
    author = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="kb_articles"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    view_count = models.IntegerField(default=0)
    helpful_count = models.IntegerField(default=0)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "knowledge_base_articles"
        ordering = ["-published_at", "-created_at"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["category", "status"]),
            models.Index(fields=["status", "-view_count"]),
            models.Index(fields=["author", "status"]),
        ]

    def __str__(self):
        return self.title
