from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import Address, PaymentMethod, UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False


class UserAdmin(BaseUserAdmin):
    inlines = [UserProfileInline]
    search_fields = [
        "username",
        "email",
        "first_name",
        "last_name",
        "profile__company",
        "profile__job_title",
        "profile__bio",
    ]
    list_display = ["username", "email", "first_name", "last_name", "is_staff", "date_joined"]
    list_filter = ["is_staff", "is_active", "date_joined"]


# Unregister the default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    search_fields = [
        "user__username",
        "user__email",
        "company",
        "job_title",
        "bio",
        "phone_number",
    ]
    list_display = ["user", "company", "job_title", "phone_number", "created_at"]
    list_filter = ["created_at"]
    raw_id_fields = ["user"]


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    search_fields = [
        "user__username",
        "user__email",
        "full_address",
        "street_address",
        "city",
        "postal_code",
        "country",
    ]
    list_display = ["user", "address_type", "city", "country", "is_default", "created_at"]
    list_filter = ["address_type", "is_default", "country", "created_at"]
    raw_id_fields = ["user"]


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    search_fields = [
        "user__username",
        "user__email",
        "card_holder_name",
        "card_last_four",
        "card_brand",
    ]
    list_display = [
        "user",
        "card_holder_name",
        "method_type",
        "card_brand",
        "is_default",
        "is_active",
        "created_at",
    ]
    list_filter = ["method_type", "is_default", "is_active", "created_at"]
    raw_id_fields = ["user"]
