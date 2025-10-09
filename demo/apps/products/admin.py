from django.contrib import admin

from .models import Category, Product, ProductImage, ProductVariant, Tag


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = [
        "name",
        "description",
        "parent__name",
    ]
    list_display = ["name", "parent", "is_active", "created_at"]
    list_filter = ["is_active", "created_at"]
    prepopulated_fields = {"slug": ("name",)}
    raw_id_fields = ["parent"]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    list_display = ["name", "slug", "created_at"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    search_fields = [
        "name",
        "sku",
        "description",
        "short_description",
        "category__name",
        "tags__name",
    ]
    list_display = [
        "name",
        "sku",
        "category",
        "price",
        "stock_quantity",
        "is_active",
        "is_featured",
        "created_at",
    ]
    list_filter = ["is_active", "is_featured", "category", "created_at"]
    prepopulated_fields = {"slug": ("name",)}
    raw_id_fields = ["category"]
    filter_horizontal = ["tags"]


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    search_fields = [
        "product__name",
        "product__sku",
        "alt_text",
        "caption",
    ]
    list_display = ["product", "alt_text", "is_primary", "display_order", "created_at"]
    list_filter = ["is_primary", "created_at"]
    raw_id_fields = ["product"]


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    search_fields = [
        "product__name",
        "product__sku",
        "sku",
        "variant_name",
        "size",
        "color",
        "material",
    ]
    list_display = [
        "product",
        "variant_name",
        "sku",
        "size",
        "color",
        "stock_quantity",
        "is_active",
        "created_at",
    ]
    list_filter = ["is_active", "size", "color", "created_at"]
    raw_id_fields = ["product"]
