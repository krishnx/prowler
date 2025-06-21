import json
from channels.generic.websocket import AsyncWebsocketConsumer


class ScanStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.scan_id = self.scope['url_route']['kwargs']['scan_id']
        self.group_name = f'scan_status_{self.scan_id}'

        # Join group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # Receive message from group
    async def scan_status_update(self, event):
        status = event['status']
        await self.send(text_data=json.dumps({
            'scan_id': self.scan_id,
            'status': status
        }))
