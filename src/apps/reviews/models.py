from django.db import models

from apps.reviews import constants
from apps.profiles.models.user import User
from apps.houserent.models import LocationObject
from apps.common.models import BaseModel
from django.utils.translation import gettext_lazy as _


class ObjectReview(BaseModel):
    user = models.ForeignKey(
        verbose_name=_("Автор отзыва"),
        to=User,
        on_delete=models.CASCADE,
        related_name="user_reviews",
    )
    object = models.ForeignKey(
        verbose_name=_("Объект"),
        to=LocationObject,
        on_delete=models.CASCADE,
        related_name="object_reviews",
    )
    quality = models.IntegerField(
        verbose_name=_("Соотношение цены"), choices=constants.STARS_CHOICE
    )
    conveniences = models.IntegerField(
        verbose_name=_("Удобства"), choices=constants.STARS_CHOICE
    )
    purity = models.IntegerField(
        verbose_name=_("Чистота"), choices=constants.STARS_CHOICE
    )
    location = models.IntegerField(
        verbose_name=_("Расположение"), choices=constants.STARS_CHOICE
    )
    comment = models.TextField(verbose_name=_("Комментарий к отзыву"))

    def __str__(self):
        return (
            f"Отзыв от: {self.user.email} \n"
            f"Объект: {self.object} \n"
            f"Комментарий: {self.comment}"
        )

    class Meta:
        db_table = "object_reviews"
        ordering = ["-created_at"]
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"


class ReviewCheck(BaseModel):
    review = models.ForeignKey(
        verbose_name=_("Объект"),
        to=ObjectReview,
        related_name="review_check",
        on_delete=models.CASCADE,
    )
    choice = models.CharField(
        max_length=20, choices=constants.REVIEW_STATUS_CHOICE, verbose_name=_("Статус")
    )

    def __str__(self):
        return f"{self.review.user.email}"

    class Meta:
        db_table = "review_checks"
        ordering = ["-created_at"]
        verbose_name = _("Проверка Модератора (Отзыв)")
        verbose_name_plural = _("Проверка Модератора (Отзыв)")
