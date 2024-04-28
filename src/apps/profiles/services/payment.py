import hashlib
from django.db import transaction as trs
from apps.profiles.models.payment import Transaction
import requests
import xmltodict
import json
from django.core.exceptions import ObjectDoesNotExist
from json2xml import json2xml
from json2xml.utils import readfromstring
from rest_framework.response import Response

from apps.profiles.serializers.payment import BookedOfferSerializer
from apps.profiles.serializers.user import PaymentDetailSerializer
from apps.travels.models import TravelOffer


class PaymentService:
    __travel_offer = TravelOffer
    __model = Transaction
    __pg_testing_mode = 1
    __merchant_id = 553628
    __merchant_secret = 'fm3ari4eHfOjrASK'

    @classmethod
    def create_transaction(cls, user, amount, offer_id):
        offer = cls.__travel_offer.objects.filter(id=offer_id).first()
        if user != offer.order.travel_detail.user:
            raise cls.__model.DoesNotExist("Заказ который был отправлен не является заказом этого пользователя")
        transaction, created = cls.__model.objects.get_or_create(
            user=user,
            travel_offer=offer,
            pg_description=f'ОПЛАТА ЗА БРОНИРОВАНИЕ'
        )
        if created:
            transaction.amount = amount
            transaction.save()
        return transaction

    @classmethod
    def payment(
            cls,
            pg_order_id,
            pg_amount,
            pg_description,
            pg_salt,
            pg_result_url,
            # pg_success_url,
            # pg_success_url_method="GET",
    ):
        link = cls.__get_payment_link(
            pg_order_id=pg_order_id,
            pg_amount=pg_amount,
            pg_description=pg_description,
            pg_salt=pg_salt,
            pg_result_url=pg_result_url,
            # pg_success_url=pg_success_url,
            # pg_success_url_method=pg_success_url_method,
        )
        response = requests.post(link)
        text = xmltodict.parse(response.text)
        res = json.dumps(text)

        return json.loads(res)

    @staticmethod
    def __get_hash_signature(base_url, *args):
        for i in args:
            base_url += ";" + str(i)
        return hashlib.md5(base_url.encode())

    @classmethod
    def __get_payment_link(
            cls,
            pg_order_id,
            pg_amount,
            pg_description,
            pg_salt,
            pg_result_url,
            # pg_success_url,
            # pg_success_url_method
    ):
        sig = cls.__get_hash_signature(
            "init_payment.php",
            pg_amount,
            pg_description,
            cls.__merchant_id,
            pg_order_id,
            pg_result_url,
            pg_salt,
            # pg_success_url,
            # pg_success_url_method,
            cls.__pg_testing_mode,
            cls.__merchant_secret,
        )

        link = (
                "https://api.paybox.money/init_payment.php?"
                "pg_order_id=%s&"
                "pg_merchant_id=%s&"
                "pg_amount=%s&"
                "pg_description=%s&"
                "pg_salt=%s&"
                "pg_sig=%s&"
                "pg_result_url=%s&"
                "pg_testing_mode=%s"
                % (
                    pg_order_id,
                    cls.__merchant_id,
                    pg_amount,
                    pg_description,
                    pg_salt,
                    sig.hexdigest(),
                    pg_result_url,
                    cls.__pg_testing_mode,
                )
        )
        return link

    @classmethod
    def result_url(
            cls,
            pg_order_id,
            pg_payment_id,
            pg_salt,
            pg_sig,
            pg_payment_date,
            pg_result,
    ):
        with trs.atomic():
            transaction = cls.__model.objects.filter(id=pg_order_id)
            if not transaction.exists():
                raise ObjectDoesNotExist("Заказ с таким pg_order_id не найден")
            pg_result = "успешно" if int(pg_result) == 1 else "неудачно"
            get_status_data = cls.get_status(
                pg_order_id=pg_order_id,
                pg_payment_id=pg_payment_id,
                pg_salt=pg_salt,
            ).get("response")

            transaction.update(
                pg_result=pg_result,
                payment_id=pg_payment_id,
                currency=get_status_data.get("pg_currency"),
                pg_salt=pg_salt,
                pg_sig=pg_sig,
                pg_card_pan=get_status_data.get("pg_card_pan"),
                amount=get_status_data.get("pg_amount"),
                payment_date=pg_payment_date,
                status=get_status_data.get("pg_status"),
                pg_failure_description=get_status_data.get("pg_failure_description"),
            )
            return transaction

    @classmethod
    def get_status(cls, pg_order_id, pg_payment_id, pg_salt):

        sig = CreateSignature.create_status_sig(
            pg_order_id=pg_order_id,
            pg_payment_id=pg_payment_id,
            pg_salt=pg_salt,
        )

        link = (
                "https://api.paybox.money/get_status2.php?"
                "pg_merchant_id=%s&"
                "pg_payment_id=%s&"
                "pg_order_id=%s&"
                "pg_salt=%s&"
                "pg_sig=%s&"
                % (cls.__merchant_id, pg_payment_id, pg_order_id, pg_salt, sig.hexdigest())
        )
        response = requests.post(link)
        text = xmltodict.parse(response.text)
        res = json.dumps(text)

        return json.loads(res)

    @classmethod
    def answer(cls, pg_status):
        payment_response = (
            {
                "pg_status": "ok",
                "pg_description": "Заказ оплачен",
                "pg_salt": "Спасибо за покупку",
            }
            if pg_status == "успешно"
            else {
                "pg_status": "rejected",
                "pg_description": "Платеж откланен",
                "pg_salt": "Не оплачено",
            }
        )

        pg_sig = CreateSignature.create_answer_sig(
            payment_response["pg_status"],
            payment_response["pg_description"],
            payment_response["pg_salt"],
        )
        data = readfromstring(
            '{"status": "%s", "pg_description": "%s", "pg_salt": "%s", "pg_sig": "%s"}'
            % (
                payment_response["pg_status"],
                payment_response["pg_description"],
                payment_response["pg_salt"],
                pg_sig.hexdigest(),
            )
        )
        response = json2xml.Json2xml(
            data=data, wrapper="response", pretty=True, attr_type=False
        ).to_xml()

        return response

    @classmethod
    def get_payment_detail(cls, offer_id, request):
        offer = cls.__travel_offer.objects.filter(id=offer_id).prefetch_related(
            'order__match_object__object_reviews__user',
        ).select_related(
            'order__match_object__location__placement__parent',
        ).first()
        serialized_data = PaymentDetailSerializer(offer, context={'request': request}).data
        return Response({'data': serialized_data, 'user_id': offer.order.travel_detail.user.id})

    @classmethod
    def get_booked_payment_detail(cls, offer_id, request):
        offer = cls.__travel_offer.objects.filter(id=offer_id).first()
        serialized_data = BookedOfferSerializer(offer, context={'request': request}).data
        return Response(serialized_data)

    @classmethod
    def booking_offer(cls, data):
        offer = cls.__travel_offer.objects.filter(id=data.get('travel_offer'), is_deleted=False).first()
        offer.first_name = data.get('first_name')
        offer.last_name = data.get('last_name')
        offer.email = data.get('email')
        offer.phone_number = data.get('phone_number')
        offer.save()
        return offer


