from datetime import timedelta
import pyotp
from argon2 import exceptions

from django.db.models import OuterRef, Subquery, IntegerField
from django.db.models import Count, Q
from django.db import models

from django.utils import timezone
from django.utils.crypto import get_random_string
from django.contrib.auth.hashers import make_password
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from django.core.exceptions import ObjectDoesNotExist

from apps.common.exceptions import UnifiedErrorResponse
from apps.common.services import Service
from apps.houserent.models import ObjectPrice
from apps.profiles.models.user import Vendor, UserResetCode
from apps.profiles.utils.sendCode import send_verification_mail
from apps.travels.models import Orders, TravelOffer
from apps.vendors.models import Agreement, QuestionBlock, VendorContract


def generate_verification_code(length=5):
    return get_random_string(length, '0123456789')


def create_temporary_user(email, password, temp_user_object, **extra_fields):
    generated_code = generate_verification_code()
    user_type = temp_user_object.create_user(
        email=email,
        password=make_password(password),
        code=generated_code,
        **extra_fields,
    )

    return user_type.id, generated_code


class TwoFactorService(Service):
    model = Vendor

    @staticmethod
    def twofactor_setup(user_object):
        if user_object.secret_key is None:
            key = pyotp.random_base32()
            user_object.secret_key = key
            user_object.save()
            return key
        return user_object.secret_key

    @classmethod
    def twofactor_verify(cls, code, email):
        try:
            user_object = cls.model.objects.get(email=email)
            totp = pyotp.TOTP(user_object.secret_key)
            if totp.verify(code):
                if user_object.twofa:
                    user_object.twofa = False
                    user_object.save()
                    return False
                user_object.twofa = True
                user_object.save()
                return True
            return None
        except ObjectDoesNotExist:
            return None, 'User type does not exist'

    @classmethod
    def twofactor_login(cls, code, email, password):
        try:
            user = cls.model.objects.get(email=email)
            totp = pyotp.TOTP(user.secret_key)
            if totp.verify(code):
                if user.check_password(password):
                    refresh_token = RefreshToken.for_user(user)
                    access_token = AccessToken.for_user(user)
                return {
                    'refresh': str(refresh_token),
                    'access': str(access_token)
                }, None
            return None, 'Wrong code'
        except ObjectDoesNotExist:
            return None, 'User type does not exist'
        except exceptions.VerificationError:
            return None, 'Password is not match'


class OrderListService(Service):
    model = Orders
    offer_model = TravelOffer
    price_model = ObjectPrice


    @classmethod
    def get_vendor_orders(cls, vendor):
        prices = ObjectPrice.objects.filter(
            object_id=OuterRef('match_object__id'),
            start_date__lte=OuterRef('travel_detail__date__end_date'),
            end_date__gte=OuterRef('travel_detail__date__end_date')
        ).order_by('start_date')

        price_subquery = Subquery(prices.values('price')[:1])

        orders = cls.model.objects.filter(
            is_deleted=False,
            match_object__vendor=vendor,
            approved=None,
        ).annotate(
            matched_price=price_subquery
        )
        return orders

    @classmethod
    def approved_vendor_orders(cls, vendor):
        orders = cls.model.objects.filter(
            is_deleted=False,
            match_object__vendor=vendor,
            approved=True,
            offers__is_payed=None,
        )
        return orders

    @classmethod
    def get_current_occupancy(cls, vendor):
        paid_offers_subquery = cls.offer_model.objects.filter(
            is_deleted=False,
            is_payed=True,
            order__travel_detail__user=OuterRef('travel_detail__user')
        ).values('order__travel_detail__user').annotate(total_count=Count('id')).values('total_count')
        paid_offers_count = Subquery(paid_offers_subquery[:1], output_field=IntegerField())

        orders = cls.model.objects.filter(
            offers__is_payed=True,
            is_deleted=False,
            match_object__vendor=vendor
        ).annotate(
            travel_quantity=paid_offers_count
        )
        return orders

    @classmethod
    def detail_current_occupancy(cls, order_id, vendor):

        prices = cls.price_model.objects.filter(
            models.Q(start_date__lte=models.OuterRef('travel_detail__date__end_date')) |
            models.Q(end_date__gte=models.OuterRef('travel_detail__date__end_date')),
            object_id=models.OuterRef('match_object__id'),
        ).order_by('start_date')

        price_subquery = models.Subquery(prices.values('price')[:1])

        paid_offers_subquery = cls.offer_model.objects.filter(
            is_deleted=False,
            is_payed=True,
            order__travel_detail__user=OuterRef('travel_detail__user')
        ).values('order__travel_detail__user').annotate(total_count=Count('id')).values('total_count')
        paid_offers_count = Subquery(paid_offers_subquery[:1], output_field=IntegerField())

        order = cls.model.objects.filter(
            id=order_id,
            offers__is_payed=True,
            is_deleted=False,
            match_object__vendor=vendor
        ).annotate(
            travel_quantity=paid_offers_count,
            matched_price=price_subquery
        ).first()
        print(order)
        return order


