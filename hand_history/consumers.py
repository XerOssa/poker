import json
from channels.generic.websocket import AsyncWebsocketConsumer

class PokerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = 'poker_room'
        self.room_group_name = 'poker'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json['message_type']

        if message_type == 'register_player':
            await self.register_player(text_data_json)
        elif message_type == 'start_game':
            await self.start_game(text_data_json)
        elif message_type == 'update_game':
            await self.update_game(text_data_json)

    async def register_player(self, data):
        # Implement registration logic
        pass

    async def start_game(self, data):
        # Implement game start logic
        pass

    async def update_game(self, data):
        # Implement game update logic
        pass

    async def send_to_group(self, message):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    async def chat_message(self, event):
        message = event['message']

        await self.send(text_data=json.dumps({
            'message': message
        }))
