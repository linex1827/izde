from rest_framework import serializers

from apps.houserent.models import Placement


class RecursiveParentSerializer(serializers.ModelSerializer):
    parent = serializers.SerializerMethodField()

    def get_parent(self, obj):
        if obj.parent is not None:
            return RecursiveParentSerializer(obj.parent, context=self.context).data
        return None

    class Meta:
        model = Placement
        fields = ['name', 'parent']


class BookedPaymentAddressSerializer(serializers.ModelSerializer):
    parent = RecursiveParentSerializer()

    class Meta:
        model = Placement
        fields = ['name', 'parent']
