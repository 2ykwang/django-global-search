from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class Article(models.Model):
    """Article model (50K rows)."""

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("published", "Published"),
        ("archived", "Archived"),
    ]

    title = models.CharField(max_length=300)
    slug = models.SlugField(max_length=300, unique=True)
    summary = models.CharField(max_length=500, blank=True)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="articles")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    view_count = models.IntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "articles"
        ordering = ["-published_at", "-created_at"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["author", "status"]),
            models.Index(fields=["status", "-published_at"]),
            models.Index(fields=["is_featured", "status"]),
        ]

    def __str__(self):
        return self.title


class BlogPost(models.Model):
    """Blog post model (50K rows)."""

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("published", "Published"),
        ("archived", "Archived"),
    ]

    title = models.CharField(max_length=300)
    slug = models.SlugField(max_length=300, unique=True)
    excerpt = models.CharField(max_length=500, blank=True)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="blog_posts")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    view_count = models.IntegerField(default=0)
    comment_count = models.IntegerField(default=0)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "blog_posts"
        ordering = ["-published_at", "-created_at"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["author", "status"]),
            models.Index(fields=["status", "-published_at"]),
        ]

    def __str__(self):
        return self.title


class Comment(models.Model):
    """Comment model with generic foreign key (300K rows)."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    author_name = models.CharField(max_length=200)  # Denormalized for search
    author_email = models.EmailField(blank=True)
    comment_text = models.TextField()
    is_approved = models.BooleanField(default=False)
    is_spam = models.BooleanField(default=False)

    # Generic relation to Article or BlogPost
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "comments"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "is_approved"]),
            models.Index(fields=["content_type", "object_id"]),
            models.Index(fields=["is_approved", "-created_at"]),
            models.Index(fields=["author_name"]),
        ]

    def __str__(self):
        return f"Comment by {self.author_name} on {self.content_object}"


class MediaFile(models.Model):
    """Media file model."""

    FILE_TYPES = [
        ("image", "Image"),
        ("video", "Video"),
        ("audio", "Audio"),
        ("document", "Document"),
    ]

    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    filename = models.CharField(max_length=300)
    file_url = models.URLField()
    file_type = models.CharField(max_length=20, choices=FILE_TYPES)
    file_size = models.BigIntegerField(default=0)  # in bytes
    mime_type = models.CharField(max_length=100, blank=True)
    uploaded_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="media_files"
    )
    articles = models.ManyToManyField(Article, related_name="media_files", blank=True)
    blog_posts = models.ManyToManyField(BlogPost, related_name="media_files", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "media_files"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["file_type", "-created_at"]),
            models.Index(fields=["uploaded_by", "-created_at"]),
            models.Index(fields=["filename"]),
        ]

    def __str__(self):
        return self.title
