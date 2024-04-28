from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from apps.profiles.models.user import Vendor, CustomUser
from apps.travels.models import Orders, TravelDetail, TravelBudget, TravelDate, TravelOffer, GuestQuantity, \
    FacilitiesQuantity
from core.settings import base
from . import services
from .services import TwoFactorService
from ..houserent.models import LocationObject, ObjectImage, ObjectKind, ObjectPrice, ObjectType, Placement
from apps.vendors.models import VendorContract, QuestionBlock, Agreement
from ..houserent.serializers import ObjectPriceSerializer
from ..profiles.serializers.payment import BookedOfferDateSerializer


class RegisterVendorSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = Vendor
        fields = [
            'email',
            'first_name',
            'last_name',
            'phone_number',
            'password',
            'confirm_password'
        ]

    def validate_password(self, value):
        request = self.context.get('request')
        temp_vendor = Vendor(
            first_name=request.data.get('first_name'),
            last_name=request.data.get('last_name'),
            email=request.data.get('email'),
        )
        validate_password(value, user=temp_vendor)
        return value

    def validate(self, data):
        if data.get('password') != data.get('confirm_password'):
            raise ValidationError({'password': 'password did not match'})
        return data


class TwoFactorSetupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = '__all__'


class TwoFACodeSerializer(serializers.Serializer):
    code = serializers.IntegerField()


class TwoFactorLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    code = serializers.IntegerField()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name']


class TravelBudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = TravelBudget
        fields = ['min_sum', 'max_sum', 'icon', ]


class ImageObjectSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = ObjectImage
        fields = ['image']

    def get_image(self, image):
        return f"{base.BASE_URL}{image.image.url}"


class ObjectOrderKindSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObjectKind
        fields = ['name']


class ObjectOrderPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObjectPrice
        fields = ['price']


class LocationObjectSerializer(serializers.ModelSerializer):
    image_objects = ImageObjectSerializer(many=True)
    object_kind = ObjectOrderKindSerializer()

    class Meta:
        model = LocationObject
        fields = ['image_objects', 'name', 'object_kind']


class TravelDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TravelDate
        fields = ['start_date', 'end_date']


class TravelDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    budget = TravelBudgetSerializer()
    date = TravelDateSerializer()

    class Meta:
        model = TravelDetail
        fields = ['commentary', 'user', 'budget', 'date']


class SuggestedOfferPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = TravelOffer
        fields = ['price', 'order_number']


class OrderSerializer(serializers.ModelSerializer):
    travel_detail = TravelDetailSerializer(read_only=True)
    match_object = LocationObjectSerializer(read_only=True)
    matched_price = serializers.IntegerField(allow_null=True)
    suggested_price = SuggestedOfferPriceSerializer(source='offers', many=True)

    class Meta:
        model = Orders
        fields = ['id', 'travel_detail', 'match_object', 'created_at', 'matched_price', 'suggested_price']


class CurrentOccupancyLocationObjectSerializer(serializers.ModelSerializer):
    location_name = serializers.CharField(source='location.name')
    location_object_name = serializers.CharField(source='name')

    class Meta:
        model = LocationObject
        fields = [
            'location_object_name',
            'location_name',
        ]


class CurrentDetailOrderNumberPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = TravelOffer
        fields = ['order_number']


class CurrentOccupancySerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='travel_detail.user.first_name')
    last_name = serializers.CharField(source='travel_detail.user.last_name')
    travel_quantity = serializers.IntegerField()
    travel_date = BookedOfferDateSerializer(source='travel_detail.date')
    object_quantity = serializers.IntegerField(source='travel_detail.facilities.facilities_quantity')
    image_objects = serializers.ImageField(source='match_object.image_objects')
    location_name = serializers.CharField(source='match_object.location.name')
    location_object_name = serializers.CharField(source='match_object.name')
    suggested_price = SuggestedOfferPriceSerializer(source='offers', many=True)

    class Meta:
        model = Orders
        fields = [
            'id',
            'user_name',
            'last_name',
            'travel_quantity',
            'travel_date',
            'object_quantity',
            'image_objects',
            'location_name',
            'location_object_name',
            'suggested_price'
        ]


