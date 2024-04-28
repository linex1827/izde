from rest_framework import generics, parsers, views, response
from rest_framework.permissions import IsAuthenticated

from apps.houserent import services, serializers, permissions
from apps.common.schemas import houserent as schemas

"""Локации"""


class PlacementListAPIView(generics.ListAPIView):
    serializer_class = serializers.PlacementSerializer
    schema = schemas.PlacementSchema()
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return services.PlacementService.get_queryset(request=self.request)


class LocationFacilityListAPIView(generics.ListAPIView):
    serializer_class = serializers.LocationFacilitySerializer
    permission_classes = [permissions.IsVendor]

    def get_queryset(self):
        return services.LocationFacilityService.search_by_name(request=self.request)


class LocationListAPIView(generics.ListAPIView):
    serializer_class = serializers.LocationListSerializer
    permission_classes = [permissions.IsVendor]

    def get_queryset(self):
        return services.LocationService.get_queryset(is_deleted=False)


class LocationDetailAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = serializers.LocationDetailSerializer
    permission_classes = [permissions.IsVendor]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]
    lookup_field = "pk"

    def get_queryset(self):
        return services.LocationService.get_queryset(
            is_deleted=False,
        )


"""Объекты"""


class ObjectTypeListAPIView(generics.ListAPIView):
    serializer_class = serializers.ObjectTypeSerializer
    permission_classes = [permissions.IsVendor]
    queryset = services.ObjectTypeService.filter(is_deleted=False)
    pagination_class = None


class ObjectKindListAPIView(generics.ListAPIView):
    serializer_class = serializers.ObjectKindSerializer
    permission_classes = [permissions.IsVendor]
    queryset = services.ObjectKindService.filter(is_deleted=False)
    pagination_class = None


class LocationObjectAPIView(generics.ListAPIView):
    serializer_class = serializers.LocationObjectListSerializer
    permission_classes = [permissions.IsVendor]

    def get_queryset(self):
        return services.LocationObjectService.get_queryset_for_list(
            request=self.request, is_deleted=False
        )


class LocationObjectDetailAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = serializers.LocationObjectDetailSerializer
    permission_classes = [permissions.IsVendorOwnerOrReadOnly]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]
    lookup_field = "pk"

    def get_queryset(self):
        return services.LocationObjectService.get_queryset_for_detail(
            is_deleted=False, vendor_id=self.request.user.id
        )


class ObjectReviewListAPIView(generics.ListAPIView):
    serializer_class = serializers.ObjectReviewSerializer
    permission_classes = [permissions.IsVendor]

    def get_queryset(self):
        return services.ObjectReviewService.get_queryset(
            is_deleted=False,
            object_id=self.kwargs["object_id"]
        )


class LocationObjectListAPIView(generics.ListAPIView):
    serializer_class = serializers.LocationObjectListSerializer
    permission_classes = [permissions.IsVendor]

    def get_queryset(self):
        return services.LocationObjectService.get_queryset_for_location(
            request=self.request, location_id=self.kwargs["location_id"], vendor_id=self.request.user.id
        )


class LocationObjectDeleteAPIView(views.APIView):
    permission_classes = [permissions.IsVendorOwnerOrReadOnly]

    def delete(self, request, *args, **kwargs):
        return services.LocationObjectService.delete_objects_from_locations(
            location_object_id=kwargs.get("object_id")
        )


class ObjectFacilityListAPIView(generics.ListAPIView):
    serializer_class = serializers.ObjectFacilitySerializer
    permission_classes = [permissions.IsVendor]
    pagination_class = None

    def get_queryset(self):
        return services.ObjectFacilityService.search_by_name(request=self.request)


class LocationObjectCreateAPIView(generics.CreateAPIView):
    serializer_class = serializers.LocationObjectCreateSerializer
    permission_classes = [permissions.IsVendor]
    queryset = services.LocationObjectService.filter(is_deleted=False)
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]


class ObjectPriceListAPIView(generics.ListAPIView):
    serializer_class = serializers.ObjectPriceSerializer
    permission_classes = [permissions.IsVendor]
    queryset = services.ObjectPriceService.filter(is_deleted=False)

    def get_queryset(self):
        return services.ObjectPriceService.filter(object_id=self.kwargs["object_id"])


class ObjectPriceDeleteAPIView(views.APIView):
    permission_classes = [permissions.IsVendorOwnerOrReadOnly]

    def delete(self, request, *args, **kwargs):
        return services.LocationObjectService.delete_prices_from_objects(
            object_price_id=kwargs.get("price_id")
        )


class ObjectCheckListAPIView(generics.ListAPIView):
    serializer_class = serializers.ObjectCheckSerializer
    permission_classes = [permissions.IsVendor]
    schema = schemas.ObjectCheckSchema()

    def get_queryset(self):
        return services.ObjectCheckService.get_queryset(
            request=self.request,
            is_deleted=False,
            object__vendor_id=self.request.user.id,
        )


class ReviewCheckListAPIView(generics.ListAPIView):
    serializer_class = serializers.ReviewCheckSerializer
    permission_classes = [permissions.IsVendor]
    schema = schemas.ReviewCheckSchema()

    def get_queryset(self):
        return services.ObjectReviewService.get_review_check_queryset(
            request=self.request,
            is_deleted=False,
            review__object__vendor_id=self.request.user.id
        )


class VendorAnalyticsAPIView(views.APIView):
    serializer_class = serializers.VendorAnalyticsSerializer
    permission_classes = [permissions.IsVendor]
    pagination_class = None

    def get(self, request, *args, **kwargs):
        analytics_data = services.LocationObjectService.calculate_vendor_analytics(
            is_deleted=False,
            vendor_id=self.request.user.id
        )
        serializer = self.serializer_class(analytics_data)
        return response.Response(serializer.data)


class VendorOffersAPIView(generics.ListAPIView):
    serializer_class = serializers.VendorOffersSerializer
    permission_classes = [permissions.IsVendor]
    pagination_class = None
    schema = schemas.VendorOffersSchema()

    def get_queryset(self):
        return services.LocationObjectService.get_offers(
            request=self.request,
            is_payed=True,
            is_deleted=False,
            order__match_object__vendor_id=self.request.user.id,
        )