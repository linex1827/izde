from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from simple_history.models import HistoricalRecords

from apps.common.admin import BaseAdmin
from apps.houserent import models
from mptt.admin import DraggableMPTTAdmin


class LocationImageTabularInline(admin.TabularInline):
    model = models.LocationImage
    fields = ["image"]
    extra = 1


class ObjectImageTabularInline(admin.TabularInline):
    model = models.ObjectImage
    fields = ["image"]
    extra = 1


class ObjectPriceStackedInline(admin.StackedInline):
    model = models.ObjectPrice
    fields = ["start_date", "end_date", "price"]
    extra = 1


@admin.register(models.ObjectCheck)
class ObjectCheckAdmin(BaseAdmin):
    list_display = ["choice", "object_link", "is_checked"]
    list_display_links = ["choice", "object_link"]
    list_filter = ["choice", "is_checked"]
    search_fields = ["object__name"]

    fields = ["object", "choice", "is_checked", "is_declined", "is_deleted",]

    def object_link(self, obj):
        url = reverse("admin:houserent_locationobject_change", args=[obj.object.pk])
        return format_html('<a href="{}">{}</a>', url, obj.object.name)

    object_link.short_description = "Объект"
    object_link.admin_order_field = "object__name"


@admin.register(models.Placement)
class PlacementAdmin(DraggableMPTTAdmin, BaseAdmin):
    list_display = ["tree_actions", "indented_title", "name", "is_deleted"]
    list_display_links = ["indented_title"]
    search_fields = ["name"]
    list_filter = ["parent"]


@admin.register(models.Location)
class LocationAdmin(BaseAdmin):
    history = HistoricalRecords()
    list_display = ["name", "is_deleted"]
    list_display_links = ["name"]
    fields = [
        "name",
        "placement",
        "street",
        "house",
        "address_link",
        "facility",
        "rules",
        "is_deleted",
    ]
    ordering = ["-created_at"]
    search_fields = ["name"]
    inlines = [LocationImageTabularInline]


@admin.register(models.LocationFacility)
class FacilityAdmin(BaseAdmin):
    history = HistoricalRecords()
    list_display = ["name", "is_deleted"]
    list_display_links = ["name"]
    fields = ["name", "is_deleted"]
    ordering = ["-created_at"]
    search_fields = ["name"]


"""Объекты"""


@admin.register(models.ObjectFacility)
class ObjectFacilityAdmin(BaseAdmin):
    history = HistoricalRecords()
    list_display = ["name", "is_deleted"]
    list_display_links = ["name"]
    fields = ["name", "is_deleted"]
    ordering = ["-created_at"]
    search_fields = ["name"]


@admin.register(models.ObjectType)
class ObjectTypeAdmin(BaseAdmin):
    history = HistoricalRecords()
    list_display = ["name", "is_deleted"]
    list_display_links = ["name"]
    fields = ["name", "is_deleted"]
    ordering = ["-created_at"]
    search_fields = ["name"]


@admin.register(models.ObjectKind)
class ObjectKindAdmin(BaseAdmin):
    history = HistoricalRecords()
    list_display = ["name", "counter", "is_deleted"]
    list_display_links = ["name"]
    fields = ["name", "counter", "is_deleted"]
    ordering = ["-created_at"]
    search_fields = ["name"]


@admin.register(models.LocationObject)
class LocationObjectAdmin(BaseAdmin):
    history = HistoricalRecords()
    list_display = ["name", "is_deleted"]
    inlines = [ObjectPriceStackedInline, ObjectImageTabularInline]
    list_display_links = ["name"]
    fields = [
        "location",
        "vendor",
        "name",
        "description",
        "room_quantity",
        "occupancy",
        "facility",
        "object_type",
        "object_kind",
        "check_in",
        "check_out",
        "rules",
        "partnership",
        "currency",
        "is_deleted",
        "full_refund_cutoff_hours",
        "partial_refund_cutoff_hours",
        "cancellation_policy",
    ]

    ordering = ["-created_at"]
    search_fields = ["name"]
