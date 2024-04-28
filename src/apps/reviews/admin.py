from django.contrib import admin
from simple_history.models import HistoricalRecords
from apps.reviews import models
from django.urls import reverse
from django.utils.html import format_html


@admin.register(models.ObjectReview)
class ObjectReviewAdmin(admin.ModelAdmin):
    history = HistoricalRecords()
    list_display = ["id", "user", "object"]
    list_display_links = ["id"]
    fields = [
        "user",
        "object",
        "quality",
        "conveniences",
        "purity",
        "location",
        "comment",
        "is_deleted"
    ]
    ordering = ["-created_at"]


@admin.register(models.ReviewCheck)
class ReviewCheckAdmin(admin.ModelAdmin):
    list_display = ["review", "review_link"]
    list_display_links = ["review", "review_link"]
    list_filter = ["choice"]
    search_fields = ["review__comment"]

    fields = ["review", "choice", "is_deleted"]

    def review_link(self, obj):
        url = reverse("admin:reviews_objectreview_change", args=[obj.review.pk])
        return format_html('<a href="{}">{}</a>', url,
                           f"Проверка отзыва")

    review_link.short_description = "Отзыв"
    review_link.admin_order_field = "review__comment"

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if obj.choice == 'approved':
            obj.review.is_deleted = True
            obj.review.save()
