from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from apps.profiles.models.managers import CustomUserManager
from apps.common.models import BaseModel
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractBaseUser, BaseModel, PermissionsMixin):
    icon = models.ImageField(verbose_name=_("Картинка профиля"), null=True, blank=True,
                             upload_to="users/icons/")
    email = models.EmailField(verbose_name=_("Почта"), unique=True, db_index=True)
    phone_number = models.CharField(verbose_name=_("Номер телефона"), max_length=50, blank=True, null=True)
    first_name = models.CharField(verbose_name=_("Имя"), max_length=100)
    last_name = models.CharField(verbose_name=_("Фамилия"), max_length=100)
    is_active = models.BooleanField(verbose_name=_("Подтвержден ли?"), default=False)
    is_staff = models.BooleanField(verbose_name=_("Является ли админом?"), default=False)
    is_moderator = models.BooleanField(verbose_name=_("Является модератором?"), default=False)
    reset_code = models.ForeignKey('UserResetCode', on_delete=models.SET_NULL, blank=True, null=True, )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def has_module_perms(self, app_label):
        return self.is_staff or self.is_moderator

    def has_perm(self, perm, obj=None):
        return self.is_staff or self.is_moderator


class Currency(BaseModel):
    title = models.CharField(
        verbose_name=_("Название валюты"),
        null=False,
        blank=False,
        unique=True
    )
    price = models.FloatField(
        verbose_name=_("Цена"),
        null=False,
        blank=False,
    )

    def __str__(self):
        return f"{self.title} - {self.price}"

    class Meta:
        db_table = "currencies"
        verbose_name = "Валюта"
        verbose_name_plural = "Валюта"


class User(CustomUser):
    currency = models.ForeignKey(
        verbose_name=_("Валюта"),
        to="Currency",
        on_delete=models.SET_NULL,
        related_name="user_currencies",
        null=True
    )

    class Meta:
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')

    def __str__(self):
        return f"{self.email}"


class Vendor(CustomUser):
    secret_key = models.CharField(max_length=100, null=True, blank=True)
    twofa = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('Вендор')
        verbose_name_plural = _('Вендоры')

    def __str__(self):
        return f"{self.email}"


class Moderator(CustomUser):
    class Meta:
        verbose_name = _('Модератор')
        verbose_name_plural = _('Модераторы')

    def __str__(self):
        return f"{self.email}"


class TemporaryUser(BaseModel):
    email = models.EmailField()
    phone_number = models.CharField(max_length=50, blank=True, null=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    password = models.CharField(max_length=255)
    code = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()


class UserResetCode(BaseModel):
    code = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
