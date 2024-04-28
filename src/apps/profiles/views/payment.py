from rest_framework import generics, permissions, reverse, response, status, mixins
from django.urls import reverse
from apps.profiles.serializers import payment as payment_serializer
from apps.profiles.services import payment as payment_services
from apps.profiles.serializers import user as user_serializers
from apps.profiles.services.payment import PaymentService
from rest_framework.permissions import IsAuthenticated

from apps.profiles.tasks.broker import send_payment_status


# Create your views here.

class PaymentInitAPIView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = payment_serializer.InitPaymentSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payment_services.PaymentService.booking_offer(self.request.data)
        transaction = payment_services.PaymentService.create_transaction(
            user=request.user.user,
            amount=serializer.validated_data.get("amount"),
            offer_id=self.request.data.get('travel_offer'),
        )

        link = payment_services.PaymentService.payment(
            pg_order_id=transaction.id,
            pg_amount=transaction.amount,
            pg_description=transaction.pg_description,
            pg_salt=transaction.user.email,
            pg_result_url=str(self.request.build_absolute_uri(reverse("profiles_payment:payment_result"))),
            # pg_success_url=success_url,
            # pg_success_url_method="GET",
        )
        return response.Response(
            data={"payment_link": link["response"]},
            status=status.HTTP_200_OK
            if link["response"]["pg_status"] == "ok"
            else status.HTTP_400_BAD_REQUEST,
        )


class ResultURLAPIView(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = payment_serializer.ResultURLSerializers

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = payment_services.PaymentService.result_url(
            pg_order_id=serializer.validated_data.get("pg_order_id"),
            pg_payment_id=serializer.validated_data.get("pg_payment_id"),
            pg_salt=serializer.validated_data.get("pg_salt"),
            pg_sig=serializer.validated_data.get("pg_sig"),
            pg_payment_date=serializer.validated_data.get("pg_payment_date"),
            pg_result=serializer.validated_data.get("pg_result"),
        )
        send_payment_status.delay(str(data.first().id))
        res = payment_services.PaymentService.answer(pg_status=data.first().pg_result)
        return response.Response(data=res)


class PaymentDetailAPIView(generics.RetrieveAPIView):
    serializer_class = user_serializers.PaymentDetailSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return PaymentService.get_payment_detail(kwargs['offer_id'], request)



class BookedPaymentDetailAPIView(generics.RetrieveAPIView):
    serializer_class = payment_serializer.BookedOfferDateSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return PaymentService.get_booked_payment_detail(kwargs['offer_id'], request)

