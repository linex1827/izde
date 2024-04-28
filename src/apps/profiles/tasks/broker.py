import json
from datetime import timedelta
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import redis
from decouple import config
from django.db.models import OuterRef, Subquery
from apps.profiles.models.payment import Transaction
from apps.profiles.serializers.user import OfferSerializer
from apps.profiles.tasks.sendCode import send_verification_code_task
from apps.travels.models import Orders, TravelOffer
from celery import shared_task
from apps.vendors.serializers import OrderSerializer
from apps.houserent.models import ObjectPrice


@shared_task
def send_order(order_id, vendor_email):
    prices = ObjectPrice.objects.filter(
        object_id=OuterRef('match_object__id'),
        start_date__lte=OuterRef('travel_detail__date__end_date'),
        end_date__gte=OuterRef('travel_detail__date__end_date')
    ).order_by('start_date')

    price_subquery = Subquery(prices.values('price')[:1])

    order_object = Orders.objects.filter(id=order_id, is_deleted=False, is_sent=False).annotate(
        matched_price=price_subquery
    ).first()

    order_object.created_at += timedelta(minutes=5)
    order_object.save()
    serialized_data = OrderSerializer(order_object).data
    json_data = json.dumps(serialized_data, ensure_ascii=False)
    r = redis.Redis(host=config('redis_host'), port=6379, db=0, password='myPass',
                    username='default')
    channel_name = r.hget('vendor_connections', vendor_email)
    channel_layer = get_channel_layer()
    if channel_name:
        decoded_data = channel_name.decode('utf-8')
        order_object.is_sent = True
        order_object.save()
        async_to_sync(channel_layer.send)(decoded_data, {
            'type': 'send_orders',
            'message': json_data
        })


@shared_task
def send_orders(vendor_email):
    orders = Orders.objects.filter(
        is_sent=False,
        is_deleted=False,
        match_object__vendor__email=vendor_email,
        approved=None,
    )

    serialized_data = OrderSerializer(orders, many=True).data
    orders.update(is_sent=True)
    json_data = json.dumps(serialized_data, ensure_ascii=False)

    r = redis.Redis(host=config('redis_host'), port=6379, db=0, password='myPass',
                    username='default')
    channel_name = r.hget('vendor_connections', vendor_email)
    decoded_data = channel_name.decode('utf-8')
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.send)(decoded_data, {
        'type': 'send_orders',
        'message': json_data
    })


@shared_task
def deleted_expired_orders(order_id, email, type_connections, send_type):
    orders = Orders.objects.filter(
        id=order_id,
        is_deleted=False,
        approved=None,
    )
    if orders.exists():
        order = orders[0]
        r = redis.Redis(host=config('redis_host'), port=6379, db=0, password='myPass',
                        username='default')
        channel_layer = get_channel_layer()
        channel_name = r.hget(type_connections, email)
        if channel_name:
            decoded_data = channel_name.decode('utf-8')
            async_to_sync(channel_layer.send)(decoded_data, {
                'type': send_type,
                'message': json.dumps(str(order.id), ensure_ascii=False)
            })
        order.is_deleted = True
        order.save()


@shared_task
def send_offer(offer_id, user_email):
    order_object = TravelOffer.objects.get(id=offer_id, is_deleted=False, is_sent=False)
    order_object.created_at += timedelta(minutes=5)
    order_object.save()

    serialized_data = OfferSerializer(order_object).data
    json_data = json.dumps(serialized_data, ensure_ascii=False)
    r = redis.Redis(host=config('redis_host'), port=6379, db=0, password='myPass',
                    username='default')
    channel_name = r.hget('user_connections', user_email)
    channel_layer = get_channel_layer()
    if channel_name:
        decoded_data = channel_name.decode('utf-8')
        order_object.is_sent = True
        order_object.save()
        async_to_sync(channel_layer.send)(decoded_data, {
            'type': 'send_offers',
            'message': json_data
        })


