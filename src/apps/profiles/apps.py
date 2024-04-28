from django.apps import AppConfig


class ProfilesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.profiles'
    verbose_name = "Панель Профиля"
    verbose_name_plural = "Панель Профилей"

    def ready(self):
        import apps.profiles.admin.user
