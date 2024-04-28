from django.urls import path
from django.views.decorators.cache import cache_page
from apps.travels import views

urlpatterns = [
    # For User
    path(
        '<uuid:pk>/',
        views.TravelDetailAPIView.as_view(),
        name='travel',
    ),
    path(
        'create/',
        views.TravelsCreateAPIView.as_view(),
        name='travel-create',
    ),
    path(
        'object_things/',
        views.ObjectsTypesAndKindsAPIView.as_view(),
        name='object-things',
    ),
    path(
        '<uuid:travel_id>/delete/',
        views.TravelDetailDeleteAPIView.as_view(),
        name='travel-delete',
    ),

    # For Vendor
    path(
        'order/<uuid:pk>/',
        views.OrderDetailAPIView.as_view(),
        name='order',
    ),
    path(
        'order/<uuid:order_id>/reject/',
        views.OrderRejectDeleteAPIView.as_view(),
        name='order-reject',
    ),
    path(
        'order/<uuid:order_id>/offer/',
        views.TravelOfferCreateAPIView.as_view(),
        name='offers',
    ),
    path(
        'offer/',
        views.ActiveOfferListAPIView.as_view(),
        name='offers',
    ),
    path(
        'offer/<uuid:pk>/',
        views.TravelOfferDetailAPIView.as_view(),
        name='offer-detail',
    ),
    path(
        'offer/past/',
        views.PastOfferListAPIView.as_view(),
        name='offer_past',
    ),
    path(
        'offer/client_rejected/',
        views.UserRejectedOfferListAPIView.as_view(),
        name='offer-rejected',
    ),
    path(
        'offer/<uuid:offer_id>/delete/',
        views.TravelOfferDeleteAPIView.as_view(),
        name='offer-delete',
    ),
    path(
        'offer/vendor_rejected/',
        views.VendorRejectedOfferListAPIView.as_view(),
        name='offer_vendor_reject',
    ),
    path(
        'offer/reject_booked/',
        views.UserRejectedOrderOfferListAPIView.as_view(),
        name='reject_booked_offer',
    ),

]
