from rest_framework import generics, parsers, permissions, views

from apps.houserent.permissions import IsVendor
from apps.travels import services, serializers
from drf_multiple_model.views import ObjectMultipleModelAPIView
from drf_multiple_model.pagination import MultipleModelLimitOffsetPagination

from apps.travels.permissions import IsUserOwnerOrReadOnly


class TravelDetailAPIView(generics.RetrieveAPIView):
    serializer_class = serializers.TravelDetailCreateSerializer
    # permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'

    def get_queryset(self):
        return services.TravelDetailCreateService.get_queryset(
            is_deleted=False
        )


class TravelsCreateAPIView(generics.CreateAPIView):
    serializer_class = serializers.TravelDetailCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        return services.TravelDetailCreateService.create_travel_detail(self.request, self.request.data)

    def perform_create(self, serializer):
        return services.TravelDetailCreateService.create_travel_detail(self.request, self.request.data)


class ObjectsTypesAndKindsAPIView(ObjectMultipleModelAPIView):
    pagination_class = MultipleModelLimitOffsetPagination
    # permission_classes = [permissions.IsAuthenticated]

    def get_querylist(self):
        querylist = services.ObjectsTypeAndKindService.get_querylist(self.request)
        return querylist


class OrderDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.OrderDetailSerializer
    # permission_classes = [IsVendor]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]
    lookup_field = 'pk'

    def get_queryset(self):
        return services.OrderDetailService.get_queryset(
            is_deleted=False,
        )


class TravelDetailDeleteAPIView(views.APIView):
    # permission_classes = [IsUserOwnerOrReadOnly]

    def delete(self, request, *args, **kwargs):
        return services.TravelDetailCreateService.delete_travel_detail(
            travel_detail_id=kwargs.get('travel_id')
        )


class OrderRejectDeleteAPIView(views.APIView):
    # permission_classes = [IsVendor]

    def delete(self, request, *args, **kwargs):
        return services.OrderDetailService.delete_order(
            order_id=kwargs.get('order_id')
        )


class TravelOfferCreateAPIView(generics.CreateAPIView):
    serializer_class = serializers.TravelDetailCreateSerializer
    # permission_classes = [IsVendor]

    def create(self, request, *args, **kwargs):
        return services.TravelOfferService.create_offer(
            validated_data=request.data,
            order=kwargs.get('order_id')
        )

    def perform_create(self, serializer, *args, **kwargs):
        return services.TravelOfferService.create_offer(
            validated_data=self.request.data,
            order=kwargs.get('order_id')
        )


class TravelOfferDetailAPIView(generics.RetrieveAPIView):
    serializer_class = serializers.TravelOfferWithEmailSerializer
    # permission_classes = [IsVendor]
    lookup_field = 'pk'

    def get_queryset(self):
        return services.TravelOfferService.get_queryset(
            is_deleted=False
        )


class TravelOfferDeleteAPIView(views.APIView):
    # permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        return services.TravelOfferService.delete_offer(
            offer_id=kwargs.get('offer_id')
        )


class PastOfferListAPIView(generics.ListAPIView):
    serializer_class = serializers.PastOffersSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = services.TravelOfferService.get_queryset(
            order__travel_detail__user=self.request.user.user,
            is_payed=True
        )
        return services.TravelOfferService.filter_past(
            queryset=queryset,
            request=self.request.query_params,
        )


class ActiveOfferListAPIView(generics.ListAPIView):
    serializer_class = serializers.TravelOfferWithEmailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = services.TravelOfferService.get_queryset(
            order__travel_detail__user=self.request.user.user,
            is_payed=True
        )
        return services.TravelOfferService.filter_active(
            queryset=queryset,
            request=self.request.query_params,
        )


class UserRejectedOfferListAPIView(generics.ListAPIView):
    serializer_class = serializers.TravelOfferSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return services.TravelOfferService.get_queryset(
            order__match_object__vendor=self.request.user.vendor,
            is_deleted=True
        )


class UserRejectedOrderOfferListAPIView(generics.ListAPIView):
    serializer_class = serializers.TravelOfferSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return services.TravelOfferService.get_queryset(
            order__match_object__vendor=self.request.user.vendor,
            is_accepted=False
        )


class VendorRejectedOfferListAPIView(generics.ListAPIView):
    serializer_class = serializers.OrderDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return services.OrderDetailService.get_queryset(
            match_object__vendor=self.request.user.vendor,
            approved=False
        )
