from apps.profiles.serializers.user import ObjectReviewsSerializer
from apps.reviews import serializers
from rest_framework import permissions, generics
from apps.reviews import services
from apps.reviews.services import ReviewService


class ObjectReviewCreateAPIView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.ObjectReviewCreateSerializer
    queryset = services.ReviewService.get_queryset(is_deleted=False)


class CheckTravelsForReview(generics.ListAPIView):
    serializer_class = serializers.ObjectReviewCheckSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return services.ReviewService.get_queryset_to_check(
            is_deleted=False, order__travel_detail__user_id=self.request.user.id
        )


class DetailReviewsListAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ObjectReviewsSerializer

    def get_queryset(self):
        return ReviewService.get_queryset(is_deleted=False, object=self.kwargs.get('location_object_id'))

