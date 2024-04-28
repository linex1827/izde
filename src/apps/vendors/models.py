from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.common.models import BaseModel
from apps.profiles.models.user import Vendor


class Agreement(BaseModel):
    title = models.CharField(verbose_name=_("Заголовок соглашения"), max_length=255,
                             null=False, blank=False)
    description = models.TextField(verbose_name=_("Описание соглашения"),
                                   null=False, blank=False)

    def __str__(self):
        return self.title

    class Meta:
        db_table = "agreements"
        ordering = ["-created_at"]
        verbose_name = "Соглашение"
        verbose_name_plural = "Соглашения"
        
    
class VendorContract(BaseModel):
    vendor = models.ForeignKey(verbose_name=_("Вендор"), on_delete=models.CASCADE,
                               to=Vendor, related_name="vendors_сontracts")
    agreement = models.ManyToManyField(verbose_name=_("Соглашение с Вендором"),
                                       related_name="agreements",
                                       to="Agreement")

    def __str__(self):
        return self.vendor.email

    class Meta:
        db_table = "contracts"
        ordering = ["-created_at"]
        verbose_name = "Блок Контракта"
        verbose_name_plural = "Блок Контракта"


class QuestionBlock(BaseModel):
    title = models.CharField(verbose_name=_("Заголовок блока"), max_length=255,
                             null=False, blank=False)
    description = models.TextField(verbose_name=_("Описание блока"),
                                   null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = "question_blocks"
        ordering = ["-created_at"]
        verbose_name = "Блок Вопроса"
        verbose_name_plural = "Блок Вопроса"
