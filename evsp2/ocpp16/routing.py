from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/ocpp/', consumers.OcppConsumer.as_asgi()),
]