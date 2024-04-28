from django.utils import timezone
from rest_framework import status

from apps.common.exceptions import UnifiedErrorResponse
from apps.common.services import Service
from apps.reviews import models as review_models
from apps.travels import models as travel_models
from django.db import models as db_models


class ReviewService(Service):
    model = review_models.ObjectReview
    offer_model = travel_models.TravelOffer

    @classmethod
    def get_queryset(cls, *args, **kwargs):
        queryset = cls.model.objects.filter(*args, **kwargs).select_related(
            "user", "object"
        )
        return queryset

    @classmethod
    def get_queryset_to_check(cls, *args, **kwargs):
        current_date = timezone.now()
        queryset = (
            cls.offer_model.objects.filter(*args, **kwargs)
            .select_related("order__travel_detail__user", "order__match_object")
            .annotate(
                has_review=db_models.Exists(
                    cls.model.objects.filter(
                        object_id=db_models.OuterRef("order__match_object__id"),
                        user_id=db_models.OuterRef("order__travel_detail__user_id"),
                    )
                )
            )
            .filter(
                db_models.Q(order__travel_detail__date__end_date__lt=current_date),
                db_models.Q(is_payed=True),
                ~db_models.Q(has_review=True),
            )
            .order_by("order__travel_detail__date__end_date")
        ).first()
        if not queryset:
            raise UnifiedErrorResponse(
                detail="Object not found", code=status.HTTP_404_NOT_FOUND
            )

        return queryset

    @classmethod
    def create_review(cls, user_id, validated_data):
        return cls.model.objects.create(**validated_data, user_id=user_id)
