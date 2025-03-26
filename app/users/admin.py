from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

User = get_user_model()


@admin.register(User)
class UserAdmin(BaseUserAdmin, admin.ModelAdmin):
    list_display = ["username", "first_name", "last_name", "date_joined", "email", "is_superuser"]
    readonly_fields = ["last_login"]
    list_filter = ["is_staff", "is_superuser", "is_active", "is_verified"]
    search_fields = ["username", "first_name", "last_name"]
    filter_horizontal = ["groups", "user_permissions"]

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            "Персональная информация",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "short_name",
                    "email",
                    "is_verified",
                )
            },
        ),
        (
            "Разрешения",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Даты", {"fields": ("last_login", "date_joined")}),
    )
