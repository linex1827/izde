from django.urls import path
from apps.notification.views import ActivateNotificationView

urlpatterns = [
    path('activate/', ActivateNotificationView.as_view(), name='activate'),
]