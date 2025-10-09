from django.contrib import admin

from .models import Invoice, Order, OrderItem, Refund, ShippingAddress


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    search_fields = [
        "order_number",
        "user__username",
        "user__email",
        "notes",
    ]
    list_display = ["order_number", "user", "status", "total", "created_at"]
    list_filter = ["status", "created_at"]
    raw_id_fields = ["user"]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    search_fields = [
        "order__order_number",
        "order__user__username",
        "product__name",
        "product__sku",
        "variant__sku",
        "product_name",
        "sku",
        "item_notes",
    ]
    list_display = ["order", "product_name", "sku", "quantity", "unit_price", "total_price"]
    list_filter = ["created_at"]
    raw_id_fields = ["order", "product", "variant"]


@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    search_fields = [
        "order__order_number",
        "order__user__username",
        "recipient_name",
        "recipient_phone",
        "full_address",
        "city",
        "postal_code",
        "country",
        "delivery_instructions",
    ]
    list_display = ["order", "recipient_name", "city", "country", "created_at"]
    list_filter = ["country", "created_at"]
    raw_id_fields = ["order", "address"]


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    search_fields = [
        "invoice_number",
        "order__order_number",
        "order__user__username",
        "notes",
    ]
    list_display = ["invoice_number", "order", "amount", "is_paid", "invoice_date", "due_date"]
    list_filter = ["is_paid", "invoice_date"]
    raw_id_fields = ["order"]


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    search_fields = [
        "refund_number",
        "order__order_number",
        "order__user__username",
        "reason",
        "notes",
    ]
    list_display = ["refund_number", "order", "status", "amount", "requested_at"]
    list_filter = ["status", "requested_at"]
    raw_id_fields = ["order"]
