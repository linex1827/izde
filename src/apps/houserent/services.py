import datetime
from apps.common.services import Service
from apps.common.mixins import SearchByNameMixin
from apps.common.exceptions import UnifiedErrorResponse
from apps.houserent import models
from apps.reviews import models as review_models
from apps.travels import models as travel_models
from apps.profiles.models import user as user_models

from django.db.models import (
    Prefetch,
    Q,
    Case,
    When,
    Value,
    IntegerField,
    Count,
    Exists,
    OuterRef,
    Sum,
    F,
    Subquery, Avg,
)
from django.db.models.functions import Extract, Coalesce, TruncDay
from django.utils import timezone
from rest_framework import status, response


class PlacementService(Service, SearchByNameMixin):
    model = models.Placement

    @classmethod
    def get_queryset(cls, request, *args, **kwargs):
        queryset = (
            cls.model.objects.filter(Q(name__icontains="город") | Q(level=2))
            .select_related("parent")
            .distinct()
        )
        name = request.query_params.get("name", None)
        if name is not None:
            queryset = queryset.filter(name__icontains=name)
        return queryset


class LocationService(Service):
    model = models.Location

    @classmethod
    def get_queryset(cls, *args, **kwargs):
        queryset = (
            cls.model.objects.filter(*args, **kwargs)
            .select_related("placement")
            .prefetch_related("facility")
            .annotate(
                objects_count=Count("object_locations", distinct=True),
            )
        )
        return queryset


class LocationFacilityService(Service, SearchByNameMixin):
    model = models.LocationFacility


class ObjectFacilityService(Service, SearchByNameMixin):
    model = models.ObjectFacility


class ObjectPriceService(Service):
    model = models.ObjectPrice


class ObjectTypeService(Service):
    model = models.ObjectType


class ObjectKindService(Service):
    model = models.ObjectKind


