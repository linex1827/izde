from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.documentation import include_docs_urls

schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include([
        path('users/', include(('apps.profiles.urls.user', 'profiles'), namespace='profiles_user')),
        path('vendors/', include(('apps.vendors.urls', 'vendors'), namespace='vendors')),
        path('payments/', include(('apps.profiles.urls.payment', 'profiles'), namespace='profiles_payment')),
        path('common/', include(('apps.common.urls', 'common'), namespace='common')),
        path('houserent/', include(('apps.houserent.urls', 'houserent'), namespace='houserent')),
        path('travel/', include(('apps.travels.urls', 'travels'), namespace='travels')),
        path('reviews/', include(('apps.reviews.urls', 'reviews'), namespace='reviews')),
        path('analytics/', include(('apps.analytics.urls', 'analytics'), namespace='analytics')),
        path('notification/', include(('apps.notification.urls', 'notifications'), namespace='notifications')),
    ])),

    path('docs/', include_docs_urls(title='IZDE API')),


    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]
