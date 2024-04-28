from datetime import timedelta

from django.db import models as db_models
from django.utils.dateparse import parse_date

from apps.common.exceptions import UnifiedErrorResponse
from apps.common.services import Service
from apps.profiles.tasks.broker import send_order, send_offer, deleted_expired_orders, \
    deleted_expired_offers
from apps.travels import models
from apps.profiles.models.user import Currency, User
from apps.profiles.serializers.user import CurrencySerializer
from apps.houserent import models as houserent_models, serializers as houserent_serializers
from rest_framework import response, status

from apps.travels.models import Orders, TravelOffer


class TravelDetailCreateService(Service):
    model = models.TravelDetail
    date_model = models.TravelDate
    budget_model = models.TravelBudget
    guests_model = models.GuestQuantity
    facilities_model = models.FacilitiesQuantity
    order_model = models.Orders
    object_model = houserent_models.LocationObject

    @classmethod
    def get_queryset(cls, *args, **kwargs):
        queryset = (
            cls.model.objects.filter(*args, **kwargs)
            .select_related(
                'placement', 'date', 'budget', 'guests', 'facilities', 'object_type', 'object_kind', 'user__currency')
        )
        return queryset

    @classmethod
    def delete_travel_detail(cls, travel_detail_id):
        try:
            travel_detail = cls.model.objects.get(id=travel_detail_id)
            travel_detail.is_deleted = True
            travel_detail.save()
            return response.Response(
                data={"detail": "Object deleted!"}, status=status.HTTP_204_NO_CONTENT
            )
        except cls.model.DoesNotExist:
            raise UnifiedErrorResponse(
                code=status.HTTP_404_NOT_FOUND, detail="Object not found"
            )

    @classmethod
    def get_user(cls, request, *args, **kwargs):
        return request.user.user

    # @classmethod
    # def create_matching_orders(cls, search, *args, **kwargs):
    #     if search.object_type:
    #         match_object = cls.object_model.objects.filter(
    #             location__placement=search.placement,
    #             object_type=search.object_type,
    #             object_kind=search.object_kind
    #         )
    #     else:
    #         match_object = cls.object_model.objects.filter(
    #             location__placement=search.placement,
    #             object_kind=search.object_kind
    #             )
    #     if match_object:
    #         for i in match_object:
    #             order = cls.order_model.objects.create(match_object=i, travel_detail=search)
    #             send_order.delay(order.id, order.match_object.vendor.email)
    #             deleted_expired_orders.apply_async(
    #                 args=[
    #                     order.id,
    #                     order.match_object.vendor.email,
    #                     'deleted_order_connections',
    #                     'send_deleted_order_id',
    #                 ], countdown=300)

    @classmethod
    def create_matching_orders(cls, travel_detail, *args, **kwargs):
        start_date = travel_detail.date.start_date
        end_date = travel_detail.date.end_date

        matching_objects = cls.object_model.objects.filter(
            location__placement=travel_detail.placement,
            object_kind=travel_detail.object_kind
        )
        print(matching_objects)
        if travel_detail.object_type:
            matching_objects = matching_objects.filter(object_type=travel_detail.object_type)

        available_objects = matching_objects.filter(
            db_models.Q(object_prices__start_date__lte=start_date) |
            db_models.Q(object_prices__end_date__gte=end_date)
        ).distinct()

        print(available_objects)

        for object in available_objects:
            order = cls.order_model.objects.create(
                match_object=object,
                travel_detail=travel_detail
            )
            send_order.delay(order.id, order.match_object.vendor.email)
            deleted_expired_orders.apply_async(
                args=[
                    order.id,
                    order.match_object.vendor.email,
                    'deleted_order_connections',
                    'send_deleted_order_id',
                ], countdown=300)

    @classmethod
    def create_travel_date(cls, validated_data, *args, **kwargs):
        start_date = validated_data.get('start_date')
        end_date = validated_data.get('end_date')
        date, created = cls.date_model.objects.get_or_create(start_date=start_date, end_date=end_date)
        return date

    @classmethod
    def create_travel_budget(cls, validated_data, *args, **kwargs):
        min_sum = validated_data.get('min_sum')
        max_sum = validated_data.get('max_sum')
        budget, created = cls.budget_model.objects.get_or_create(min_sum=min_sum, max_sum=max_sum)
        return budget

    @classmethod
    def create_facilities_quantity(cls, validated_data, *args, **kwargs):
        facilities_quantity = validated_data.get('facilities_quantity')
        facility, created = cls.facilities_model.objects.get_or_create(facilities_quantity=facilities_quantity)
        return facility

    @classmethod
    def create_guest_quantity(cls, validated_data, *args, **kwargs):
        guest_quantity = validated_data.get('guest_quantity')
        guests, created = cls.guests_model.objects.get_or_create(guest_quantity=guest_quantity)
        return guests

    @classmethod
    def create_travel_detail(cls, request, validated_data, *args, **kwargs):
        commentary = validated_data.get('commentary')
        object_type_id = validated_data.get('object_type_id')
        object_kind_id = validated_data.get('object_kind_id')
        placement_id = validated_data.get('placement_id')

        user = cls.get_user(request)
        date = cls.create_travel_date(validated_data)
        budget = cls.create_travel_budget(validated_data)
        guests = cls.create_guest_quantity(validated_data)
        facilities = cls.create_facilities_quantity(validated_data)

        travel_detail = cls.model.objects.create(
            date=date,
            budget=budget,
            guests=guests,
            facilities=facilities,
            commentary=commentary,
            object_type_id=object_type_id,
            object_kind_id=object_kind_id,
            placement_id=placement_id,
            user=user
        )

        cls.create_matching_orders(travel_detail)

        expires_in = travel_detail.created_at + timedelta(minutes=5)

        success = response.Response(
            {
                'Success': 'Travel\'s detail was successfully created',
                'id': travel_detail.id,
                'Expired_time': expires_in
            }, status=status.HTTP_201_CREATED
        )

        return success


