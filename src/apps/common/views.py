from django.apps import apps
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from apps.common.serializers import ModelSerializer
from django.db.models.fields.related import ForeignKey, ManyToManyField



class ListModelsView(APIView):
    excluded_models = [
        "auth", "admin", "contenttypes", "sessions", "django_celery_beat"
    ]
    def get(self, request, *args, **kwargs):
        models = apps.get_models()
        data = []
        for model in models:
            if model._meta.app_label not in self.excluded_models:
                model_fields = {}

                for field in model._meta.get_fields():
                    if hasattr(field, 'verbose_name'):
                        field_info = {
                            'type': field.get_internal_type(),
                            'verbose_name': field.verbose_name
                        }
                        if isinstance(field, ForeignKey) or isinstance(field, ManyToManyField):
                            field_info['related_model'] = field.related_model.__name__

                        model_fields[field.name] = field_info

                model_info = {
                    'name': model.__name__,
                    'app_label': model._meta.app_label,
                    'fields': model_fields,
                }
                data.append(model_info)

        serializer = ModelSerializer(data=data, many=True)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)


def get_model_serializer(model):
    """Dynamically creates a serializer class for a given model."""
    class DynamicModelSerializer(ModelSerializer):
        class Meta:
            pass

    DynamicModelSerializer.Meta.model = model
    DynamicModelSerializer.Meta.fields = '__all__'

    return DynamicModelSerializer


class DynamicModelCreateView(CreateAPIView):
    def get_serializer_class(self):
        app_label = self.kwargs.get('app_label')
        model_name = self.kwargs.get('model_name')
        model = apps.get_model(app_label, model_name)
        return get_model_serializer(model)

    def get_queryset(self):
        app_label = self.kwargs.get('app_label')
        model_name = self.kwargs.get('model_name')
        model = apps.get_model(app_label, model_name)
        return model.objects.all()

    def perform_create(self, serializer):
        serializer.save()
