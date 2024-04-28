from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ReviewsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.reviews"

    verbose_name = _("Панель Отзыва")
    verbose_name_plural = _("Панель Отзывов")
