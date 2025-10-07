"""Test app admin."""

from django.contrib import admin

from .models import Author, Book, Category, Publisher


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    """Author admin with search_fields."""

    list_display = ["name", "email"]
    search_fields = ["name", "email", "bio"]


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """Book admin with search_fields."""

    list_display = ["title", "author", "isbn", "is_active"]
    search_fields = ["title", "isbn", "description", "author__name"]
    list_filter = ["is_active"]

    def get_queryset(self, request):
        """Override to add select_related."""
        return super().get_queryset(request).select_related("author")


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    """Publisher admin with search_fields."""

    list_display = ["name", "country"]
    search_fields = ["name", "country", "website"]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Category admin WITHOUT search_fields (should be excluded from search)."""

    list_display = ["name", "description"]
