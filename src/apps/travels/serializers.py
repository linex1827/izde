from rest_framework import serializers

from apps.travels import models
from apps.houserent import models as houserent_models
from apps.houserent import serializers as houserent_serializer
from apps.profiles.models.user import User, Currency, Vendor


class ObjectKindForOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = houserent_models.ObjectKind
        fields = ['id', 'name', 'icon']


class ObjectTypeForOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = houserent_models.ObjectType
        fields = ['id', 'name', 'icon']


class PlacementForOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = houserent_models.Placement
        fields = [
            'id',
            'name',
            "lft",
            "rght",
            "tree_id",
            "level",
            "parent",
            'icon'
        ]


class CurrencyForOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = [
            'id',
            'title',
            'price'
        ]


class UserForOrderSerializer(serializers.ModelSerializer):
    currency = CurrencyForOrderSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'first_name',
            'last_name',
            'currency'
        ]


class UserForDetailOfferSerializer(serializers.ModelSerializer):
    currency = CurrencyForOrderSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'currency'
        ]


class VendorForOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = [
            'id',
            'first_name',
            'last_name',
            'icon',
            'phone_number'
        ]


class LocationObjectForOrderListSerializer(serializers.ModelSerializer):
    object_type = houserent_serializer.ObjectTypeSerializer(read_only=True)
    object_kind = houserent_serializer.ObjectKindSerializer(read_only=True)
    image_objects = houserent_serializer.ObjectImageSerializer(many=True, read_only=True)
    location = houserent_serializer.LocationDetailSerializer(read_only=True)
    object_prices = houserent_serializer.ObjectPriceSerializer(many=True, read_only=True)
    vendor = VendorForOrderSerializer(read_only=True)
    object_reviews = houserent_serializer.ObjectReviewSerializer(many=True, read_only=True)

    class Meta:
        model = models.LocationObject
        fields = [
            'id',
            'name',
            'vendor',
            'location',
            'object_type',
            'object_kind',
            'image_objects',
            'object_prices',
            'check_in',
            'check_out',
            'currency',
            'object_reviews',
            'cancellation_policy'
        ]


"""Количество гостей"""


class GuestQuantityCreateSerializer(serializers.ModelSerializer):
    guest_quantity = serializers.IntegerField()

    class Meta:
        model = models.GuestQuantity
        fields = [
            'id',
            'guest_quantity',
            'icon'
        ]
        read_only_fields = [
            'id',
            'icon'
        ]


"""Бюджет"""


class TravelBudgetCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TravelBudget
        fields = [
            'id',
            'min_sum',
            'max_sum',
            'icon'
        ]
        read_only_fields = [
            'id',
            'icon'
        ]


"""Количество объектов"""


class FacilitiesQuantityCreateSerializer(serializers.ModelSerializer):
    facilities_quantity = serializers.IntegerField()

    class Meta:
        model = models.FacilitiesQuantity
        fields = [
            'id',
            'facilities_quantity',
            'icon'
        ]
        read_only_fields = [
            'id',
            'icon'
        ]


"""Дата поездки"""


class TravelDateCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TravelDate
        fields = [
            'id',
            'start_date',
            'end_date',
            'icon'
        ]
        read_only_fields = [
            'id',
            'icon'
        ]


class TravelDetailWithEmailSerializer(serializers.ModelSerializer):
    date = TravelDateCreateSerializer(read_only=True)
    budget = TravelBudgetCreateSerializer(read_only=True)
    guests = GuestQuantityCreateSerializer(read_only=True)
    facilities = FacilitiesQuantityCreateSerializer(read_only=True)
    object_type = ObjectTypeForOrderSerializer(read_only=True)
    object_kind = ObjectKindForOrderSerializer(read_only=True)
    placement = PlacementForOrderSerializer(read_only=True)

    commentary = serializers.CharField(max_length=2500, required=False)
    object_type_id = serializers.CharField(required=False)
    user = UserForDetailOfferSerializer(read_only=True)

    class Meta:
        model = models.TravelDetail
        fields = [
            'id',
            'object_type',
            'object_kind',
            'placement',
            'user',
            'date',
            'budget',
            'guests',
            'facilities',
            'object_type_id',
            'object_kind_id',
            'placement_id',
            'commentary',
        ]
        read_only_fields = [
            'id'
        ]


