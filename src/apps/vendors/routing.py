from django.urls import path, re_path
from apps.profiles.consumers import user
from apps.vendors import consumers

websocket_urlpatterns = [
    path('orders/', consumers.VendorConsumer.as_asgi()),
    path('deleted_orders/', consumers.VendorDeleteOrderConsumer.as_asgi()),
    path('offers/', user.UserConsumer.as_asgi()),
    path('deleted_offers/', user.DeletedOffersConsumer.as_asgi()),
    path('payment_status/', user.PaymentResultConsumer.as_asgi()),
]