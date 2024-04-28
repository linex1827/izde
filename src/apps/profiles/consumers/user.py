import json
import jwt
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from apps.profiles.models.user import User
from apps.profiles.tasks.broker import send_offers, send_deleted_offers, send_some_payment_status
from apps.vendors.utils import add_to_redis, delete_from_redis
from core.settings.base import SECRET_KEY


class UserConsumer(AsyncWebsocketConsumer):
    user_connections = {}

    @sync_to_async
    def get_user(self, user_id):
        return User.objects.get(id=user_id)

    async def connect(self):
        await self.accept()
        token = self.scope['query_string'].decode()
        tk = token.split('=')[1]

        try:
            decoded_token = jwt.decode(tk, SECRET_KEY, algorithms=['HS256'])
            user_id = decoded_token.get("user_id")
            if not user_id:
                await self.close(code=4001)
                return
            user = await self.get_user(decoded_token.get("user_id"))
            if not user:
                await self.close(code=4001)
                return
            self.user_connections[str(user)] = self.channel_name
            add_to_redis('user_connections', str(user), self.channel_name)
            send_offers.delay(str(user))
        except jwt.ExpiredSignatureError:
            await self.send(text_data='{"error": "Invalid token"}')
            await self.close(code=4001)
        except jwt.DecodeError:
            await self.send(text_data='{"error": "Invalid token"}')
            await self.close(code=4001)
        except Exception as e:
            await self.send(text_data=f'{{"error": "{str(e)}"}}')
            await self.close(code=4001)

    async def disconnect(self, event):
        token_to_remove = []
        for user_email, channel_name in self.user_connections.items():
            if channel_name == self.channel_name:
                delete_from_redis('user_connections', user_email)
                token_to_remove.append(user_email)
        del self.user_connections[token_to_remove[0]]

    async def send_offers(self, event):
        message = event["message"]

        await self.send(
            text_data=message
        )


class DeletedOffersConsumer(AsyncWebsocketConsumer):
    deleted_offers_user_connections = {}

    @sync_to_async
    def get_user(self, user_id):
        return User.objects.get(id=user_id)

    async def connect(self):
        await self.accept()
        token = self.scope['query_string'].decode()
        tk = token.split('=')[1]

        try:
            decoded_token = jwt.decode(tk, SECRET_KEY, algorithms=['HS256'])
            user_id = decoded_token.get("user_id")
            if not user_id:
                await self.close(code=4001)
                return
            user = await self.get_user(decoded_token.get("user_id"))
            if not user:
                await self.close(code=4001)
                return
            self.deleted_offers_user_connections[str(user)] = self.channel_name
            add_to_redis('deleted_offers_connections', str(user), self.channel_name)
            send_deleted_offers.delay(str(user))
        except jwt.ExpiredSignatureError:
            await self.send(text_data='{"error": "Invalid token"}')
            await self.close(code=4001)
        except jwt.DecodeError:
            await self.send(text_data='{"error": "Invalid token"}')
            await self.close(code=4001)
        except Exception as e:
            await self.send(text_data=f'{{"error": "{str(e)}"}}')
            await self.close(code=4001)

    async def disconnect(self, event):
        token_to_remove = []
        for user_email, channel_name in self.deleted_offers_user_connections.items():
            if channel_name == self.channel_name:
                delete_from_redis('deleted_offers_connections', user_email)
                token_to_remove.append(user_email)
        del self.deleted_offers_user_connections[token_to_remove[0]]

    async def send_deleted_offers_id(self, event):
        message = event["message"]

        await self.send(
            text_data=message
        )


class PaymentResultConsumer(AsyncWebsocketConsumer):
    @sync_to_async
    def get_user(self, user_id):
        return User.objects.get(id=user_id)

    async def connect(self):
        await self.accept()
        url = self.scope['query_string'].decode()
        user_id = url.split('=')[1]
        user = await self.get_user(user_id)
        add_to_redis('payment_connections', str(user.email), self.channel_name)
        send_some_payment_status.delay(str(user))

    async def disconnect(self, event):
        url = self.scope['query_string'].decode()
        user_id = url.split('=')[1]
        user = await self.get_user(user_id)
        delete_from_redis('payment_connections', str(user.email))

    async def send_payment_status(self, event):
        message = event["message"]

        await self.send(
            text_data=message
        )
