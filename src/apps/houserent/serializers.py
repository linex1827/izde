from rest_framework import serializers
from apps.houserent import models, services
from apps.profiles.models import user as user_models
from apps.reviews import models as review_models
from apps.travels import models as travel_models


class PlacementSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Placement
        fields = [
            "id",
            "name",
            "lft",
            "rght",
            "tree_id",
            "level",
            "parent",
        ]
        depth = 2


class CurrencyNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Currency
        fields = ["id", "title", "price"]


class LocationFacilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.LocationFacility
        fields = ["id", "name"]


class LocationImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.LocationImage
        fields = [
            "id",
            "image",
        ]
        read_only_fields = ["id"]


class LocationListSerializer(serializers.ModelSerializer):
    facility = LocationFacilitySerializer(many=True, read_only=True)
    objects_count = serializers.IntegerField(read_only=True)
    placement = PlacementSerializer(read_only=True)

    class Meta:
        model = models.Location
        fields = [
            "id",
            "name",
            "facility",
            "street",
            "house",
            "placement",
            "objects_count",
        ]


class LocationNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Location
        fields = ["id", "name"]


class LocationDetailSerializer(serializers.ModelSerializer):
    facility = LocationFacilitySerializer(many=True, read_only=True)
    objects_count = serializers.IntegerField(read_only=True)
    image_locations = LocationImageSerializer(many=True, read_only=True)
    placement = PlacementSerializer(read_only=True)

    class Meta:
        model = models.Location
        fields = [
            "id",
            "name",
            "street",
            "house",
            "placement",
            "address_link",
            "facility",
            "rules",
            "objects_count",
            "image_locations",
        ]


"""ОБЪЕКТЫ"""


class ObjectFacilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ObjectFacility
        fields = ["id", "name"]


class ObjectKindSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ObjectKind
        fields = ["id", "name", "counter"]


class ObjectTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ObjectType
        fields = ["id", "name"]


class ObjectImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ObjectImage
        fields = ["id", "image"]


class ObjectPriceSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(required=False)

    class Meta:
        model = models.ObjectPrice
        fields = ["id", "start_date", "end_date", "price"]


class LocationObjectListSerializer(serializers.ModelSerializer):
    object_type = ObjectTypeSerializer(read_only=True)
    object_kind = ObjectKindSerializer(read_only=True)
    image_objects = ObjectImageSerializer(many=True, read_only=True)
    location = LocationNameSerializer(read_only=True)
    current_price = serializers.IntegerField(read_only=True)
    is_checked = serializers.BooleanField(read_only=True)
    objects_count = serializers.IntegerField(read_only=True)
    currency = CurrencyNameSerializer(read_only=True)

    class Meta:
        model = models.LocationObject
        fields = [
            "id",
            "name",
            "location",
            "object_type",
            "objects_count",
            "object_kind",
            "image_objects",
            "current_price",
            "currency",
            "is_checked",
        ]


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = user_models.User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
        ]


class ObjectReviewSerializer(serializers.ModelSerializer):
    user = AuthorSerializer(read_only=True)

    class Meta:
        model = review_models.ObjectReview
        fields = [
            "id",
            "user",
            "quality",
            "conveniences",
            "purity",
            "location",
            "comment",
            "created_at",
            "updated_at",
        ]


class ObjectVendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = user_models.Vendor
        fields = ["id", "icon", "first_name", "last_name"]


