from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common.models import BaseModel
from apps.houserent.models import Placement, ObjectType, ObjectKind, LocationObject
from apps.profiles.models.user import User
from apps.common.fields import CompressedImageField


"""Количество гостей"""


class GuestQuantity(BaseModel):
    guest_quantity = models.IntegerField(verbose_name=_('Количество Гостей'))
    icon = CompressedImageField(
        verbose_name=_('Иконка Количества Гостей'),
        blank=True, null=True,
        upload_to='icons',
        default='icons/Vector.svg'
    )

    def __str__(self):
        return f'{self.guest_quantity}'

    class Meta:
        db_table = "guest_quantity"
        ordering = ["-created_at"]
        verbose_name = "Количество гостей"
        verbose_name_plural = "Количество гостей"


"""Бюджет"""


class TravelBudget(BaseModel):
    min_sum = models.CharField(verbose_name=_('Минимальная Сумма'), max_length=100)
    max_sum = models.CharField(verbose_name=_('Максимальная Сумма'), max_length=100)
    icon = CompressedImageField(
        verbose_name=_('Иконка Бюджета'),
        blank=True,
        null=True,
        upload_to='icons',
        default='icons/money-bill-solid 3.svg')

    def __str__(self):
        return f'{self.min_sum} - {self.max_sum}'

    class Meta:
        db_table = "travel_budget"
        ordering = ["-created_at"]
        verbose_name = "Бюджет"
        verbose_name_plural = "Бюджет"


"""Количество объектов"""


class FacilitiesQuantity(BaseModel):
    facilities_quantity = models.IntegerField(verbose_name=_('Количество Объектов'))
    icon = CompressedImageField(
        verbose_name=_('Иконка Количества Объектов'),
        blank=True,
        null=True,
        upload_to='icons',
        default='icons/uil_object-group.svg'
    )

    def __str__(self):
        return f'{self.facilities_quantity}'

    class Meta:
        db_table = "facilities_quantity"
        ordering = ["-created_at"]
        verbose_name = "Количество объктов"
        verbose_name_plural = "Количество объктов"


"""Дата поездки"""


class TravelDate(BaseModel):
    start_date = models.DateField(verbose_name=_('Начало Поездки'))
    end_date = models.DateField(verbose_name=_('Конец Поездки'))
    icon = CompressedImageField(
        verbose_name=_('Иконка Даты'),
        blank=True,
        null=True,
        upload_to='icons',
        default='icons/calendar-days-solid 1.svg'
    )

    def __str__(self):
        return f'{self.start_date} - {self.end_date}'

    class Meta:
        db_table = "travel_date"
        ordering = ["-created_at"]
        verbose_name = "Дата поездки"
        verbose_name_plural = "Дата поездки"


class TravelDetail(BaseModel):
    placement = models.ForeignKey(
        Placement,
        on_delete=models.CASCADE,
        related_name='travel',
        verbose_name=_('Местоположение')
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='travel',
        verbose_name=_('Пользователь')
    )
    date = models.ForeignKey(
        TravelDate,
        on_delete=models.CASCADE,
        related_name='travel',
        verbose_name=_('Дата')
    )
    budget = models.ForeignKey(
        TravelBudget,
        on_delete=models.CASCADE,
        related_name='travel',
        verbose_name=_('Бюджет')
    )
    guests = models.ForeignKey(
        GuestQuantity,
        on_delete=models.CASCADE,
        related_name='travel',
        verbose_name=_('Гости')
    )
    facilities = models.ForeignKey(
        FacilitiesQuantity,
        on_delete=models.CASCADE,
        related_name='travel',
        verbose_name=_('Объекты')
    )
    object_type = models.ForeignKey(
        ObjectType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='travel',
        verbose_name=_('Тип Объекта')
    )
    object_kind = models.ForeignKey(
        ObjectKind,
        on_delete=models.CASCADE,
        related_name='travel',
        verbose_name=_('Вид Объекта')
    )
    commentary = models.TextField(
        verbose_name=_('Комментарий'),
        null=True,
        blank=True
    )

    def __str__(self):
        return f'{self.user.email}'

    class Meta:
        db_table = "travel_detail"
        ordering = ["-created_at"]
        verbose_name = "Детали путешествия"
        verbose_name_plural = "Детали путешествия"


class Orders(BaseModel):
    travel_detail = models.ForeignKey(
        TravelDetail,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name=_('Поиск Пользователя')
    )
    match_object = models.ForeignKey(
        LocationObject,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name=_('Подходящий Объект')
    )
    approved = models.BooleanField(
        verbose_name=_('Одобрено'),
        null=True,
        blank=True
    )
    is_sent = models.BooleanField(
        verbose_name=_('Отправлено'),
        default=False
    )

    def __str__(self):
        return f'order for {self.match_object.name}'

    class Meta:
        db_table = "order"
        ordering = ["-created_at"]
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"


class TravelOffer(BaseModel):
    order = models.ForeignKey(
        Orders,
        on_delete=models.CASCADE,
        related_name='offers',
        verbose_name=_('Заказ')
    )
    is_payed = models.BooleanField(verbose_name=_('Оплачено'), null=True, blank=True)
    is_accepted = models.BooleanField(
        verbose_name=_('Принято'),
        null=True,
        blank=True
    )
    order_number = models.BigIntegerField(verbose_name=_('Номер Заказа'), unique=True)
    comment = models.TextField(
        verbose_name=_('Комментарий'),
        null=True,
        blank=True
    )
    price = models.BigIntegerField(verbose_name=_('Цена'))
    is_sent = models.BooleanField(
        verbose_name=_('Отправлено'),
        default=False
    )

    first_name = models.CharField(max_length=200, verbose_name=_('Имя для брони'),  null=True, blank=True)
    last_name = models.CharField(max_length=200, verbose_name=_('Фамилия для брони'), null=True, blank=True)
    email = models.EmailField(verbose_name=_('Почта для брони'), null=True, blank=True)
    phone_number = models.CharField(
        max_length=200,
        verbose_name=_('Номер телефона для брони'),
        null=True,
        blank=True
    )

    def __str__(self):
        return f'{self.order_number}'

    class Meta:
        db_table = "offer"
        ordering = ["-created_at"]
        verbose_name = "Предложение Вендора"
        verbose_name_plural = "Предложения Вендоров"
