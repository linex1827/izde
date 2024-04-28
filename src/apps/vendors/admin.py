from django.contrib import admin

from apps.common.admin import BaseAdmin
from apps.vendors import models
from apps.profiles.models.user import Vendor, UserResetCode
from django.contrib.auth.admin import UserAdmin


@admin.register(models.Agreement)
class AgreementAdmin(BaseAdmin):
    list_display = [
        "title"
    ]
    list_display_links = [
        "title"
    ]
    fields = [
        "title",
        "description"
    ]
    ordering = ["-created_at"]
    search_fields = ["title"]


@admin.register(models.VendorContract)
class VendorContractAdmin(BaseAdmin):
    list_display = [
        "vendor"
    ]
    list_display_links = [
        "vendor"
    ]
    fields = [
        "vendor",
        "agreement"
    ]
    ordering = ["-created_at"]
    search_fields = ["title"]


@admin.register(models.QuestionBlock)
class QuestionBlockAdmin(BaseAdmin):
    list_display = [
        "title"
    ]
    list_display_links = [
        "title"
    ]
    fields = [
        "title",
        "description"
    ]
    ordering = ["-created_at"]
    search_fields = ["title"]


@admin.register(Vendor)
class VendorAdmin(UserAdmin):
    ordering = []
    list_filter = []
    list_display = [
        "email",
        'first_name',
        'last_name',
    ]
    fieldsets = (
        (
            None,
            {
                'fields': (
                    'email',
                    'first_name',
                    'last_name',
                    'phone_number',
                    'is_active',
                    'password',
                    'twofa',
                    'secret_key'
                )
            },
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                'fields': (
                    'email',
                    'first_name',
                    'last_name',
                    'phone_number',
                    'is_active',
                    'password1',
                    'password2',
                )
            },
        ),
    )


admin.site.register(UserResetCode)