from rest_framework import serializers


class AnalyticSerializer(serializers.Serializer):
    actual_views = serializers.IntegerField()
    total_income_date = serializers.IntegerField()
    total_income = serializers.IntegerField()
    income_month = serializers.IntegerField()
    income = serializers.IntegerField()
    client_month = serializers.IntegerField()
    client = serializers.IntegerField()
    analytics_date_total = serializers.IntegerField()
    analytics_date = serializers.IntegerField()
    read_only_fields = ('vendor',)

