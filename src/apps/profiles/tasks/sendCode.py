import json
import pika

import redis
from django.core.mail import send_mail
from core.settings.base import EMAIL_HOST_USER as from_email
from celery import shared_task


@shared_task
def send_verification_code_task(email):
    subject = 'Жилье в аренду'
    message = 'Вы успешно забронировали жилье'
    send_mail(subject, message, from_email, [email])
