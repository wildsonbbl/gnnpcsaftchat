"""
ASGI config for gnnpcsaft project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
import sys

from decouple import config
from django.core.asgi import get_asgi_application

from .cpu_compat import show_compatibility_warning, supports_avx2

if not supports_avx2():
    show_compatibility_warning()
    sys.exit(1)

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    str(config("DJANGO_SETTINGS_MODULE", default="app.settings")),
)

# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()

# pylint: disable = C0413,C0411
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

import chat.routing

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(URLRouter(chat.routing.websocket_urlpatterns))
        ),
    }
)
