from rest_framework import generics
from apps.analytics.permissions import IsVendor
from apps.analytics.serializers import *
from apps.analytics import services
from apps.travels.serializers import *


class AnalyticsView(generics.RetrieveAPIView):
    serializer_class = AnalyticSerializer
    permission_classes = [IsVendor]
    lookup_field = 'pk'


class AnalyticRejectedClientList(generics.ListAPIView):
    serializer_class = TravelOfferSerializer
    permission_classes = [IsVendor]
    lookup_field = 'pk'

    def get_queryset(self):
        return services.AnalyticsRejectedClientServices.get_queryset(
            is_accepted=False
        )


class AnalyticsRejectedVendorList(generics.ListAPIView):
    serializer_class = TravelOfferSerializer
    permission_classes = [IsVendor]
    lookup_field = 'pk'

    def get_queryset(self):
        return services.AnalyticsRejectedVendorServices.get_queryset(
            approved=False
        )


class AnalyticsCancellationClientList(generics.ListAPIView):
    serializer_class = TravelOfferSerializer
    permission_classes = [IsVendor]
    lookup_field = 'pk'

    def get_queryset(self):
        return services.AnalyticsCancellationClientServices.get_queryset(
            is_accepted=True,
            is_payed=False
        )