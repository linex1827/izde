from django.urls import path
from apps.reviews import views


urlpatterns = [
    path("check/", views.CheckTravelsForReview.as_view(), name="check-to-review"),
    path(
        "create/",
        views.ObjectReviewCreateAPIView.as_view(),
        name="review-create",
    ),
    path(
        'detail_reviews/<uuid:location_object_id>/', views.DetailReviewsListAPIView.as_view(),
        name='list-reviews'
    )
]
