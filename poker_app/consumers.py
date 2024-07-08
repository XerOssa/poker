from channels.generic.websocket import AsyncWebsocketConsumer
import json
from django.core.cache import cache
import poker_app.pypokergui.server.game_manager as GM

global_game_manager = GM.GameManager()

class PokerConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        try:
            js = json.loads(text_data)
            message_type = js.get('type')
            
            if message_type == "action_new_member":
                await self.join_human_player(js.get('name'))

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return
        except KeyError as e:
            print(f"KeyError accessing message type: {e}")
            return

    async def join_human_player(self, player_name):
        # Assuming global_game_manager is available
        global_game_manager.join_human_player(player_name, self.scope['user'].id)
        await self.broadcast_config_update()

    async def broadcast_config_update(self):
        # Assuming MM and global_game_manager are available
        for socket in self.scope['group']:
            await self.channel_layer.send(socket, {
                'type': 'config.update',
                'message': self.gen_config_update_message(),
            })

    def gen_config_update_message(self):
        # Generate the config update message
        registered = global_game_manager.get_human_player_info(self.scope['user'].id)
        return {
            'message_type': 'config_update',
            'html': self.render_string("game_config.html", config=global_game_manager, registered=registered),
            'registered': registered
        }
