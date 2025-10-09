from django.contrib import admin

from .models import Article, BlogPost, Comment, MediaFile


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    search_fields = [
        "title",
        "summary",
        "content",
        "author__username",
        "author__email",
    ]
    list_display = [
        "title",
        "author",
        "status",
        "is_featured",
        "view_count",
        "published_at",
        "created_at",
    ]
    list_filter = ["status", "is_featured", "published_at", "created_at"]
    prepopulated_fields = {"slug": ("title",)}
    raw_id_fields = ["author"]


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    search_fields = [
        "title",
        "excerpt",
        "content",
        "author__username",
        "author__email",
    ]
    list_display = [
        "title",
        "author",
        "status",
        "view_count",
        "comment_count",
        "published_at",
        "created_at",
    ]
    list_filter = ["status", "published_at", "created_at"]
    prepopulated_fields = {"slug": ("title",)}
    raw_id_fields = ["author"]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    search_fields = [
        "comment_text",
        "author_name",
        "author_email",
        "user__username",
        "user__email",
    ]
    list_display = ["author_name", "user", "content_object", "is_approved", "is_spam", "created_at"]
    list_filter = ["is_approved", "is_spam", "content_type", "created_at"]
    raw_id_fields = ["user"]


@admin.register(MediaFile)
class MediaFileAdmin(admin.ModelAdmin):
    search_fields = [
        "title",
        "description",
        "filename",
        "uploaded_by__username",
    ]
    list_display = ["title", "filename", "file_type", "file_size", "uploaded_by", "created_at"]
    list_filter = ["file_type", "created_at"]
    raw_id_fields = ["uploaded_by"]
    filter_horizontal = ["articles", "blog_posts"]
