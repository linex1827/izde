from django.contrib import admin
from apps.profiles.models import payment
from apps.common.admin import BaseAdmin
from apps.profiles.models import user as models
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _


@admin.register(models.User)
class UserAdmin(UserAdmin, BaseAdmin):
    ordering = []
    list_filter = []
    fieldsets = (
        (
            None,
            {"fields": ("email", "first_name", "last_name", "currency", "is_active", "password")},
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "currency",
                    "is_active",
                    "password1",
                    "password2",
                )
            },
        ),
    )

    exclude = ["groups", "is_superuser"]
    list_display = [
        "email",
        "first_name",
        "last_name",
    ]


@admin.register(models.Moderator)
class ModeratorAdmin(UserAdmin, BaseAdmin):
    ordering = []
    list_filter = []
    fieldsets = (
        (
            _("Основная информация"),
            {"fields": ("email", "first_name", "last_name", "password")},
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "password1",
                    "password2",
                )
            },
        ),
    )

    exclude = ["groups", "is_superuser"]
    list_display = [
        "email",
        "first_name",
        "last_name",
    ]

    def save_model(self, request, obj, form, change):
        obj.is_active = True
        obj.is_staff = True
        obj.is_moderator = True
        super().save_model(request, obj, form, change)


@admin.register(models.Currency)
class CurrencyAdmin(BaseAdmin):
    list_display = [
        "title",
        "price"
    ]
    fields = [
        "title",
        "price"
    ]
    ordering = ["-created_at"]


admin.site.register(payment.Transaction)
