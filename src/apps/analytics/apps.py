from django.apps import AppConfig


class AnalyticsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.analytics"

    verbose_name = "Панель Аналитики"
    verbose_name_plural = "Панель Аналитики"
