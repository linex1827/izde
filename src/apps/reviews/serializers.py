from apps.reviews import services
from apps.reviews.models import ObjectReview
from rest_framework import serializers


class ObjectReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ObjectReview
        fields = [
            "id",
            "user",
            "object",
            "quality",
            "conveniences",
            "purity",
            "location",
            "comment",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "user"]

    def create(self, validated_data):
        return services.ReviewService.create_review(
            user_id=self.context["request"].user.id, validated_data=validated_data
        )


class ObjectReviewCheckSerializer(serializers.Serializer):
    id = serializers.PrimaryKeyRelatedField(read_only=True)
    has_review = serializers.BooleanField(read_only=True)
    object = serializers.PrimaryKeyRelatedField(read_only=True, source="order__match_object")
