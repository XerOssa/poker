import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.generic.websocket import WebsocketConsumer
from .models import GameState
from asgiref.sync import sync_to_async

class PokerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("poker", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("poker", self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data['type'] == 'update_round_count':
            game_state = await sync_to_async(GameState.objects.get)(id=1)
            game_state.round_count += 1
            await sync_to_async(game_state.save)()
            await self.channel_layer.group_send("poker", {
                'type': 'round_count_update',
                'round_count': game_state.round_count
            })
    async def round_count_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'round_count',
            'round_count': event['round_count']
        }))

class PokerConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message
        }))