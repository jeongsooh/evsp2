import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import json

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
        await ocpp_message_handler(message)

        await self.send(
            text_data=json.dumps(
                {'message': message}
            )
        )

@database_sync_to_async
def ocpp_message_handler(message):
    pass
