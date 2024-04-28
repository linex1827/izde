from apps.common.services import Service
import firebase_admin
from firebase_admin import credentials, messaging
from apps.notification.models import Notification
from apps.notification.utils import push_notifications


class NotificationService(Service):
    @staticmethod
    def multi_push_notifications_service(title, message):
        users = Notification.objects.all()
        tokens = []
        for user in users:
            tokens.append(user.token)
        push = push_notifications(title, message, tokens)
        return push

    @staticmethod
    def push_notifications_service(title, message, user_object):
        tokens = Notification.objects.get(user=user_object)
        push = push_notifications(title, message, tokens)
        return push