class TravelDetailCreateSerializer(serializers.ModelSerializer):
    date = TravelDateCreateSerializer(read_only=True)
    budget = TravelBudgetCreateSerializer(read_only=True)
    guests = GuestQuantityCreateSerializer(read_only=True)
    facilities = FacilitiesQuantityCreateSerializer(read_only=True)
    object_type = ObjectTypeForOrderSerializer(read_only=True)
    object_kind = ObjectKindForOrderSerializer(read_only=True)
    placement = PlacementForOrderSerializer(read_only=True)

    commentary = serializers.CharField(max_length=2500, required=False)
    object_type_id = serializers.CharField(required=False)
    user = UserForOrderSerializer(read_only=True)

    class Meta:
        model = models.TravelDetail
        fields = [
            'id',
            'object_type',
            'object_kind',
            'placement',
            'user',
            'date',
            'budget',
            'guests',
            'facilities',
            'object_type_id',
            'object_kind_id',
            'placement_id',
            'commentary',
            'created_at'
        ]
        read_only_fields = [
            'id'
        ]


class OrderDetailWithEmailSerializer(serializers.ModelSerializer):
    travel_detail = TravelDetailWithEmailSerializer()
    match_object = LocationObjectForOrderListSerializer()
    expired_in = serializers.DateTimeField(read_only=True)
    matched_price = serializers.IntegerField(read_only=True)
    user_travel_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.Orders
        fields = [
            'id',
            'travel_detail',
            'match_object',
            'approved',
            'expired_in',
            'matched_price',
            'user_travel_count'
        ]
        read_only_fields = [
            'id'
        ]


class TravelOfferWithEmailSerializer(serializers.ModelSerializer):
    order_number = serializers.IntegerField(required=False)
    is_payed = serializers.BooleanField(required=False)
    order = OrderDetailWithEmailSerializer(read_only=True)
    user_travel_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.TravelOffer
        fields = [
            'id',
            'is_payed',
            'order',
            'order_number',
            'comment',
            'price',
            'user_travel_count'
        ]
        read_only_fields = [
            'id',
        ]


class OrderDetailSerializer(serializers.ModelSerializer):
    travel_detail = TravelDetailCreateSerializer()
    match_object = LocationObjectForOrderListSerializer()
    expired_in = serializers.DateTimeField(read_only=True)
    matched_price = serializers.IntegerField(read_only=True)
    user_travel_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.Orders
        fields = [
            'id',
            'travel_detail',
            'match_object',
            'approved',
            'expired_in',
            'matched_price',
            'user_travel_count'
        ]
        read_only_fields = [
            'id'
        ]


class TravelOfferSerializer(serializers.ModelSerializer):
    order_number = serializers.IntegerField(required=False)
    is_payed = serializers.BooleanField(required=False)
    order = OrderDetailSerializer(read_only=True)
    user_travel_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.TravelOffer
        fields = [
            'id',
            'is_payed',
            'order',
            'order_number',
            'comment',
            'price',
            'user_travel_count'
        ]
        read_only_fields = [
            'id',
        ]


class LocationObjectForPastSerializer(serializers.ModelSerializer):
    location = houserent_serializer.LocationNameSerializer(read_only=True)

    class Meta:
        model = houserent_models.LocationObject
        fields = [
            'id',
            'name',
            'location'
        ]


class TravelDetailForPastSerializer(serializers.ModelSerializer):
    date = TravelDateCreateSerializer(read_only=True)

    class Meta:
        model = models.TravelDetail
        fields = [
            'id',
            'date'
        ]


class OrderForPastSerializer(serializers.ModelSerializer):
    travel_detail = TravelDetailForPastSerializer(read_only=True)
    match_object = LocationObjectForPastSerializer(read_only=True)

    class Meta:
        model = models.TravelDetail
        fields = [
            'id',
            'travel_detail',
            'match_object'
        ]


class PastOffersSerializer(serializers.ModelSerializer):
    order = OrderForPastSerializer(read_only=True)

    class Meta:
        model = models.TravelOffer
        fields = [
            'id',
            'order_number',
            'order'
        ]
