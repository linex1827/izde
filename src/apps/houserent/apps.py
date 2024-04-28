from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class HouserentConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.houserent"

    verbose_name = _("Панель Жилья")
    verbose_name_plural = _("Панель Жилья")
