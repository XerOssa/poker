from channels.generic.websocket import AsyncWebsocketConsumer
import json
import uuid
from django.core.cache import cache
import poker_app.pypokergui.server.game_manager as GM
import poker_app.pypokergui.server.message_manager as MM
import poker_app.pypokergui.ai_generator as AG
# from poker_app.pypokergui.server.poker import setup_config

global_game_manager = GM.GameManager()
MODE_SPEED = "moderate"

class PokerConsumer(AsyncWebsocketConsumer):
    async def receive(self, text_data):
        try:
            js = json.loads(text_data)
            message_type = js.get('type')

            if message_type == 'action_start_game':
                game_config = self.scope["session"].get("game_config")
                if not game_config:
                    # Set up game config if not already set
                    form_data = js.get('form_data', {})
                    default_config = self.get_default_config()
                    game_config = setup_game_config(form_data, default_config)
                    self.scope["session"]["game_config"] = game_config

                print(f"Game config found: {game_config}")  # Debugging
                self.setup_config(game_config)
                global_game_manager.start_game()
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
        except KeyError as e:
            print(f"KeyError accessing message type: {e}")

    def get_default_config(self):
        return {
            'initial_stack': 100,
            'small_blind': 1,
            'ante': 0,
            'max_round': 10,
            'ai_players': [],
            # 'blind_structure': None
        }

    def setup_config(self, game_config):
        required_keys = ['initial_stack', 'small_blind', 'ante', 'max_round', 'ai_players']
        for key in required_keys:
            assert key in game_config, f"{key} missing in game config"

        global_game_manager.rule = {
            'initial_stack': game_config['initial_stack'],
            'small_blind': game_config['small_blind'],
            'ante': game_config['ante'],
            'max_round': game_config['max_round']
        }

        human_players = self.scope["session"].get("human_players", [])
        
        # Debugging: Print human players and AI players to check their contents
        print(f"Human players: {human_players}")
        print(f"AI players: {game_config['ai_players']}")

        # Validate AI players
        for ai_player in game_config['ai_players']:
            if 'uuid' not in ai_player:
                # print(f"Missing 'uuid' in AI player: {ai_player}")
                ai_player['uuid'] = str(uuid.uuid4())  # Generate a new UUID if missing

        global_game_manager.members_info = game_config['ai_players'] + human_players

        # Debugging: Print members_info to check for missing 'uuid' keys
        print(f"Members info: {global_game_manager.members_info}")

        # Proceed with creating uuid_list
        uuid_list = [member["uuid"] for member in global_game_manager.members_info]
        # print(f"UUID list: {uuid_list}")

        global_game_manager.is_playing_poker = False

        print("Configuration completed")  # Debugging


def setup_game_config(form_data, default_config):
    game_config = {
        'max_round': 10,
        'initial_stack': form_data.get('initial_stack', default_config['initial_stack']),
        'small_blind': form_data.get('small_blind', default_config['small_blind']),
        'ante': form_data.get('ante', default_config['ante']),
        # 'blind_structure': form_data.get('blind_structure', default_config.get('blind_structure')),
        'ai_players': form_data.get('ai_players', default_config['ai_players'])
    }


    print(f"Setup game config: {game_config}")  # Debugging
    return game_config