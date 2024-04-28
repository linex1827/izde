from rest_framework import serializers


class ModelSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    app_label = serializers.CharField(max_length=255)
    fields = serializers.DictField(
        child=serializers.DictField()
    )