class ObjectsTypeAndKindService(Service):
    object_type_model = houserent_models.ObjectType
    object_kind_model = houserent_models.ObjectKind
    currency_model = Currency
    user_model = User

    @classmethod
    def get_querylist(cls, user, *args, **kwargs):
        user = TravelDetailCreateService.get_user(user)
        currency_queryset = cls.currency_model.objects.filter(id=user.currency_id)
        querylist = [
            {
                'queryset': cls.object_type_model.objects.filter(*args, **kwargs),
                'serializer_class': houserent_serializers.ObjectTypeSerializer,
                'label': 'object_type',
            },
            {
                'queryset': cls.object_kind_model.objects.filter(*args, **kwargs),
                'serializer_class': houserent_serializers.ObjectKindSerializer,
                'label': 'object_kind'
            },
            {
                'queryset': currency_queryset,
                'serializer_class': CurrencySerializer,
                'label': 'currency'
            },
        ]
        return querylist


class OrderDetailService(Service):
    model = models.Orders
    price_model = houserent_models.ObjectPrice
    offer_model = models.TravelOffer

    @classmethod
    def make_approved_true(cls, order_id):
        try:
            order = cls.model.objects.get(id=order_id)
            order.approved = True
            order.save()
            return response.Response(
                data={"detail": "Order approved!"}, status=status.HTTP_204_NO_CONTENT
            )
        except cls.model.DoesNotExist:
            raise UnifiedErrorResponse(
                code=status.HTTP_404_NOT_FOUND, detail="Order not found"
            )

    @classmethod
    def delete_order(cls, order_id):
        try:
            order = cls.model.objects.get(id=order_id)
            order.is_deleted = True
            order.approved = False
            order.save()
            return response.Response(
                data={"detail": "Order rejected!"}, status=status.HTTP_204_NO_CONTENT
            )
        except cls.model.DoesNotExist:
            raise UnifiedErrorResponse(
                code=status.HTTP_404_NOT_FOUND, detail="Order not found"
            )

    @classmethod
    def get_travel_count(cls):
        travel_count_subquery = cls.offer_model.objects.filter(
            order__travel_detail__user=db_models.OuterRef('travel_detail__user'),
            is_payed=True,
            is_accepted=True
        ).values('order__travel_detail__user').annotate(
            count=db_models.Count('id')
        ).values('count')
        return travel_count_subquery

    @classmethod
    def get_queryset(cls, *args, **kwargs):
        prices = cls.price_model.objects.filter(
            db_models.Q(start_date__lte=db_models.OuterRef('travel_detail__date__end_date')) |
            db_models.Q(end_date__gte=db_models.OuterRef('travel_detail__date__end_date')),
            object_id=db_models.OuterRef('match_object__id'),
        ).order_by('start_date')

        price_subquery = db_models.Subquery(prices.values('price')[:1])

        queryset = (
            cls.model.objects.filter(*args, **kwargs)
            .select_related(
                'match_object__object_kind',
                'match_object__object_type',
                'travel_detail__placement',
                'travel_detail__user__currency',
                'travel_detail__date',
                'travel_detail__budget',
                'travel_detail__guests',
                'travel_detail__facilities',
                'travel_detail__object_kind',
                'travel_detail__object_type',
                'match_object__location',
                'match_object__vendor',
                'match_object__currency'
            )
            .prefetch_related(
                'match_object__image_objects', 'match_object__object_prices', 'match_object__object_reviews__user'
            )
            .annotate(
                expired_in=db_models.ExpressionWrapper(db_models.F('travel_detail__created_at') + timedelta(minutes=15),
                                                       output_field=db_models.DateTimeField()),
                matched_price=price_subquery,
                user_travel_count=db_models.Subquery(
                    cls.get_travel_count(),
                    output_field=db_models.IntegerField())
            )
        )
        return queryset


