from decimal import Decimal

from django.contrib.auth.models import User
from django.db import models


class Order(models.Model):
    """Order model (300K rows)."""

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
        ("refunded", "Refunded"),
    ]

    order_number = models.CharField(max_length=50, unique=True, db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"))
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"))
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"))
    total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"))
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "orders"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["order_number"]),
            models.Index(fields=["user", "status"]),
            models.Index(fields=["status", "-created_at"]),
        ]

    def __str__(self):
        return f"Order {self.order_number} - {self.user.username}"


class OrderItem(models.Model):
    """Order items."""

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(
        "products.Product", on_delete=models.SET_NULL, null=True, related_name="order_items"
    )
    variant = models.ForeignKey(
        "products.ProductVariant",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order_items",
    )
    product_name = models.CharField(max_length=300)  # Snapshot at order time
    sku = models.CharField(max_length=100)  # Snapshot at order time
    quantity = models.IntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    item_notes = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "order_items"
        ordering = ["order", "id"]
        indexes = [
            models.Index(fields=["order"]),
            models.Index(fields=["product"]),
            models.Index(fields=["sku"]),
        ]

    def __str__(self):
        return f"{self.order.order_number} - {self.product_name} x{self.quantity}"


class ShippingAddress(models.Model):
    """Shipping address for orders."""

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="shipping_address")
    address = models.ForeignKey(
        "users.Address",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="shipping_orders",
    )
    recipient_name = models.CharField(max_length=200)
    recipient_phone = models.CharField(max_length=20)
    full_address = models.CharField(max_length=500)
    street_address = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    delivery_instructions = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "shipping_addresses"
        indexes = [
            models.Index(fields=["order"]),
            models.Index(fields=["postal_code"]),
        ]

    def __str__(self):
        return f"{self.order.order_number} - {self.recipient_name}"


class Invoice(models.Model):
    """Invoice for orders."""

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="invoice")
    invoice_number = models.CharField(max_length=50, unique=True, db_index=True)
    invoice_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(null=True, blank=True)
    paid_date = models.DateTimeField(null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "invoices"
        ordering = ["-invoice_date"]
        indexes = [
            models.Index(fields=["invoice_number"]),
            models.Index(fields=["is_paid", "-invoice_date"]),
        ]

    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.order.order_number}"


class Refund(models.Model):
    """Refund for orders."""

    STATUS_CHOICES = [
        ("requested", "Requested"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("processed", "Processed"),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="refunds")
    refund_number = models.CharField(max_length=50, unique=True, db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="requested")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.TextField()
    notes = models.TextField(blank=True)
    requested_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "refunds"
        ordering = ["-requested_at"]
        indexes = [
            models.Index(fields=["refund_number"]),
            models.Index(fields=["order", "status"]),
        ]

    def __str__(self):
        return f"Refund {self.refund_number} - {self.order.order_number}"
