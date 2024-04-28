from django.urls import path
from apps.analytics.views import AnalyticsView, AnalyticRejectedClientList, AnalyticsRejectedVendorList, \
    AnalyticsCancellationClientList

urlpatterns = [
     path('<uuid:pk>/analytics/', AnalyticsView.as_view(),
          name='Analytics'),
     path('<uuid:pk>/analytics/rejected/client/', AnalyticRejectedClientList.as_view(),
          name='Rejected-Client-List'),
     path('<uuid:pk>/analytics/rejected/vendor/', AnalyticsRejectedVendorList.as_view(),
          name='Rejected-Vendor-List'),
     path('<uuid:pk>/analytics/cancellation/client/', AnalyticsCancellationClientList.as_view(),
          name='Cancellation-Client-List')
 ]
