from django.urls import path

from apps.profiles.views import payment
from apps.profiles.views.payment import PaymentInitAPIView, ResultURLAPIView, BookedPaymentDetailAPIView

urlpatterns = [
    path('payment_init/', PaymentInitAPIView.as_view()),
    path('payment_result/', ResultURLAPIView.as_view(), name='payment_result'),
    path('payment_detail/<uuid:offer_id>/', payment.PaymentDetailAPIView.as_view()),
    path('booked_payment_detail/<uuid:offer_id>/', BookedPaymentDetailAPIView.as_view())
]