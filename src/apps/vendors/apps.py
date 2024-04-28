from django.apps import AppConfig


class VendorsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.vendors'

    verbose_name = "Панель Вендора"
    verbose_name_plural = "Панель Вендора"