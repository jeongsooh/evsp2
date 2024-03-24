import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
import json
import jwt

from user.models import User

class OcppConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_greoup_name = f'chat_{self.room_name}'

        await self.channel_layer.group_add(
            self.room_greoup_name,
            self.channel_name
        )

        await self.accept()
    
    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    async def chat_message(self, event):
        message = event['message']

        # call your async task here
        conf = await ocpp_message_handler(message)

        await self.send(
            text_data=json.dumps(
                {'message': conf}
            )
        )

    @database_sync_to_async
    def ocpp_message_handler(message):
        pass


class JwtAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        query_string = scope.get('query_string').decode('utf-8')
        token = [val.split('=')[1]
                 for val in query_string.split('&')
                 if val.startswitch('token=')]
        if token:
            user =await self.get_user_from_token(token[0])
            if user:
                scope['user'] = user
        return await super().__call__(scope, receive, send)
    
    @database_sync_to_async
    def get_user_from_token(self, token):
        try:
            payload = jwt.decode(token, "SECRET_KEY")
            user = User.objects.get(username=payload['username'])
            return user
        except Exception as e:
            return None