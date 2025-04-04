import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from privilege_escalation_tool import routing  # Make sure this import is correct

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'privilege_escalation_tool.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    # Add other protocol routing as needed, for example:
    # "websocket": URLRouter(routing.websocket_urlpatterns),
})