class LocationObjectDetailSerializer(serializers.ModelSerializer):
    location = LocationListSerializer(read_only=True)
    facility = ObjectFacilitySerializer(many=True, read_only=True, required=False)
    object_type = ObjectTypeSerializer(read_only=True)
    object_kind = ObjectKindSerializer(read_only=True)
    image_objects = ObjectImageSerializer(many=True, read_only=True, required=False)
    objects_count = serializers.IntegerField(read_only=True)
    object_prices = ObjectPriceSerializer(many=True, required=False)
    review_averages = serializers.SerializerMethodField()
    reviews_count = serializers.IntegerField(read_only=True)
    total_revenue_all_time = serializers.IntegerField(read_only=True)
    total_revenue_current_month = serializers.IntegerField(read_only=True)
    total_clients_all_time = serializers.IntegerField(read_only=True)
    total_clients_current_month = serializers.IntegerField(read_only=True)
    is_checked = serializers.BooleanField(read_only=True)
    currency = CurrencyNameSerializer(read_only=True)
    vendor = ObjectVendorSerializer(read_only=True)

    class Meta:
        model = models.LocationObject
        fields = [
            "id",
            "location",
            "vendor",
            "name",
            "description",
            "room_quantity",
            "occupancy",
            "facility",
            "image_objects",
            "object_type",
            "object_kind",
            "objects_count",
            "object_prices",
            "check_in",
            "check_out",
            "rules",
            "partnership",
            "currency",
            "review_averages",
            "reviews_count",
            "total_revenue_all_time",
            "total_revenue_current_month",
            "total_clients_all_time",
            "total_clients_current_month",
            "is_checked",
            "full_refund_cutoff_hours",
            "partial_refund_cutoff_hours",
            "cancellation_policy",
        ]

    def get_review_averages(self, obj):
        return services.ObjectReviewService.get_avg_reviews(
            object=obj
        )

    def update(self, instance, validated_data):
        return services.LocationObjectService.update_object(
            data=self.context["request"].data,
            instance=instance,
            validated_data=validated_data,
        )


class LocationObjectCreateSerializer(serializers.ModelSerializer):
    facility = ObjectFacilitySerializer(many=True, read_only=True)
    object_prices = ObjectPriceSerializer(many=True, read_only=True)
    image_objects = ObjectImageSerializer(many=True, read_only=True)
    vendor = serializers.PrimaryKeyRelatedField(read_only=True)
    currency = CurrencyNameSerializer(read_only=True)
    description = serializers.CharField(max_length=1000)
    rules = serializers.CharField(max_length=1000)

    uploaded_images = serializers.ListField(
        child=serializers.ImageField(
            max_length=1000000, allow_empty_file=False, use_url=False
        ),
        write_only=True,
    )

    uploaded_prices = serializers.ListField(
        child=ObjectPriceSerializer(), write_only=True
    )

    uploaded_facilities = serializers.ListField(
        child=serializers.UUIDField(allow_null=True), write_only=True
    )

    class Meta:
        model = models.LocationObject
        fields = [
            "id",
            "location",
            "name",
            "description",
            "room_quantity",
            "object_prices",
            "occupancy",
            "facility",
            "image_objects",
            "uploaded_images",
            "vendor",
            "currency",
            "object_type",
            "object_kind",
            "check_in",
            "check_out",
            "rules",
            "partnership",
            "uploaded_facilities",
            "uploaded_prices",
            "full_refund_cutoff_hours",
            "partial_refund_cutoff_hours",
            "cancellation_policy"
        ]
        read_only_fields = [
            "id",
        ]

    def create(self, validated_data):
        return services.LocationObjectService.create_object(
            validated_data, self.context["request"].user.id
        )


class ObjectShortSerializer(serializers.ModelSerializer):
    location = LocationNameSerializer(read_only=True)
    image_objects = ObjectImageSerializer(read_only=True, many=True)

    class Meta:
        model = models.LocationObject
        fields = ["id", "name", "location", "image_objects"]


class ObjectCheckSerializer(serializers.ModelSerializer):
    object = ObjectShortSerializer(read_only=True)

    class Meta:
        model = models.ObjectCheck
        fields = ["id", "choice", "object", "is_checked", "created_at", "is_declined"]


class ReviewCheckSerializer(serializers.ModelSerializer):
    object = ObjectShortSerializer(read_only=True, source="review.object")
    review = ObjectReviewSerializer(read_only=True)

    class Meta:
        model = review_models.ReviewCheck
        fields = [
            "id",
            "review",
            "object",
            "choice",
            "created_at"
        ]


class VendorAnalyticsSerializer(serializers.ModelSerializer):
    total_clients_all_time = serializers.IntegerField(read_only=True)
    total_clients_current_month = serializers.IntegerField(read_only=True)
    total_revenue_all_time = serializers.IntegerField(read_only=True)
    total_revenue_current_month = serializers.IntegerField(read_only=True)
    total_views = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.LocationObject
        fields = [
            "id",
            "total_clients_all_time",
            "total_clients_current_month",
            "total_revenue_all_time",
            "total_revenue_current_month",
            "total_views"
        ]


class VendorOffersSerializer(serializers.ModelSerializer):
    date = serializers.DateField(read_only=True)
    total_price = serializers.IntegerField(read_only=True)

    class Meta:
        model = travel_models.TravelOffer
        fields = [
            "id",
            "date",
            "total_price",
        ]
