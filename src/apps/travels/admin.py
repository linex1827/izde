from django.contrib import admin
from simple_history.models import HistoricalRecords

from apps.travels import models


@admin.register(models.TravelDetail)
class TravelDetailAdmin(admin.ModelAdmin):
    history = HistoricalRecords()
    list_display = ["id", 'user', 'placement', 'object_type', 'object_kind', 'is_deleted']
    list_display_links = ['id']
    fields = [
        'user',
        'placement',
        'budget',
        'guests',
        'date',
        'facilities',
        'object_type',
        'object_kind',
        'commentary'
    ]
    ordering = ['-created_at']
    search_fields = ['placement__name']
    list_filter = ['object_type', 'object_kind']


@admin.register(models.TravelDate)
class TravelDateAdmin(admin.ModelAdmin):
    history = HistoricalRecords()
    list_display = ['id', 'start_date', 'end_date', 'is_deleted']
    list_display_links = ['id']
    fields = ['start_date', 'end_date', 'icon']
    ordering = ['-created_at']


@admin.register(models.FacilitiesQuantity)
class FacilitiesQuantityAdmin(admin.ModelAdmin):
    history = HistoricalRecords()
    list_display = ['id', 'facilities_quantity', 'is_deleted']
    list_display_links = ['id']
    fields = ['facilities_quantity', 'icon']
    ordering = ['-created_at']


@admin.register(models.TravelBudget)
class TravelBudgetAdmin(admin.ModelAdmin):
    history = HistoricalRecords()
    list_display = ['id', 'min_sum', 'max_sum', 'is_deleted']
    list_display_links = ['id']
    fields = ['min_sum', 'max_sum', 'icon']
    ordering = ['-created_at']


@admin.register(models.GuestQuantity)
class GuestQuantityAdmin(admin.ModelAdmin):
    history = HistoricalRecords()
    list_display = ['id', 'guest_quantity', 'is_deleted']
    list_display_links = ['id']
    fields = ['guest_quantity', 'icon']
    ordering = ['-created_at']


@admin.register(models.Orders)
class OrdersAdmin(admin.ModelAdmin):
    history = HistoricalRecords()
    list_display = ['id', 'travel_detail', 'match_object', 'approved', 'is_deleted']
    list_display_links = ['id']
    fields = ['travel_detail', 'match_object', 'approved']
    ordering = ['-created_at']


@admin.register(models.TravelOffer)
class OrdersAdmin(admin.ModelAdmin):
    history = HistoricalRecords()
    list_display = ['id', 'order_number', 'price', 'is_payed', 'is_deleted']
    list_display_links = ['id']
    fields = ['order', 'order_number', 'comment', 'price', 'is_payed', 'is_accepted']
    ordering = ['-created_at']
