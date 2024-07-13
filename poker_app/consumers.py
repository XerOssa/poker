from channels.generic.websocket import AsyncWebsocketConsumer
import json
from django.core.cache import cache
import poker_app.pypokergui.server.game_manager as GM
import poker_app.pypokergui.server.message_manager as MM
# from poker_app.pypokergui.server.poker import setup_config

global_game_manager = GM.GameManager()
MODE_SPEED = "moderate"

class PokerConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'poker_group'
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
                    game_config = self.scope["session"].get("game_config")
                    if game_config:
                        print(f"Game config found: {game_config}")  # Debugging
                        self.setup_config(game_config)
                        print("Setup config executed")  # Debugging
                        global_game_manager.start_game()
                        print("Game started")  # Debugging
                        MM.broadcast_start_game(self, global_game_manager, self.sockets)
                        MM.broadcast_update_game(self, global_game_manager, self.sockets, MODE_SPEED)
                        if self._is_next_player_ai(global_game_manager):
                            self._progress_the_game_till_human()
                    else:
                        print("Game configuration not found in session.")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
        except KeyError as e:
            print(f"KeyError accessing message type: {e}")

    async def join_human_player(self, name):
        global_game_manager.join_human_player(name)

    def setup_config(self, game_config):
        assert 'initial_stack' in game_config, "Initial stack missing in game config"
        assert 'small_blind' in game_config, "Small blind missing in game config"
        assert 'ante' in game_config, "Ante missing in game config"
        assert 'max_round' in game_config, "Max round missing in game config"
        assert 'ai_players' in game_config, "AI players missing in game config"

        global_game_manager.rule = {
            'initial_stack': game_config['initial_stack'],
            'small_blind': game_config['small_blind'],
            'ante': game_config['ante'],
            'max_round': game_config['max_round']
        }

        human_players = self.scope["session"].get("human_players", [])
        global_game_manager.members_info = game_config['ai_players'] + human_players

        # Debugging: Print members_info to check for missing 'uuid' keys
        print(f"Members info: {global_game_manager.members_info}")

        # Ensure all members have 'uuid' key, handle missing key
        for member in global_game_manager.members_info:
            if 'uuid' not in member:
                print(f"Missing 'uuid' in member: {member}")
                # Handle the missing 'uuid' case (e.g., assign a default or raise an error)
                member['uuid'] = 'default_uuid'  # Example default value

        # Proceed with creating uuid_list
        uuid_list = [member["uuid"] for member in global_game_manager.members_info]
        print(f"UUID list: {uuid_list}")

        global_game_manager.is_playing_poker = False

        print("Configuration completed")  # Debugging
