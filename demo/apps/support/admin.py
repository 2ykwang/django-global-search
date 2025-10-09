from django.contrib import admin

from .models import FAQ, KnowledgeBaseArticle, Ticket, TicketCategory, TicketMessage


@admin.register(TicketCategory)
class TicketCategoryAdmin(admin.ModelAdmin):
    search_fields = ["name", "description"]
    list_display = ["name", "is_active", "created_at"]
    list_filter = ["is_active", "created_at"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    search_fields = [
        "ticket_number",
        "subject",
        "description",
        "user__username",
        "user__email",
        "assigned_to__username",
        "category__name",
    ]
    list_display = [
        "ticket_number",
        "subject",
        "user",
        "assigned_to",
        "category",
        "status",
        "priority",
        "created_at",
    ]
    list_filter = ["status", "priority", "category", "created_at"]
    raw_id_fields = ["user", "assigned_to", "category"]


@admin.register(TicketMessage)
class TicketMessageAdmin(admin.ModelAdmin):
    search_fields = [
        "ticket__ticket_number",
        "ticket__subject",
        "message_text",
        "user__username",
        "user__email",
    ]
    list_display = ["ticket", "user", "is_staff_reply", "is_internal_note", "created_at"]
    list_filter = ["is_staff_reply", "is_internal_note", "created_at"]
    raw_id_fields = ["ticket", "user"]


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    search_fields = [
        "question",
        "answer",
        "category__name",
    ]
    list_display = [
        "question",
        "category",
        "display_order",
        "view_count",
        "is_published",
        "created_at",
    ]
    list_filter = ["is_published", "category", "created_at"]
    raw_id_fields = ["category"]


@admin.register(KnowledgeBaseArticle)
class KnowledgeBaseArticleAdmin(admin.ModelAdmin):
    search_fields = [
        "title",
        "content",
        "summary",
        "author__username",
        "category__name",
    ]
    list_display = [
        "title",
        "author",
        "category",
        "status",
        "view_count",
        "helpful_count",
        "published_at",
    ]
    list_filter = ["status", "category", "published_at", "created_at"]
    prepopulated_fields = {"slug": ("title",)}
    raw_id_fields = ["category", "author"]