class AgreementService(Service):
    model = Agreement


class QuestionBlockService(Service):
    model = QuestionBlock


class VendorContractService(Service):
    model = VendorContract
    agreement_model = Agreement

    @classmethod
    def create_contract(cls, vendor, validated_data):
        agreement_data = validated_data.pop("uploaded_agreement")
        contract_model = cls.model.objects.create(**validated_data, vendor_id=vendor)
        if agreement_data:
            agreement_objects = cls.agreement_model.objects.filter(id__in=agreement_data)
            contract_model.agreement.set(agreement_objects)

        return contract_model


class VendorService(Service):
    model = Vendor
    code_model = UserResetCode

    @classmethod
    def get_queryset(cls, *args, **kwargs):
        queryset = (cls.model.objects
        .filter(*args, **kwargs)
        .annotate(
            location_object_count=Count('vendors', distinct=True),
            paid_offers_count=Count(
                'vendors__orders__offers',
                filter=Q(vendors__orders__offers__is_payed=True),
                distinct=True
            ))
        )
        return queryset

    @classmethod
    def send_change_phone_code(cls, vendor_id, phone_number):
        generated_code = get_random_string(5, '0123456789')
        vendor = cls.get_or_none(id=vendor_id)
        vendor_reset_code = cls.code_model.objects.create(code=generated_code)
        vendor.reset_code = vendor_reset_code
        vendor.save()
        # send_sms_code_from_nikita(phone_number=phone_number,
        #                           vendor_code=generated_code)

    @classmethod
    def check_change_phone_code(cls, code, vendor_id, phone_number):
        vendor = cls.get_or_none(id=vendor_id)
        cls.check_time(code_date=vendor.reset_code.created_at,
                       expiration_time=timedelta(minutes=3))
        cls.check_code(received_code=vendor.reset_code.code, sent_code=code)
        vendor.phone_number = phone_number
        vendor.save()
        vendor.reset_code.delete()
        return vendor

    @classmethod
    def resend_change_phone_code(cls, vendor_id, phone_number):
        generated_code = get_random_string(5, '0123456789')
        vendor = cls.get_or_none(id=vendor_id)
        if hasattr(vendor, 'reset_code') and vendor.reset_code:
            vendor.reset_code.delete()

        code = cls.code_model.objects.create(
            code=generated_code
        )
        vendor.reset_code = code
        vendor.save()
        # send_sms_code_from_nikita(phone_number=phone_number,
        #                           vendor_code=generated_code)

    @classmethod
    def send_change_email_code(cls, vendor_id, email):
        generated_code = get_random_string(5, '0123456789')
        vendor = cls.get_or_none(id=vendor_id)
        vendor_reset_code = cls.code_model.objects.create(code=generated_code)
        vendor.reset_code = vendor_reset_code
        vendor.save()
        send_verification_mail(email=email, generated_code=generated_code)

    @staticmethod
    def check_code(received_code, sent_code):
        if sent_code != received_code:
            raise UnifiedErrorResponse(detail="Invalid code!",
                                       code=status.HTTP_403_FORBIDDEN)

    @staticmethod
    def check_time(code_date, expiration_time: timedelta):
        time_elapsed = timezone.now() - code_date
        if time_elapsed > expiration_time:
            raise UnifiedErrorResponse(detail="Reset code has expired. Please request a new one",
                                       code=status.HTTP_408_REQUEST_TIMEOUT)

    @classmethod
    def check_change_email_code(cls, vendor_id, code, email):
        vendor = cls.get_or_none(id=vendor_id)
        cls.check_time(code_date=vendor.reset_code.created_at,
                       expiration_time=timedelta(minutes=3))
        cls.check_code(received_code=vendor.reset_code.code, sent_code=code)
        vendor.email = email
        vendor.save()
        vendor.reset_code.delete()
        return vendor

    @classmethod
    def resend_change_email_code(cls, vendor_id, email):
        generated_code = get_random_string(5, '0123456789')
        vendor = cls.get_or_none(id=vendor_id)
        if hasattr(vendor, 'reset_code') and vendor.reset_code:
            vendor.reset_code.delete()

        code = cls.code_model.objects.create(
            code=generated_code
        )
        vendor.reset_code = code
        vendor.save()
        send_verification_mail(email=email, generated_code=generated_code)

    @classmethod
    def change_password(cls, vendor, new_password, old_password):

        if not vendor.check_password(old_password):
            raise UnifiedErrorResponse(detail={'old_password': 'Неверный старый пароль.'}, 
                                       code=status.HTTP_400_BAD_REQUEST)
        vendor.set_password(new_password)
        vendor.save()
