import json
from channels.generic.websocket import AsyncWebsocketConsumer

class DashboardConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()  # Accept the WebSocket connection
        await self.channel_layer.group_add("dashboard", self.channel_name)  # Add to the "dashboard" group

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("dashboard", self.channel_name)  # Remove from the "dashboard" group

    async def send_update(self, event):
        message = event['message']  # Get the message from the event
        await self.send(text_data=json.dumps({  # Send the message to the client
            'message': message
        }))
