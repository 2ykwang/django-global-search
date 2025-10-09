from django.contrib import admin

from .models import (
    PurchaseOrder,
    PurchaseOrderItem,
    Stock,
    StockMovement,
    Supplier,
    Warehouse,
)


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    search_fields = [
        "name",
        "code",
        "location_address",
        "city",
        "country",
        "manager_name",
    ]
    list_display = ["name", "code", "city", "country", "capacity", "is_active", "created_at"]
    list_filter = ["is_active", "country", "created_at"]


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    search_fields = [
        "name",
        "company_name",
        "contact_person",
        "email",
        "phone_number",
        "city",
        "country",
    ]
    list_display = ["company_name", "contact_person", "email", "phone_number", "is_active"]
    list_filter = ["is_active", "country", "created_at"]


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    search_fields = [
        "product__name",
        "product__sku",
        "warehouse__name",
        "warehouse__code",
        "notes",
    ]
    list_display = [
        "product",
        "warehouse",
        "quantity",
        "reserved_quantity",
        "available_quantity",
        "updated_at",
    ]
    list_filter = ["warehouse", "updated_at"]
    raw_id_fields = ["product", "warehouse"]


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    search_fields = [
        "stock__product__name",
        "stock__product__sku",
        "stock__warehouse__name",
        "reference_number",
        "notes",
        "performed_by__username",
    ]
    list_display = [
        "stock",
        "movement_type",
        "quantity",
        "reference_number",
        "performed_by",
        "created_at",
    ]
    list_filter = ["movement_type", "created_at"]
    raw_id_fields = ["stock", "performed_by"]


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    search_fields = [
        "po_number",
        "supplier__company_name",
        "warehouse__name",
        "notes",
    ]
    list_display = ["po_number", "supplier", "warehouse", "status", "total_amount", "ordered_at"]
    list_filter = ["status", "ordered_at", "created_at"]
    raw_id_fields = ["supplier", "warehouse"]


@admin.register(PurchaseOrderItem)
class PurchaseOrderItemAdmin(admin.ModelAdmin):
    search_fields = [
        "purchase_order__po_number",
        "product__name",
        "product__sku",
        "notes",
    ]
    list_display = [
        "purchase_order",
        "product",
        "quantity",
        "received_quantity",
        "unit_price",
        "total_price",
    ]
    list_filter = ["created_at"]
    raw_id_fields = ["purchase_order", "product"]
