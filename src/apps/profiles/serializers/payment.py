from rest_framework import serializers
from django.db.models import Sum, Count

from apps.houserent.models import LocationObject, Placement, Location
from apps.houserent.serializers import ObjectImageSerializer
from apps.profiles.models.payment import Transaction
from apps.profiles.serializers.base_serializers import BookedPaymentAddressSerializer
from apps.profiles.serializers.user import LocationPaymentSerializer, PaymentDetailBudgetSerializer
from apps.travels.models import TravelOffer, TravelDate


class InitPaymentSerializer(serializers.Serializer):
    amount = serializers.IntegerField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    phone_number = serializers.CharField(required=True)
    travel_offer = serializers.UUIDField(required=True)


class ResultURLSerializers(serializers.Serializer):
    pg_order_id = serializers.CharField(required=True)
    pg_payment_id = serializers.CharField(required=True)
    pg_payment_date = serializers.DateTimeField(required=False)
    pg_result = serializers.IntegerField(required=True)
    pg_salt = serializers.CharField(required=True)
    pg_sig = serializers.CharField(required=True)


class BookedOfferDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TravelDate
        fields = ['start_date', 'end_date']


class LocationAddressSerializer(serializers.ModelSerializer):
    placement = BookedPaymentAddressSerializer()

    class Meta:
        model = Location
        fields = [
            'street',
            'house',
            'placement',
        ]


class BookedOfferSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='order.travel_detail.user.email')
    travel_date = BookedOfferDateSerializer(source='order.travel_detail.date')
    check_in = serializers.TimeField(source='order.match_object.check_in')
    check_out = serializers.TimeField(source='order.match_object.check_out')
    object_images = ObjectImageSerializer(source='order.match_object.image_objects', many=True)
    location_object = LocationPaymentSerializer(source='order.match_object')
    reviews_quantity = serializers.SerializerMethodField()
    general_rating = serializers.SerializerMethodField()
    location_address = LocationAddressSerializer(source='order.match_object.location')
    currency = serializers.CharField(source='order.travel_detail.user.currency')
    user_budget = PaymentDetailBudgetSerializer(source='order.travel_detail.budget')
    guest_quantity = serializers.IntegerField(source='order.travel_detail.guests.guest_quantity')
    facilities_quantity = serializers.IntegerField(source='order.travel_detail.facilities.facilities_quantity')

    class Meta:
        model = TravelOffer
        fields = [
            'email',
            'order_number',
            'travel_date',
            'check_in',
            'check_out',
            'object_images',
            'location_object',
            'reviews_quantity',
            'general_rating',
            'location_address',
            'currency',
            'user_budget',
            'guest_quantity',
            'facilities_quantity',
            'price'
        ]

    def get_reviews_quantity(self, travel_offer):
        return travel_offer.order.match_object.object_reviews.count()

    def get_general_rating(self, travel_offer):
        rating_sum = travel_offer.order.match_object.object_reviews.aggregate(
            total_rating=Sum('general_rating'),
            count=Count('id')
        )
        if rating_sum['count'] > 0:
            return rating_sum['total_rating'] / rating_sum['count']
        return 0
