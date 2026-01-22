"routing module"

from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(  # type: ignore
        route=r"ws/chat/(?:(?P<session_id>[^/]+)/)?",
        view=consumers.ChatConsumer.as_asgi(),  # type: ignore
    ),
]
