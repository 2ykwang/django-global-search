from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    """User profile with additional information."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField(blank=True)
    company = models.CharField(max_length=200, blank=True)
    job_title = models.CharField(max_length=100, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    website = models.URLField(blank=True)
    avatar_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_profiles"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["company"]),
            models.Index(fields=["job_title"]),
        ]

    def __str__(self):
        return f"{self.user.username}'s profile"


class Address(models.Model):
    """User address information."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
    address_type = models.CharField(
        max_length=20,
        choices=[
            ("home", "Home"),
            ("work", "Work"),
            ("billing", "Billing"),
            ("shipping", "Shipping"),
        ],
    )
    full_address = models.CharField(max_length=500)
    street_address = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "addresses"
        ordering = ["-is_default", "-created_at"]
        indexes = [
            models.Index(fields=["user", "is_default"]),
            models.Index(fields=["city"]),
            models.Index(fields=["postal_code"]),
        ]
        verbose_name_plural = "Addresses"

    def __str__(self):
        return f"{self.user.username} - {self.address_type}: {self.city}"


class PaymentMethod(models.Model):
    """Payment method information."""

    METHOD_TYPES = [
        ("credit_card", "Credit Card"),
        ("debit_card", "Debit Card"),
        ("paypal", "PayPal"),
        ("bank_transfer", "Bank Transfer"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payment_methods")
    method_type = models.CharField(max_length=20, choices=METHOD_TYPES)
    card_holder_name = models.CharField(max_length=200)
    card_last_four = models.CharField(max_length=4, blank=True)
    card_brand = models.CharField(max_length=50, blank=True)  # Visa, Mastercard, etc
    expiry_month = models.IntegerField(null=True, blank=True)
    expiry_year = models.IntegerField(null=True, blank=True)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "payment_methods"
        ordering = ["-is_default", "-created_at"]
        indexes = [
            models.Index(fields=["user", "is_default"]),
            models.Index(fields=["card_holder_name"]),
        ]

    def __str__(self):
        return f"{self.card_holder_name} - {self.method_type}"
