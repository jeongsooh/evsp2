### Referenced from https://python.plainenglish.io/leveraging-websockets-in-django-for-real-time-communication-a5e2b1d2ce36

1. Create Virtual Environment
````
$ python3 -m venv myenv  or
$ virtualenv venv

$ source venv/scripts/activate
````
2. Install Django / install Channels /install Channels-Redis
````
$ pip install django
$ pip install channels
$ pip install channels-redis
````
3. Setting up Redis from official website (https://redis.io/download/)
````
$ redis-cli ping
````
4. Project setup in Django
````
$ django-admin startproject my_project_name
$ cd my_project_name
$ django-admin startapp my_app_name  or
$ python manage.py startapp my_app_name
````
5. Creating a new django project and App
- Register App: Open evsp2/settings.py and add your new app to the INSTALLED_APPS list:
````
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'channels',
]

INSTALLED_APPS += [
    'user',
    'chargerInfo',
    'cardInfo',
]
````
- Set ASGI_APPLICATION: Still in settings.py, you have to point to the routing object in asgi.py by modifying the ASGI_APPLICATION setting:
````
ASGI_APPLICATION = 'evsp2.asgi.application'
````
- Configure Redis
````
CHANNEL_LAYERS = {
    'default':{
        'BACKEND':'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1',6379)],
        },
    },
}

$ python manage.py check
````
6. Routing and Consumers
- Create routing.py: In your app directory, create a new Python file named routing.py
- Import and URL Mapping: Import your consumers and use the websocket_urlpatterns list to specify routing.
`````
from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/ocpp/', consumers.ocppConsumer.as_asgi()),
]
`````
- Update asgi.py: Add your routing.py to the project-level asgi.py
`````
import os

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

import ocpp16.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'evsp2.settings')

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': URLRouter(ocpp16.routing.websocket_urlpatterns)
}) 
`````
7. Create consumer.py and simple WebSocket.js 
`````
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
import json

class OcppConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
    
    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        await self.send(
            text_data=json.dumps(
                {'message': message}
            )
        )
`````
`````
const socket = new WebSocket(
    'ws://127.0.0.1:8000/ws/ocpp/'
);

socket.addEventListener('open', function(event) {
    console.log('Connected to the WebSocket.');
    socket.send('Hello Server!');
});

socket.addEventListener('message', function(event) {
    console.log('Message received: ', event.data);
});

socket.addEventListener('close', function(event) {
    console.log('WebSocket connection closed: ', event.code, event.reason);
});

socket.addEventListener('error', function(event) {
    console.log('WebSocket error: ', event);
});
````` 
8. Building a Chat Application
- models design
`````
from django.db import models

# Create your models here.

class Room(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True) 

class Message(models.Model):
    room = models.ForeignKey(
        Room,
        related_name='messages',
        on_delete=models.CASCADE
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
`````
- basic consumer set up and group management 
`````
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_greoup_name = f'chat_{self.room_name}'

        await self.channel_layer.group_add(
            self.room_greoup_name,
            self.channel_name
        )

        await self.accept()
`````
- sending and receiving messages
`````
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
`````
