from rest_framework import serializers
from apps.notification.models import Notification


class NotificationSerializer(serializers.Serializer):
    token = serializers.CharField()

