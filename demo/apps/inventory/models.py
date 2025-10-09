from django.db import models


class Warehouse(models.Model):
    """Warehouse model."""

    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True, db_index=True)
    location_address = models.CharField(max_length=500)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    capacity = models.IntegerField(default=0)
    manager_name = models.CharField(max_length=200, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "warehouses"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"


class Supplier(models.Model):
    """Supplier model."""

    name = models.CharField(max_length=200)
    company_name = models.CharField(max_length=300)
    contact_person = models.CharField(max_length=200)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    address = models.CharField(max_length=500, blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "suppliers"
        ordering = ["company_name"]
        indexes = [
            models.Index(fields=["company_name"]),
            models.Index(fields=["email"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return self.company_name


class Stock(models.Model):
    """Stock model (200K rows)."""

    product = models.ForeignKey("products.Product", on_delete=models.CASCADE, related_name="stocks")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name="stocks")
    quantity = models.IntegerField(default=0)
    reserved_quantity = models.IntegerField(default=0)  # Reserved for orders
    available_quantity = models.IntegerField(default=0)  # quantity - reserved
    reorder_level = models.IntegerField(default=10)
    notes = models.TextField(blank=True)
    last_restocked_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "stocks"
        ordering = ["-updated_at"]
        unique_together = [["product", "warehouse"]]
        indexes = [
            models.Index(fields=["product", "warehouse"]),
            models.Index(fields=["warehouse", "quantity"]),
        ]

    def __str__(self):
        return f"{self.product.name} @ {self.warehouse.name} - Qty: {self.quantity}"


class StockMovement(models.Model):
    """Stock movement history."""

    MOVEMENT_TYPES = [
        ("in", "Stock In"),
        ("out", "Stock Out"),
        ("transfer", "Transfer"),
        ("adjustment", "Adjustment"),
        ("return", "Return"),
    ]

    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name="movements")
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
    quantity = models.IntegerField()  # Can be negative for out movements
    reference_number = models.CharField(max_length=100, blank=True)  # PO, Order, etc
    notes = models.TextField(blank=True)
    performed_by = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="stock_movements",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "stock_movements"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["stock", "-created_at"]),
            models.Index(fields=["movement_type", "-created_at"]),
            models.Index(fields=["reference_number"]),
        ]

    def __str__(self):
        return f"{self.movement_type} - {self.quantity} @ {self.stock}"


class PurchaseOrder(models.Model):
    """Purchase order from suppliers."""

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("sent", "Sent"),
        ("confirmed", "Confirmed"),
        ("received", "Received"),
        ("cancelled", "Cancelled"),
    ]

    po_number = models.CharField(max_length=50, unique=True, db_index=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name="purchase_orders")
    warehouse = models.ForeignKey(
        Warehouse, on_delete=models.CASCADE, related_name="purchase_orders"
    )
    products = models.ManyToManyField(
        "products.Product", through="PurchaseOrderItem", related_name="purchase_orders"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    ordered_at = models.DateTimeField(null=True, blank=True)
    expected_delivery = models.DateTimeField(null=True, blank=True)
    received_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "purchase_orders"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["po_number"]),
            models.Index(fields=["supplier", "status"]),
            models.Index(fields=["status", "-created_at"]),
        ]

    def __str__(self):
        return f"PO {self.po_number} - {self.supplier.company_name}"


class PurchaseOrderItem(models.Model):
    """Purchase order items (through table for M2M)."""

    purchase_order = models.ForeignKey(
        PurchaseOrder, on_delete=models.CASCADE, related_name="items"
    )
    product = models.ForeignKey(
        "products.Product", on_delete=models.CASCADE, related_name="po_items"
    )
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    received_quantity = models.IntegerField(default=0)
    notes = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "purchase_order_items"
        ordering = ["purchase_order", "id"]
        indexes = [
            models.Index(fields=["purchase_order"]),
            models.Index(fields=["product"]),
        ]

    def __str__(self):
        return f"{self.purchase_order.po_number} - {self.product.name}"
