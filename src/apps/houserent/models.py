import datetime
from django.core.validators import MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import BaseModel
from apps.profiles.models.user import Vendor, Currency, User
from apps.common.fields import CompressedImageField
from apps.houserent import validators, constants

from mptt import models as mptt_models


class ObjectCheck(BaseModel):
    object = models.ForeignKey(
        verbose_name=_("Объект"),
        to="LocationObject",
        related_name="objects_check",
        on_delete=models.CASCADE,
    )
    choice = models.CharField(
        max_length=20, choices=constants.OBJECT_STATUS_CHOICES, verbose_name=_("Статус")
    )
    is_checked = models.BooleanField(verbose_name=_("Проверено?"), default=False)
    is_declined = models.BooleanField(verbose_name=_("Отклонено?"), default=False)

    def __str__(self):
        return f"{self.object.name} - {self.choice}"

    class Meta:
        db_table = "object_checks"
        ordering = ["-created_at"]
        verbose_name = _("Проверка Модератора (Объект)")
        verbose_name_plural = _("Проверка Модератора (Объект)")


"""Локации"""


class Placement(mptt_models.MPTTModel):
    name = models.CharField(_("Название"), max_length=50, unique=True)
    parent = mptt_models.TreeForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="placements",
    )
    icon = CompressedImageField(
        verbose_name=_("Иконка Местоположения"),
        null=True,
        blank=True,
        upload_to="icons",
        default="icons/Group 4.svg",
    )
    is_deleted = models.BooleanField(default=False, verbose_name=_("удаленный?"))

    class MPTTMeta:
        order_insertion_by = ["name"]

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        validators.HouseRentValidator.check_placement(self.name)

    class Meta:
        verbose_name = _("Расположение")
        verbose_name_plural = _("Расположения")