class LocationObjectService(Service):
    model = models.LocationObject
    vendor_model = user_models.Vendor
    location_model = models.Location
    location_facility_model = models.LocationFacility
    image_model = models.ObjectImage
    price_model = models.ObjectPrice
    facility_model = models.ObjectFacility
    check_model = models.ObjectCheck
    review_model = review_models.ObjectReview
    order_model = travel_models.Orders
    offer_model = travel_models.TravelOffer

    @classmethod
    def delete_prices_from_objects(cls, object_price_id):
        price_object = cls.get_or_error(cls.price_model, object_price_id)
        price_object.is_deleted = True
        price_object.save()
        return response.Response(
            data={"detail": "Object deleted!"}, status=status.HTTP_204_NO_CONTENT
        )

    @classmethod
    def delete_objects_from_locations(cls, location_object_id):
        location_object = cls.get_or_error(cls.location_model, location_object_id)
        location_object.is_deleted = True
        location_object.save()
        return response.Response(
            data={"detail": "Object deleted!"}, status=status.HTTP_204_NO_CONTENT
        )

    @classmethod
    def parse_date(cls, date_str):
        if date_str:
            date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
            return date, date.month, date.day
        else:
            date = timezone.now().date()
            return date, date.month, date.day

    # post

    @classmethod
    def create_object(cls, validated_data, vendor, *args, **kwargs):
        images_data = validated_data.pop("uploaded_images")
        facilities_data = validated_data.pop("uploaded_facilities")
        prices_data = validated_data.pop("uploaded_prices")
        location_object = cls.model.objects.create(**validated_data, vendor_id=vendor)
        if facilities_data:
            facility_objects = cls.facility_model.objects.filter(id__in=facilities_data)
            location_object.facility.set(facility_objects)

        price_to_create = [
            cls.price_model(
                start_date=price["start_date"],
                end_date=price["end_date"],
                price=price["price"],
                object=location_object,
            )
            for price in prices_data
        ]
        cls.price_model.objects.bulk_create(price_to_create)
        images_to_create = [
            cls.image_model(object=location_object, image=img) for img in images_data
        ]
        cls.image_model.objects.bulk_create(images_to_create)
        cls.check_model.objects.create(
            object=location_object, choice="created", is_checked=False
        )
        return location_object

    # get
    @classmethod
    def get_queryset_for_location(cls, request, *args, **kwargs):
        prefetches = cls.get_prefetches()
        date, date_month, date_day = cls.parse_date(
            request.query_params.get("date", None)
        )
        unchecked_exists = Exists(
            cls.check_model.objects.filter(object_id=OuterRef("pk"), is_checked=False)
        )
        price_subquery = (
            cls.price_model.objects.filter(
                object_id=OuterRef("pk"),
                start_date__month=date_month,
                start_date__day__lte=date_day,
                end_date__month=date_month,
                end_date__day__gte=date_day,
            )
            .order_by("start_date")
            .values("price")[:1]
        )

        queryset = (
            cls.model.objects.filter(*args, **kwargs)
            .select_related("object_type", "object_kind")
            .prefetch_related("location", prefetches["objects_images_prefetch"])
            .annotate(
                current_price=Subquery(price_subquery, output_field=IntegerField()),
                is_checked=~unchecked_exists,
                objects_count=Count("location__object_locations", distinct=True),
            )
        )
        return queryset

    @classmethod
    def get_prefetches(cls):
        return {
            "objects_images_prefetch": Prefetch(
                "image_objects", queryset=cls.image_model.objects.all()
            ),
            "objects_prices_prefetch": Prefetch(
                "object_prices", queryset=cls.price_model.objects.all()
            ),
            "reviews_prefetch": Prefetch(
                "object_reviews", queryset=cls.review_model.objects.all()
            ),
        }

    @classmethod
    def get_start_of_month(cls):
        now = timezone.now()
        return datetime.datetime(now.year, now.month, 1)

    @classmethod
    def get_total_clients_subquery(cls, match_field, date_filter=None):
        queryset = cls.order_model.objects.filter(match_object_id=OuterRef(match_field))
        if date_filter:
            queryset = queryset.filter(created_at__gte=date_filter)
        return Subquery(
            queryset.annotate(
                total=Count("offers", filter=Q(offers__is_payed=True), distinct=True)
            ).values("total")[:1]
        )

    @classmethod
    def get_total_revenue_subquery(cls, match_field, date_filter=None):
        queryset = cls.order_model.objects.filter(match_object_id=OuterRef(match_field))
        if date_filter:
            queryset = queryset.filter(created_at__gte=date_filter)
        return Subquery(
            queryset.annotate(
                total=Sum("offers__price", filter=Q(offers__is_payed=True))
            ).values("total")[:1]
        )

    @classmethod
    def get_queryset_for_list(cls, request, *args, **kwargs):
        prefetches = cls.get_prefetches()
        unchecked_exists = Exists(
            cls.check_model.objects.filter(object_id=OuterRef("pk"), is_checked=False)
        )

        queryset = (
            cls.model.objects.filter(*args, **kwargs)
            .prefetch_related(
                prefetches["objects_images_prefetch"],
                "location__facility",
                "facility",
            )
            .annotate(
                objects_count=Count("vendor__vendors", distinct=True),
                is_checked=~unchecked_exists,
            )
            .filter(vendor_id=request.user.vendor.id)
            .select_related("location__placement", "object_kind", "object_type")
        )
        return queryset

    @classmethod
    def get_queryset_for_detail(cls, *args, **kwargs):
        prefetches = cls.get_prefetches()
        start_of_month = cls.get_start_of_month()
        unchecked_exists = Exists(
            cls.check_model.objects.filter(object_id=OuterRef("pk"), is_checked=False)
        )

        queryset = (
            cls.model.objects.filter(*args, **kwargs)
            .prefetch_related(
                prefetches["objects_images_prefetch"],
                prefetches["objects_prices_prefetch"],
                prefetches["reviews_prefetch"],
                "location__facility",
                "facility",
            )
            .annotate(
                objects_count=Count("vendor__vendors", distinct=True),
                is_checked=~unchecked_exists,
                reviews_count=Count("object_reviews", distinct=True),
                total_clients_all_time=Coalesce(
                    cls.get_total_clients_subquery("pk"), 0
                ),
                total_clients_current_month=Coalesce(
                    cls.get_total_clients_subquery("pk", start_of_month), 0
                ),
                total_revenue_all_time=Coalesce(
                    cls.get_total_revenue_subquery("pk"), 0
                ),
                total_revenue_current_month=Coalesce(
                    cls.get_total_revenue_subquery("pk", start_of_month), 0
                ),
            )
            .select_related(
                "location__placement", "object_kind", "object_type", "vendor"
            )
        )
        return queryset

    # update

    @classmethod
    def update_object(cls, data, instance, validated_data):
        cls.check_or_create_if_updated(instance)
        if "object_prices" in data:
            cls.update_prices(instance, data.pop("object_prices"))
        if "image_objects" in data:
            cls.update_images(instance, data.pop("image_objects"))
        if "facility" in data:
            cls.update_facilities(instance, data.pop("facility"))
        cls.update_basic_attributes(instance, validated_data)
        instance.save()
        return instance

    @classmethod
    def update_prices(cls, instance, prices_data):
        existing_ids = [price["id"] for price in prices_data if "id" in price]
        instance.object_prices.exclude(id__in=existing_ids).delete()
        for price_data in prices_data:
            price_id = price_data.get("id")
            if price_id:
                price_obj = cls.price_model.objects.get(id=price_id, object=instance)
                for key, value in price_data.items():
                    setattr(price_obj, key, value)
                price_obj.save()
            else:
                cls.price_model.objects.create(**price_data, object=instance)

    @classmethod
    def update_basic_attributes(cls, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

    @classmethod
    def update_images(cls, instance, images_data):
        cls.image_model.objects.filter(object=instance).delete()
        images_to_create = [
            cls.image_model(object=instance, image=img) for img in images_data
        ]
        cls.image_model.objects.bulk_create(images_to_create)

    @classmethod
    def update_facilities(cls, instance, facilities_data):
        if facilities_data:
            instance.facility.clear()
            for facility_id in facilities_data:
                facility_obj = cls.facility_model.objects.get(id=facility_id)
                instance.facility.add(facility_obj)

    @classmethod
    def check_or_create_if_updated(cls, instance):
        if cls.check_model.objects.filter(
            object=instance, choice="updated", is_checked=False
        ).exists():
            raise UnifiedErrorResponse(
                detail="This object was already updated", code=405
            )
        else:
            cls.check_model.objects.create(object=instance, choice="updated")

    @classmethod
    def calculate_vendor_analytics(cls, *args, **kwargs):
        start_of_month = cls.get_start_of_month()
        queryset = cls.model.objects.filter(*args, **kwargs).annotate(
            object_total_clients_all_time=Coalesce(
                cls.get_total_clients_subquery("orders__match_object_id"), 0
            ),
            object_total_clients_current_month=Coalesce(
                cls.get_total_clients_subquery("orders__match_object_id", start_of_month), 0
            ),
            object_total_revenue_all_time=Coalesce(
                cls.get_total_revenue_subquery("orders__match_object_id"), 0
            ),
            object_total_revenue_current_month=Coalesce(
                cls.get_total_revenue_subquery("orders__match_object_id", start_of_month), 0
            ),
            object_total_views=Coalesce(Count(
                'object_views',
                distinct=True
            ), 0))

        aggregated_data = queryset.aggregate(
            total_clients_all_time=Sum('object_total_clients_all_time'),
            total_clients_current_month=Sum('object_total_clients_current_month'),
            total_revenue_all_time=Sum('object_total_revenue_all_time'),
            total_revenue_current_month=Sum('object_total_revenue_current_month'),
            total_views=Sum('object_total_views')
        )

        return aggregated_data

    @staticmethod
    def get_start_date_from_filter(date_filter):
        now = timezone.now()

        if date_filter == "week":
            return now - datetime.timedelta(weeks=1)
        elif date_filter == "month":
            return now - datetime.timedelta(days=30)
        elif date_filter == "half_year":
            return now - datetime.timedelta(days=182)
        else:
            return None

    @classmethod
    def get_offers(cls, request, *args, **kwargs):
        date_filter = request.query_params.get("date", "all")
        start_date = cls.get_start_date_from_filter(date_filter)
        queryset = cls.offer_model.objects.filter(*args, **kwargs)

        if start_date:
            queryset = queryset.filter(order__travel_detail__date__end_date__gte=start_date)

        queryset = (queryset
                    .select_related('order__travel_detail__date')
                    .annotate(date=TruncDay('order__travel_detail__date__end_date'))
                    .values('date').annotate(total_price=Sum('price'))
                    .order_by('date')
                    )
        return queryset


class ObjectCheckService(Service):
    model = models.ObjectCheck

    @classmethod
    def get_queryset(cls, request, *args, **kwargs):
        queryset = cls.model.objects.filter(*args, **kwargs)
        choice = request.query_params.get("choice", None)
        if choice is not None:
            queryset = queryset.filter(choice__exact=choice)
        return queryset


class ObjectReviewService(Service):
    model = review_models.ObjectReview
    check_model = review_models.ReviewCheck
    object_image_model = models.ObjectImage

    @classmethod
    def get_queryset(cls, *args, **kwargs):
        queryset = (cls.model.objects
                    .filter(*args, **kwargs)
                    .select_related("user", "object")
                    )
        return queryset

    @staticmethod
    def get_avg_reviews(object):
        reviews = object.object_reviews.all()
        if reviews.exists():
            return {
                "average_quality": reviews.aggregate(Avg('quality'))['quality__avg'] or 0,
                "average_conveniences": reviews.aggregate(Avg('conveniences'))['conveniences__avg'] or 0,
                "average_purity": reviews.aggregate(Avg('purity'))['purity__avg'] or 0,
                "average_location": reviews.aggregate(Avg('location'))['location__avg'] or 0
            }
        return {
            "average_quality": 0,
            "average_conveniences": 0,
            "average_purity": 0,
            "average_location": 0
        }

    @classmethod
    def get_review_check_queryset(cls, request, *args, **kwargs):
        queryset = (cls.check_model.objects
                    .filter(*args, **kwargs)
                    .select_related("review__user", "review__object__location")
                    .prefetch_related(
                        Prefetch("review__object__image_objects",
                                 queryset=cls.object_image_model.objects.all())
                        )
                    )
        choice = request.query_params.get("choice", None)
        if choice is not None:
            queryset = queryset.filter(choice__exact=choice)

        return queryset