class TravelOfferService(Service):
    model = models.TravelOffer
    order_model = models.Orders
    image_model = houserent_models.ObjectImage
    price_model = houserent_models.ObjectPrice
    currency_model = Currency

    @classmethod
    def get_travel_count(cls):
        travel_count_subquery = cls.model.objects.filter(
            order__travel_detail__user=db_models.OuterRef('order__travel_detail__user'),
            is_payed=True,
            is_accepted=True
        ).values('order__travel_detail__user').annotate(
            count=db_models.Count('id')
        ).values('count')
        return travel_count_subquery

    @classmethod
    def filter_past(cls, request, queryset, *args, **kwargs):
        date_past = request.get('date', None)

        if date_past:
            parsed_date = parse_date(date_past)
            return queryset.filter(order__travel_detail__date__end_date__lte=parsed_date)
        return queryset

    @classmethod
    def filter_active(cls, request, queryset, *args, **kwargs):
        date_active = request.get('date', None)

        if date_active:
            parsed_date = parse_date(date_active)
            return queryset.filter(order__travel_detail__date__end_date__gte=parsed_date)
        return queryset

    @classmethod
    def get_queryset(cls, *args, **kwargs):
        queryset = (
            cls.model.objects.filter(*args, **kwargs)
            .select_related(
                'order__match_object__object_kind',
                'order__match_object__object_type',
                'order__travel_detail__placement',
                'order__travel_detail__date',
                'order__travel_detail__budget',
                'order__travel_detail__guests',
                'order__travel_detail__facilities',
                'order__travel_detail__object_kind',
                'order__travel_detail__object_type',
                'order__match_object__location',
                'order__match_object__vendor',
                'order__match_object__currency',
                'order__travel_detail__user__currency'
            )
            .prefetch_related(
                'order__match_object__image_objects',
                'order__match_object__object_prices',
                'order__match_object__object_reviews__user'
            ).annotate(
                user_travel_count=db_models.Subquery(
                    cls.get_travel_count(),
                    output_field=db_models.IntegerField())
            )
        )
        return queryset

    @classmethod
    def create_offer(cls, validated_data, order, *args, **kwargs):
        try:
            order_queryset = Orders.objects.select_related('travel_detail__budget').get(id=order)
        except Orders.DoesNotExist:
            return response.Response(
                {'Error': 'Order not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        max_budget = int(order_queryset.travel_detail.budget.max_sum)
        comment = validated_data.get('commentary')
        price = validated_data.get('price')
        last_order_number = cls.model.objects.aggregate(db_models.Max('order_number'))['order_number__max'] or 0
        order_code = last_order_number + 1

        if int(price) > max_budget:
            return response.Response(
                {'Error': 'Price exceeds the maximum allowed budget.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        offer = cls.model.objects.create(
            comment=comment,
            price=price,
            order_number=order_code,
            order_id=order,
        )
        send_offer.delay(offer.id, offer.order.travel_detail.user.email)

        deleted_expired_offers.apply_async(
            args=[
                offer.id,
                offer.order.match_object.vendor.email,
                'deleted_offers_connections',
                'send_deleted_offers_id',
            ], countdown=300)

        OrderDetailService.make_approved_true(order)

        expires_in = offer.created_at + timedelta(minutes=15)

        success = response.Response(
            {
                'Success': 'Travel\'s detail was successfully created',
                'Expired_time': expires_in
            }, status=status.HTTP_201_CREATED
        )

        return success

    @classmethod
    def delete_offer(cls, offer_id):
        try:
            offer = cls.model.objects.get(id=offer_id)
            offer.is_deleted = True
            offer.is_accepted = False
            offer.save()
            return response.Response(
                data={"detail": "Offer deleted!"}, status=status.HTTP_204_NO_CONTENT
            )
        except cls.model.DoesNotExist:
            raise UnifiedErrorResponse(
                code=status.HTTP_404_NOT_FOUND, detail="Offer not found"
            )