class CreateSignature:
    __pg_testing_mode = 1
    __merchant_id = 553628
    __merchant_secret = 'fm3ari4eHfOjrASK'

    @classmethod
    def create_init_payment_sig(
            cls,
            pg_order_id=None,
            pg_amount=None,
            pg_description=None,
            pg_salt=None,
            pg_result_url=None,
            pg_success_url=None,
            pg_success_url_method=None,
    ) -> str:
        signature = "init_payment.php;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s" % (
            pg_amount,
            pg_description,
            cls.__merchant_id,
            pg_order_id,
            pg_result_url,
            pg_salt,
            pg_success_url,
            pg_success_url_method,
            cls.__pg_testing_mode,
            cls.__merchant_secret,
        )

        sig = hashlib.md5(signature.encode())

        return sig

    @classmethod
    def create_answer_sig(
            cls,
            pg_description=None,
            pg_salt=None,
            pg_status=None,
    ) -> str:
        signature = "init_payment.php;%s;%s;%s" % (
            pg_status,
            pg_description,
            pg_salt,
        )

        sig = hashlib.md5(signature.encode())
        return sig

    @classmethod
    def create_status_sig(
            cls,
            pg_order_id=None,
            pg_payment_id=None,
            pg_salt=None,
    ) -> str:
        signature = "get_status2.php;%s;%s;%s;%s;%s" % (
            cls.__merchant_id,
            pg_order_id,
            pg_payment_id,
            pg_salt,
            cls.__merchant_secret,
        )

        sig = hashlib.md5(signature.encode())
        return sig