class LocationImage(BaseModel):
    image = CompressedImageField(
        verbose_name=_("Фотография локаций"), null=True, blank=True
    )
    location = models.ForeignKey(
        verbose_name=_("Локация"),
        to="Location",
        related_name="image_locations",
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f"{self.location.name} - {self.id}"

    class Meta:
        db_table = "location_images"
        ordering = ["-created_at"]
        verbose_name = _("Фотография Локации")
        verbose_name_plural = _("Фотографии Локации")


class LocationFacility(BaseModel):
    name = models.CharField(
        verbose_name=_("Название удобства"),
        max_length=255,
        null=False,
        blank=False,
        unique=True,
    )

    def __str__(self):
        return self.name

    class Meta:
        db_table = "location_facilities"
        ordering = ["-created_at"]
        verbose_name = _("Удобство Локации")
        verbose_name_plural = _("Удобства Локации")


class Location(BaseModel):
    name = models.CharField(
        verbose_name=_("Название Локации"),
        max_length=255,
        null=False,
        blank=False,
        unique=True,
    )
    placement = models.ForeignKey(
        verbose_name=_("Расположение"),
        to=Placement,
        on_delete=models.CASCADE,
        related_name="location_placements",
    )
    street = models.CharField(
        verbose_name=_("Улица"), max_length=255, null=True, blank=True
    )
    house = models.CharField(
        verbose_name=_("Дом"), max_length=255, null=True, blank=True
    )
    address_link = models.URLField(
        verbose_name=_("Ссылка адреса"), null=False, blank=False
    )
    facility = models.ManyToManyField(
        verbose_name=_("Удобства"),
        to="LocationFacility",
        related_name="location_facilities",
    )
    rules = models.TextField(
        verbose_name=_("Правило проживания на территории"), null=False, blank=False
    )

    def __str__(self):
        return self.name

    class Meta:
        db_table = "locations"
        ordering = ["-created_at"]
        verbose_name = _("Локация")
        verbose_name_plural = _("Локации")


""" Объекты """


class ObjectFacility(BaseModel):
    name = models.CharField(
        verbose_name=_("Название удобства"),
        max_length=255,
        null=False,
        blank=False,
        unique=True,
    )

    def __str__(self):
        return self.name

    class Meta:
        db_table = "object_facilities"
        ordering = ["-created_at"]
        verbose_name = _("Удобство Объекта")
        verbose_name_plural = _("Удобства Объекта")


class ObjectType(BaseModel):
    name = models.CharField(
        verbose_name=_("Название типа размещения"),
        max_length=255,
        null=False,
        blank=False,
        unique=True,
    )
    counter = models.IntegerField(
        verbose_name=_("Номер Типа Размещения"), default=0, null=True, blank=True
    )
    icon = CompressedImageField(
        verbose_name=_("Иконка Типа Размещения"),
        null=True,
        blank=True,
        upload_to="icons",
        default="icons/dashicons_saved.svg",
    )

    def __str__(self):
        return self.name

    class Meta:
        db_table = "object_types"
        ordering = ["-created_at"]
        verbose_name = _("Тип Размещения Объекта")
        verbose_name_plural = _("Типы Размещения Объекта")


class ObjectKind(BaseModel):
    name = models.CharField(
        verbose_name=_("Название вида"),
        max_length=255,
        null=False,
        blank=False,
        unique=True,
    )
    counter = models.IntegerField(
        verbose_name=_("Вместимость"), default=0, null=True, blank=True
    )
    icon = CompressedImageField(
        verbose_name=_("Иконка Вида Размещения"),
        null=True,
        blank=True,
        upload_to="icons",
        default="icons/mdi_bed-double-outline.svg",
    )

    def __str__(self):
        return self.name

    class Meta:
        db_table = "object_kinds"
        ordering = ["-created_at"]
        verbose_name = _("Вид Объекта")
        verbose_name_plural = _("Виды Объекта")


class ObjectImage(BaseModel):
    image = CompressedImageField(
        verbose_name=_("Фотография Объекта"), null=True, blank=True
    )
    object = models.ForeignKey(
        verbose_name=_("Объект"),
        to="LocationObject",
        related_name="image_objects",
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f"{self.object.name} - {self.id}"

    class Meta:
        db_table = "object_images"
        ordering = ["-created_at"]
        verbose_name = _("Фотография Объекта")
        verbose_name_plural = _("Фотографии Объекта")


class ObjectPrice(BaseModel):
    start_date = models.DateField(verbose_name=_("Начало"), null=False, blank=False)
    end_date = models.DateField(verbose_name=_("Конец"), null=False, blank=False)
    price = models.IntegerField(verbose_name=_("Цена"), null=False, blank=False)
    object = models.ForeignKey(
        verbose_name=_("Объект"),
        to="LocationObject",
        related_name="object_prices",
        on_delete=models.CASCADE,
    )

    # def clean(self):
    #     validators.HouseRentValidator.validate_dates(start_date=self.start_date,
    #                                         end_date=self.end_date)

    def __str__(self):
        return f"{self.object.name}-{self.start_date}-{self.end_date}-{self.price}"

    class Meta:
        db_table = "object_prices"
        ordering = ["-created_at"]
        verbose_name = _("Цена объекта")
        verbose_name_plural = _("Цены объекта")


class LocationObject(BaseModel):
    location = models.ForeignKey(
        verbose_name=_("Локация"),
        to=Location,
        related_name="object_locations",
        on_delete=models.CASCADE,
    )
    vendor = models.ForeignKey(
        verbose_name=_("Вендор"),
        to=Vendor,
        related_name="vendors",
        on_delete=models.CASCADE,
    )
    name = models.CharField(
        verbose_name=_("Название объекта"), max_length=255, null=False, blank=False
    )
    description = models.TextField(
        verbose_name=_("Описание объекта"), null=False, blank=False
    )
    room_quantity = models.PositiveSmallIntegerField(
        verbose_name=_("Количество комнат"), null=False, blank=False
    )
    occupancy = models.PositiveSmallIntegerField(
        verbose_name=_("Вместимость"), null=False, blank=False
    )
    facility = models.ManyToManyField(
        verbose_name=_("Удобства Объекта"),
        to=ObjectFacility,
        related_name="object_facilities",
    )
    object_type = models.ForeignKey(
        verbose_name=_("Тип объекта рамзещения"),
        to=ObjectType,
        related_name="object_types",
        on_delete=models.CASCADE,
    )
    object_kind = models.ForeignKey(
        verbose_name=_("Вид объекта"),
        to=ObjectKind,
        related_name="object_kinds",
        on_delete=models.CASCADE,
    )
    check_in = models.TimeField(
        verbose_name=_("Заезд"), default=datetime.time(14, 0), null=False, blank=False
    )
    check_out = models.TimeField(
        verbose_name=_("Выезд"), default=datetime.time(12, 0), null=False, blank=False
    )
    rules = models.TextField(
        verbose_name=_("Правило проживания в объекте"), null=False, blank=False
    )

    partnership = models.PositiveIntegerField(
        verbose_name=_("Комиссия партнера"),
        validators=[MaxValueValidator(100)],
        default=15,
    )

    currency = models.ForeignKey(
        verbose_name=_("Валюта"),
        to=Currency,
        related_name="object_currency",
        on_delete=models.SET_NULL,
        null=True,
    )

    cancellation_policy = models.TextField(
        verbose_name=_("Правило Отмены"), null=False, blank=False
    )

    full_refund_cutoff_hours = models.IntegerField(default=48,
                                                   verbose_name=_("Часы до заселения для полного возврата"))

    partial_refund_cutoff_hours = models.IntegerField(default=24,
                                                      verbose_name=_("Часы до заселения для частичного возврата"))

    def clean(self):
        super().clean()
        validators.HouseRentValidator.validate_times(
            check_in=self.check_in, check_out=self.check_out
        )
        validators.HouseRentValidator.validate_unique_names_for_objects(
            id=self.pk, name=self.name, vendor_id=self.vendor.id
        )

    def __str__(self):
        return self.name

    class Meta:
        db_table = "objects"
        ordering = ["-created_at"]
        verbose_name = _("Объект")
        verbose_name_plural = _("Объекты")


class LocationObjectView(BaseModel):
    user = models.ForeignKey(verbose_name=_("Пользователь"), to=User,
                             on_delete=models.CASCADE, related_name="user_views")
    object = models.ForeignKey(verbose_name=_("Объект"), to=LocationObject,
                               on_delete=models.CASCADE, related_name="object_views")

    def __str__(self):
        return f"{self.user.email} - {self.object}"

    class Meta:
        db_table = "object_views"
        ordering = ["-created_at"]
        verbose_name = _("Просмотры Объекта")
        verbose_name_plural = _("Просмотры Объекта")
