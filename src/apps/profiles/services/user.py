from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from django.utils.crypto import get_random_string, constant_time_compare
from rest_framework.response import Response
from apps.common.services import Service
from apps.profiles.models.user import User, TemporaryUser, UserResetCode, Currency
from apps.travels.models import TravelOffer, Orders, TravelDetail
from apps.vendors.services import create_temporary_user
from core.settings.base import DEBUG
from apps.profiles.utils.sendCode import send_verification_mail
from apps.profiles.tasks.sendCode import send_verification_code_task
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.contrib.auth.password_validation import validate_password
from google.oauth2 import id_token
from google.auth.transport import requests
from django.contrib.auth.hashers import make_password
import jwt


def change_user_password(request):
    user = request.user
    old_password = request.data.get('old_password')
    new_password = request.data.get('new_password')
    confirm_password = request.data.get('confirm_password')
    if user.check_password(old_password):
        if constant_time_compare(new_password, confirm_password):
            user.password = make_password(confirm_password)
            user.save()
            return 'success'
        return 'Password is not match'
    return 'Password is not correct'


def update_user_profile(request):
    user = request.user
    new_first_name = request.data.get('first_name')
    new_last_name = request.data.get('last_name')
    user.first_name = new_first_name
    user.last_name = new_last_name
    user.save()
    return 'success'


def register(self):
    serializer = self.get_serializer(data=self.request.data)
    user = User.objects.filter(email=self.request.data.get('email')).first()
    if user:
        return None, {'status': 'user is already exist'}
    if serializer.is_valid(raise_exception=True):
        temporary_user_id, user_code = create_temporary_user(
            email=serializer.validated_data['email'],
            first_name=serializer.validated_data['first_name'],
            last_name=serializer.validated_data['last_name'],
            password=serializer.validated_data['password'],
            phone_number=serializer.validated_data['phone_number'],
            temp_user_object=TemporaryUser.objects
        )

        # send_sms_code(serializer.validated_data['phone_number'], vendor_code)
        send_verification_mail(serializer.validated_data['email'], user_code)

        # send_sms_code_from_nikita(serializer.validated_data['phone_number'], vendor_code)

        return temporary_user_id, None


def create_verified_user_type(token, code, user_object, **kwargs):
    temporary_user = TemporaryUser.objects.get(id=token)
    if code != temporary_user.code:
        return None, "Invalid code"
    user = user_object.create_user(
        email=temporary_user.email,
        first_name=temporary_user.first_name,
        last_name=temporary_user.last_name,
        password=temporary_user.password,
        phone_number=temporary_user.phone_number,
    )
    currency, _ = Currency.objects.get_or_create(title="KGS", defaults={'price': 1})
    user.currency = currency
    user.save()
    temporary_user.delete()

    refresh_token = RefreshToken.for_user(user)
    access_token = AccessToken.for_user(user)

    tokens = {
        'refresh': str(refresh_token),
        'access': str(access_token),
    }
    return tokens, None


def authenticate(email, password, user_object):
    try:
        user = user_object.get(email=email)
        if user.check_password(password):
            refresh_token = RefreshToken.for_user(user)
            access_token = AccessToken.for_user(user)
            return {
                'refresh': str(refresh_token),
                'access': str(access_token)
            }, None
        return None, 'Password is not match'
    except ObjectDoesNotExist:
        return None, 'User type does not exist'


def send_reset_code(email, user_object):
    generated_code = get_random_string(5, '0123456789')
    user = user_object.get(email=email)
    user_reset_code = UserResetCode.objects.create(code=generated_code)
    user.reset_code = user_reset_code
    user.save()
    send_verification_mail(email, generated_code)
    return user.id


def check_reset_code(code, token, user_object):
    user = user_object.filter(id=token)

    if code != user[0].reset_code.code:
        return None, "Invalid code"

    user[0].reset_code.delete()
    access = AccessToken.for_user(user[0])
    return {'access': str(access)}, None


def check_user_password(user, new_password, confirm_password):
    if not constant_time_compare(new_password, confirm_password):
        return None, 'passwords are not match',
    try:
        validate_password(confirm_password, user=user)
    except ValidationError as e:
        return None, e
    user.password = make_password(new_password)
    user.save()
    return 'success', None