class DetailCurrentOccupancyObjectSerializer(serializers.ModelSerializer):
    image_objects = ImageObjectSerializer(many=True)
    location_object_name = serializers.CharField(source='name')
    location_name = serializers.CharField(source='location.name')
    kind_object = serializers.CharField(source='object_kind.name')
    type_object = serializers.CharField(source='object_type.name')
    location_address = serializers.CharField(source='location.placement.name')

    class Meta:
        model = LocationObject
        fields = [
            'image_objects',
            'location_object_name',
            'location_name',
            'kind_object',
            'type_object',
            'object_prices',
            'partnership',
            'location_address',
        ]


class DetailCurrentDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TravelDate
        fields = [
            'start_date',
            'end_date',
            'icon',
        ]


class DetailCurrentGuestQuantitySerializer(serializers.ModelSerializer):
    class Meta:
        model = GuestQuantity
        fields = [
            'guest_quantity',
            'icon',
        ]


class DetailCurrentFacilitiesQuantitySerializer(serializers.ModelSerializer):
    class Meta:
        model = FacilitiesQuantity
        fields = [
            'facilities_quantity',
            'icon',
        ]


class DetailCurrentObjectTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObjectType
        fields = [
            'name',
            'icon',
        ]


class DetailCurrentObjectKindSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObjectKind
        fields = [
            'name',
            'icon',
        ]


class OrderInfoSerializer(serializers.ModelSerializer):
    date = DetailCurrentDateSerializer()
    budget = TravelBudgetSerializer()
    guests = DetailCurrentGuestQuantitySerializer()
    facilities = DetailCurrentFacilitiesQuantitySerializer()
    object_type = DetailCurrentObjectTypeSerializer()
    object_kind = DetailCurrentObjectKindSerializer()

    class Meta:
        model = TravelDetail
        fields = [
            'date',
            'budget',
            'guests',
            'facilities',
            'object_type',
            'object_kind',
        ]


class DetailCurrentOccupancySerializer(serializers.ModelSerializer):
    currency = serializers.CharField(source='travel_detail.user.currency')
    location_object = DetailCurrentOccupancyObjectSerializer(source='match_object')
    matched_price = serializers.IntegerField()
    user_name = serializers.CharField(source='travel_detail.user.first_name')
    last_name = serializers.CharField(source='travel_detail.user.last_name')
    travel_quantity = serializers.IntegerField()
    order_data = OrderInfoSerializer(source='travel_detail')
    suggested_price = SuggestedOfferPriceSerializer(source='offers', many=True)

    class Meta:
        model = Orders
        fields = [
            'currency',
            'location_object',
            'matched_price',
            'user_name',
            'last_name',
            'travel_quantity',
            'order_data',
            'suggested_price',
        ]


'''AGREEMENT SERIALIZERS'''


class AgreementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agreement
        fields = [
            "id",
            "title",
            "description",
        ]


class VendorContractSerializer(serializers.ModelSerializer):
    agreement = AgreementSerializer(many=True, read_only=True)
    vendor = serializers.PrimaryKeyRelatedField(read_only=True)
    uploaded_agreement = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True
    )

    class Meta:
        model = VendorContract
        fields = [
            "id",
            "vendor",
            "agreement",
            "uploaded_agreement"
        ]

    def create(self, validated_data):
        return services.VendorContractService.create_contract(
            vendor=self.context["request"].user.id,
            validated_data=validated_data
        )


class QuestionBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionBlock
        fields = [
            "id",
            "title",
            "description"
        ]


class VendorDetailSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(read_only=True)
    email = serializers.CharField(read_only=True)
    location_object_count = serializers.IntegerField(read_only=True)
    paid_offers_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Vendor
        fields = [
            "id",
            "icon",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "twofa",
            "location_object_count",
            "paid_offers_count"
        ]


class PhoneChangeSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)


class PhoneCodeSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=5)
    phone_number = serializers.CharField(max_length=15)


class EmailChangeSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255, required=True, write_only=True)


class EmailCodeSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=5, required=True, write_only=True)
    email = serializers.EmailField(max_length=255, required=True, write_only=True)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password1 = serializers.CharField(required=True)
    new_password2 = serializers.CharField(required=True)

    def validate_new_password1(self, value):
        validate_password(value, self.context['request'].user)
        return value

    def validate(self, data):
        if data['new_password1'] != data['new_password2']:
            raise serializers.ValidationError({'new_password2': 'Новые пароли не совпадают.'})
        return data