@shared_task
def send_offers(user_email):
    orders = TravelOffer.objects.filter(
        is_sent=False,
        is_deleted=False,
        is_accepted=None,
        order__travel_detail__user__email=user_email,
    )

    serialized_data = OfferSerializer(orders, many=True).data
    orders.update(is_sent=True)
    json_data = json.dumps(serialized_data, ensure_ascii=False)

    r = redis.Redis(host=config('redis_host'), port=6379, db=0, password='myPass',
                    username='default')
    channel_name = r.hget('user_connections', user_email)
    decoded_data = channel_name.decode('utf-8')
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.send)(decoded_data, {
        'type': 'send_offers',
        'message': json_data
    })


@shared_task
def send_deleted_offers(user_email):
    orders = TravelOffer.objects.filter(
        is_sent=True,
        is_deleted=True,
        order__travel_detail__user__email=user_email,
        is_accepted=None,
    ).values_list('id', flat=True)

    order_ids_str = [str(order_id) for order_id in orders]

    orders.update(is_sent=True)

    r = redis.Redis(host=config('redis_host'), port=6379, db=0, password='myPass',
                    username='default')
    channel_name = r.hget('deleted_offers_connections', user_email)
    decoded_data = channel_name.decode('utf-8')
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.send)(decoded_data, {
        'type': 'send_deleted_offers_id',
        'message': json.dumps(order_ids_str, ensure_ascii=False)
    })


@shared_task
def deleted_expired_offers(offer_id, email, type_connections, send_type):
    order_or_offer = TravelOffer.objects.filter(
        id=offer_id,
        is_deleted=False,
        is_accepted=None,
    ).first()
    if order_or_offer:
        r = redis.Redis(host=config('redis_host'), port=6379, db=0, password='myPass',
                        username='default')
        channel_layer = get_channel_layer()
        channel_name = r.hget(type_connections, email)
        if channel_name:
            decoded_data = channel_name.decode('utf-8')
            async_to_sync(channel_layer.send)(decoded_data, {
                'type': send_type,
                'message': json.dumps(str(order_or_offer.id), ensure_ascii=False)
            })
        order_or_offer.is_deleted = True
        order_or_offer.save()


@shared_task
def send_payment_status(transaction_id):
    transaction = Transaction.objects.filter(id=transaction_id).first()
    offer = transaction.travel_offer
    if transaction.pg_result == 'успешно':
        offer.is_payed = True
        offer.save()
        send_verification_code_task.delay(offer.order.travel_detail.user.email)
    else:
        offer.is_payed = False
        offer.save()
    r = redis.Redis(host=config('redis_host'), port=6379, db=0, password='myPass',
                    username='default')
    channel_layer = get_channel_layer()
    channel_name = r.hget('payment_connections', offer.order.travel_detail.user.email)
    if channel_name:
        transaction.is_sent = True
        transaction.save()
        decoded_data = channel_name.decode('utf-8')
        async_to_sync(channel_layer.send)(decoded_data, {
            'type': 'send_payment_status',
            'message': json.dumps({'status': offer.is_payed}, ensure_ascii=False)
        })


@shared_task
def send_some_payment_status(user_email):
    transaction = Transaction.objects.filter(user__email=user_email, is_deleted=False, is_sent=False).first()
    print(transaction)
    if transaction:
        print(transaction)
        r = redis.Redis(host=config('redis_host'), port=6379, db=0, password='myPass',
                        username='default')
        channel_layer = get_channel_layer()
        channel_name = r.hget('payment_connections', user_email)
        if channel_name:
            transaction.is_sent = True
            transaction.save()
            decoded_data = channel_name.decode('utf-8')
            async_to_sync(channel_layer.send)(decoded_data, {
                'type': 'send_payment_status',
                'message': json.dumps({'status': transaction.travel_offer.is_payed}, ensure_ascii=False)
            })
