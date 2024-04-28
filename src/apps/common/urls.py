from django.urls import path
from apps.common import views

urlpatterns = [
    path('models/', views.ListModelsView.as_view(), name='list-models'),
    path('models/<str:app_label>/<str:model_name>/create/', views.DynamicModelCreateView.as_view(), name='dynamic-model-create'),

]
