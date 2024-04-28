from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db.models import Sum, Count

from apps.houserent import models
from apps.houserent.models import LocationObject, Location, LocationImage
from apps.houserent.serializers import LocationObjectListSerializer, ObjectTypeSerializer, ObjectKindSerializer, \
    ObjectImageSerializer, LocationNameSerializer, ObjectPriceSerializer, ObjectFacilitySerializer, \
    LocationFacilitySerializer
from apps.houserent.services import ObjectCheckService, ObjectReviewService
from apps.profiles.models.user import User, Currency, Vendor
from apps.profiles.serializers.base_serializers import BookedPaymentAddressSerializer
from apps.reviews.models import ObjectReview
from apps.travels.models import TravelOffer, Orders, TravelDetail, TravelDate, TravelBudget
from apps.travels.serializers import TravelDateCreateSerializer, UserForOrderSerializer
from core.settings import base


class ProfileUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'phone_number'
        ]


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=100)
    new_password = serializers.CharField(max_length=100)
    confirm_password = serializers.CharField(max_length=100)


class UpdateUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']


class RegisterUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'email',
            'first_name',
            'last_name',
            'password',
            'confirm_password',
        ]

    def validate_password(self, value):
        request = self.context.get('request')
        temp_user = User(
            first_name=request.data.get('first_name'),
            last_name=request.data.get('last_name'),
            email=request.data.get('email'),
        )
        validate_password(value, user=temp_user)
        return value

    def validate(self, data):
        if data.get('password') != data.get('confirm_password'):
            raise ValidationError({'password': 'password did not match'})
        return data


class VerifyUserSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=100)
    code = serializers.CharField(max_length=100)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=255)


class SendResetCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ChangeUserPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(max_length=100)
    confirm_password = serializers.CharField(max_length=100)


class CheckVerifyTokenSerializer(serializers.Serializer):
    verification_token = serializers.CharField(max_length=250)


class GoogleOAuthSerializer(serializers.Serializer):
    google_token = serializers.CharField(max_length=1000)

    class Meta:
        fields = ['google_token']


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = [
            "id",
            "title",
            "price"
        ]


class TravelUserDetailSerializer(serializers.ModelSerializer):
    date = TravelDateCreateSerializer(read_only=True)
    user = UserForOrderSerializer(read_only=True)

    class Meta:
        model = TravelDetail
        fields = ['date', 'user']


class OfferObjectImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = models.ObjectImage
        fields = ["id", "image"]

    def get_image(self, image):
        return f"{base.BASE_URL}{image.image.url}"


class OfferLocationObjectListSerializer(serializers.ModelSerializer):
    object_type = ObjectTypeSerializer(read_only=True)
    object_kind = ObjectKindSerializer(read_only=True)
    image_objects = OfferObjectImageSerializer(many=True, read_only=True)
    location = LocationNameSerializer(read_only=True)
    object_prices = ObjectPriceSerializer(many=True, read_only=True)

    class Meta:
        model = LocationObject
        fields = [
            "id",
            "name",
            "location",
            "object_type",
            "object_kind",
            "image_objects",
            "object_prices",
        ]


class OrderSerializer(serializers.ModelSerializer):
    travel_detail = TravelUserDetailSerializer()
    match_object = OfferLocationObjectListSerializer()

    class Meta:
        model = Orders
        fields = [
            'match_object',
            'travel_detail',
        ]


class OfferSerializer(serializers.ModelSerializer):
    order = OrderSerializer(read_only=True)

    class Meta:
        model = TravelOffer
        fields = [
            'id',
            'order',
            'price',
            'comment',
            'created_at',
        ]


class CancelOfferSerializer(serializers.Serializer):
    offer_id = serializers.CharField(max_length=255)


class LocationPaymentSerializer(serializers.ModelSerializer):
    location_name = serializers.CharField(source='location.name')
    location_object_name = serializers.CharField(source='name')
    vendor_first_name = serializers.CharField(source='vendor.first_name')
    vendor_last_name = serializers.CharField(source='vendor.last_name')
    vendor_icon = serializers.CharField(source='vendor.icon')

    class Meta:
        model = LocationObject
        fields = [
            'location_object_name',
            'location_name',
            'vendor_first_name',
            'vendor_last_name',
            'vendor_icon',
        ]


class PaymentDetailTravelDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TravelDate
        fields = ['start_date', 'end_date']


class PaymentDetailBudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = TravelBudget
        fields = ['min_sum', 'max_sum']


class PaymentDetailLocationImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocationImage
        fields = ['id','image']


class CommentAuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name']


class ObjectReviewsSerializer(serializers.ModelSerializer):
    user = CommentAuthorSerializer()

    class Meta:
        model = ObjectReview
        fields = [
            'user',
            'created_at',
            'comment',
        ]


class PaymentDetailSerializer(serializers.ModelSerializer):
    location_images = PaymentDetailLocationImageSerializer(source='order.match_object.location.image_locations', many=True)
    location_object = LocationPaymentSerializer(source='order.match_object')
    travel_date = PaymentDetailTravelDateSerializer(source='order.travel_detail.date')
    user_budget = PaymentDetailBudgetSerializer(source='order.travel_detail.budget')
    guest_quantity = serializers.IntegerField(source='order.travel_detail.guests.guest_quantity')
    facilities_quantity = serializers.IntegerField(source='order.travel_detail.facilities.facilities_quantity')
    currency = serializers.CharField(source='order.travel_detail.user.currency.title')
    object_description = serializers.CharField(source='order.match_object.description')
    object_type = serializers.CharField(source='order.match_object.object_type')
    object_kind = serializers.CharField(source='order.match_object.object_kind')
    room_quantity = serializers.CharField(source='order.match_object.room_quantity')
    occupancy = serializers.CharField(source='order.match_object.occupancy')
    house = serializers.CharField(source='order.match_object.location.house')
    street = serializers.CharField(source='order.match_object.location.street')
    address_link = serializers.URLField(source='order.match_object.location.address_link')
    placement = BookedPaymentAddressSerializer(source='order.match_object.location.placement')
    image_objects = OfferObjectImageSerializer(source='order.match_object.image_objects', many=True)
    reviews_quantity = serializers.SerializerMethodField()
    avg_reviews = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()
    check_in = serializers.TimeField(source='order.match_object.check_in')
    check_out = serializers.TimeField(source='order.match_object.check_out')
    object_rules = serializers.CharField(source='order.match_object.rules')
    location_rules = serializers.CharField(source='order.match_object.location.rules')
    object_amenities = serializers.SerializerMethodField()
    location_amenities = serializers.SerializerMethodField()
    cancellation_policy = serializers.CharField(source='order.match_object.cancellation_policy')
    full_refund_cutoff_hours = serializers.IntegerField(source='order.match_object.full_refund_cutoff_hours')
    partial_refund_cutoff_hours = serializers.IntegerField(source='order.match_object.partial_refund_cutoff_hours')

    class Meta:
        model = TravelOffer
        fields = [
            'location_images',
            'location_object',
            'travel_date',
            'user_budget',
            'guest_quantity',
            'facilities_quantity',
            'price',
            'currency',
            'object_description',
            'object_type',
            'object_kind',
            'room_quantity',
            'occupancy',
            'house',
            'street',
            'address_link',
            'placement',
            'image_objects',
            'reviews_quantity',
            'avg_reviews',
            'reviews',
            'check_in',
            'check_out',
            'object_rules',
            'location_rules',
            'object_amenities',
            'location_amenities',
            'cancellation_policy',
            'full_refund_cutoff_hours',
            'partial_refund_cutoff_hours',
        ]

    def get_location_amenities(self, offer):
        location_amenities = offer.order.match_object.location.facility.all()
        serialized_data = LocationFacilitySerializer(location_amenities, many=True).data
        return serialized_data

    def get_object_amenities(self, offer):
        object_amenities = offer.order.match_object.facility.all()
        serialized_data = ObjectFacilitySerializer(object_amenities, many=True).data
        return serialized_data

    def get_reviews(self, offer):
        reviews = offer.order.match_object.object_reviews.all()[:10]
        serialized_data = ObjectReviewsSerializer(reviews, many=True).data
        return serialized_data

    def get_reviews_quantity(self, travel_offer):
        return travel_offer.order.match_object.object_reviews.count()

    def get_avg_reviews(self, offer):
        return ObjectReviewService.get_avg_reviews(offer.order.match_object)


class AppleOAuthSerializer(serializers.Serializer):
    apple_token = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
