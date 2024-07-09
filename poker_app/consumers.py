from channels.generic.websocket import AsyncWebsocketConsumer
import json
from django.core.cache import cache
import poker_app.pypokergui.server.game_manager as GM
import poker_app.pypokergui.server.message_manager as MM

global_game_manager = GM.GameManager()
MODE_SPEED = "moderate"


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
            elif message_type == 'action_start_game':
                if global_game_manager.is_playing_poker:
                    MM.alert_server_restart(self, self.uuid, self.sockets)
                else:
                    
                    global_game_manager.start_game()
                    MM.broadcast_start_game(self, global_game_manager, self.sockets)
                    MM.broadcast_update_game(self, global_game_manager, self.sockets, MODE_SPEED)
                    if self._is_next_player_ai(global_game_manager):
                        self._progress_the_game_till_human()
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
        registered = global_game_manager.get_human_player_info(self.scope['user'].id)
        return {
            'message_type': 'config_update',
            'html': self.render_string("game_config.html", config=global_game_manager, registered=registered),
            'registered': registered
        }

    def _is_next_player_ai(self, game_manager):
        # Placeholder method to check if the next player is an AI
        return False

    def _progress_the_game_till_human(self):
        # Placeholder method to progress the game until a human player's turn
        pass
