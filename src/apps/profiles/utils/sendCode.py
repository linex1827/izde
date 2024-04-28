from django.core.mail import send_mail
from core.settings.base import EMAIL_HOST_USER as from_email


def send_verification_mail(email, generated_code):
    subject = 'Your verification code'
    message = f'Your verification code:\n{generated_code}\nThanks for using our application.'
    send_mail(subject, message, from_email, [email])


