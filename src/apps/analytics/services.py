from apps.common.services import Service
from django.db.models import Count, Sum, Q
from datetime import timedelta
from apps.profiles.models.user import Vendor
from apps.travels.models import Orders, TravelOffer
from django.utils import timezone


class AnalyticService(Service):
    model = Vendor

    @classmethod
    def get_total_income(cls, period, vendor_id):
        today = timezone.now()
        if period == 'week':
            start_date = today - timedelta(days=7)
        elif period == 'month':
            start_date = today - timedelta(days=30)
        elif period == 'six_months':
            start_date = today - timedelta(days=180)
        else:
            return None

        total_stats = cls.model.objects.filter(id=vendor_id).annotate(
            total_income_date=Sum('vendor__user_currencies__transactions__amount', filter=Q(
                analytics_date_total__gte=start_date, vendor__user_currencies__transactions__pg_result="успешно")),
            total_income=Sum('vendor__user_currencies__transactions__amount', filter=Q(
                vendor__user_currencies__transactions__pg_result="успешно"
            )),
        ).first()
        return total_stats

    @classmethod
    def get_income_client(cls, period, vendor_id):
        today = timezone.now()
        if period == 'month':
            start_date = today - timedelta(days=30)
        else:
            return None

        income_client_stats = cls.model.objects.filter(id=vendor_id).annotate(
            income_month=Sum('vendor__user_currencies__transactions__amount', filter=Q(
                analytics_date=start_date, vendor__user_currencies__transactions__pg_result="успешно")),
            income=Sum('vendor__user_currencies__transactions__amount', filter=Q(
                vendor__user_currencies__transactions__pg_result="успешно")),
            client_month=Count('vendors__orders__offers', filter=Q(analytics_date=start_date,
                                                                   vendors__orders__approved=True,
                                                                   vendors__orders__offers__is_accepted=True,
                                                                   vendors__orders__offers__is_payed=True)),
            client=Count('vendors__orders__offers', filter=Q(vendors__orders__approved=True,
                                                             vendors__orders__offers__is_accepted=True,
                                                             vendors__orders__offers__is_payed=True)),
            actual_views=Sum('vendors__object_locations__views'),

        ).first()
        return income_client_stats


class AnalyticsRejectedClientServices(Service):
    model = TravelOffer

    @classmethod
    def get_rejected_client(cls, offers_id, *args, **kwargs):
        queryset = cls.model.objects.filter(id=offers_id, *args,
                                            **kwargs).select_related('offers__orders__travel__user',
                                                                     'offers').order_by('-created_at')
        return queryset


class AnalyticsRejectedVendorServices(Service):
    model = Orders

    @classmethod
    def get_rejected_client(cls, offers_id, *args, **kwargs,):
        queryset = cls.model.objects.filter(id=offers_id, *args,
                                            **kwargs).select_related('orders__travel__user',
                                                                     'orders__offers').order_by('-created_at')
        return queryset


class AnalyticsCancellationClientServices(Service):
    model = TravelOffer

    @classmethod
    def get_rejected_client(cls, offers_id, *args, **kwargs):
        queryset = cls.model.objects.filter(id=offers_id, *args,
                                            **kwargs).select_related('offers_orders__travel__user',
                                                                     'offers').order_by('-created_at')
        return queryset





