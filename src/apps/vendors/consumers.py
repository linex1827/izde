import jwt
from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from apps.profiles.models.user import Vendor
from apps.profiles.tasks.broker import send_orders
from apps.vendors.utils import add_to_redis, delete_from_redis
from core.settings.base import SECRET_KEY


class VendorConsumer(AsyncWebsocketConsumer):
    vendor_connections = {}

    @sync_to_async
    def get_user(self, user_id):
        return Vendor.objects.get(id=user_id)

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
            self.vendor_connections[str(user)] = self.channel_name
            add_to_redis('vendor_connections', str(user), self.channel_name)
            send_orders.delay(str(user))
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
        for user_email, channel_name in self.vendor_connections.items():
            if channel_name == self.channel_name:
                delete_from_redis('vendor_connections', user_email)
                token_to_remove.append(user_email)
        del self.vendor_connections[token_to_remove[0]]

    async def send_orders(self, event):
        message = event["message"]

        await self.send(
            text_data=message
        )


class VendorDeleteOrderConsumer(AsyncWebsocketConsumer):
    delete_order_connections = {}

    @sync_to_async
    def get_user(self, user_id):
        return Vendor.objects.get(id=user_id)

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
            self.delete_order_connections[str(user)] = self.channel_name
            add_to_redis('deleted_order_connections', str(user), self.channel_name)
            send_orders.delay(str(user))
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
        for user_email, channel_name in self.delete_order_connections.items():
            if channel_name == self.channel_name:
                delete_from_redis('deleted_order_connections', user_email)
                token_to_remove.append(user_email)
        del self.delete_order_connections[token_to_remove[0]]

    async def send_deleted_order_id(self, event):
        message = event["message"]

        await self.send(
            text_data=message
        )