def send_new_reset_code(verification_token, user_object):
    generated_code = get_random_string(5, '0123456789')
    user = user_object.get(id=verification_token)
    if not user.reset_code:
        reset_code = UserResetCode.objects.create(code=generated_code)
        user.reset_code = reset_code
        user.save()
        if DEBUG:
            send_verification_mail(user.email, generated_code)
        else:
            send_verification_code_task.delay(user.email, generated_code)
        return {"status": 'success'}
    user.reset_code.delete()
    user_reset_code = UserResetCode.objects.create(code=generated_code)
    user.reset_code = user_reset_code
    user.save()
    if DEBUG:
        send_verification_mail(user.email, generated_code)
    else:
        send_verification_code_task.delay(user.email, generated_code)
    return {"status": 'success'}


def send_new_register_code(verification_token, user_object):
    generated_code = get_random_string(5, '0123456789')
    try:
        user = user_object.get(id=verification_token)
        user.code = generated_code
        user.save()
        if DEBUG:
            send_verification_mail(user.email, generated_code)
        else:
            send_verification_code_task.delay(user.email, generated_code)
        return None, {"status": 'success'}
    except ObjectDoesNotExist:
        return None, {"status": 'user is not found'}


def get_or_create_from_google(google_token, objects):
    user_info = id_token.verify_oauth2_token(google_token, requests.Request())

    try:
        user = objects.get(email=user_info['email'])

        access_token = AccessToken.for_user(user)
        refresh_token = RefreshToken.for_user(user)
        return {
            'access': str(access_token),
            'refresh': str(refresh_token),
            'user_created': False
        }
    except ObjectDoesNotExist:
        random_password = get_random_string(length=20)
        user = User.objects.create_user(
            email=user_info['email'],
            first_name=user_info['given_name'],
            last_name=user_info['family_name'],
            password=make_password(random_password)
        )

        access_token = AccessToken.for_user(user)
        refresh_token = RefreshToken.for_user(user)
        return {
            'access': str(access_token),
            'refresh': str(refresh_token),
            'user_created': True
        }


def get_or_create_from_apple(self):
    first_name = self.request.data.get('first_name')
    last_name = self.request.data.get('last_name')
    user_apple_token = self.request.data.get('apple_token')
    decoded = jwt.decode(user_apple_token, options={"verify_signature": False})

    try:
        user = User.objects.get(email=decoded['email'])
        access_token = AccessToken.for_user(user)
        refresh_token = RefreshToken.for_user(user)
        return Response({
            'access': str(access_token),
            'refresh': str(refresh_token)
        })
    except ObjectDoesNotExist:
        random_password = get_random_string(length=12)
        user = User.objects.create_user(
            email=decoded['email'],
            first_name=first_name,
            last_name=last_name,
            password=random_password
        )
        access_token = AccessToken.for_user(user)
        refresh_token = RefreshToken.for_user(user)
        return Response({'access': str(access_token), 'refresh': str(refresh_token)})


class CurrencyService(Service):
    model = Currency


class SearchService(Service):
    offer_model = TravelOffer
    order_model = Orders
    travel_detail_model = TravelDetail

    @classmethod
    def cancel_search(cls, user):
        cls.offer_model.objects.filter(
            order__travel_detail__user=user,
            is_deleted=False,
            is_payed=None,
            is_accepted=None
        ).update(is_deleted=True)
        cls.order_model.objects.filter(
            travel_detail__user=user,
            is_deleted=False,
            approved=None,
            offers__is_payed__isnull=True
        ).update(is_deleted=True)
        cls.travel_detail_model.objects.filter(
            user=user,
            is_deleted=False,
            orders__offers__is_payed__isnull=True
        ).update(is_deleted=True)
        return Response({'status': 'success'})

    @classmethod
    def cancel_offer(cls, offer_id):
        cls.offer_model.objects.filter(id=offer_id, is_deleted=False).update(is_deleted=True, is_accepted=False)
        return Response({'status': 'success'})

    @classmethod
    def accept_offer(cls, offer_id):
        offer = TravelOffer.objects.filter(id=offer_id, is_deleted=False).first()
        offer.is_accepted = True
        offer.save()
        return Response({'status': 'success'})
