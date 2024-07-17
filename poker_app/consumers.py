from channels.generic.websocket import AsyncWebsocketConsumer
import json
import uuid
import logging
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
                    form_data = js.get('form_data', {})
                    default_config = self.get_default_config()
                    game_config = setup_game_config(form_data, default_config)
                    self.scope["session"]["game_config"] = game_config

                self.setup_config(game_config)
                
                human_player = self.scope["session"].get("human_player")
                ai_players = game_config['ai_players']

                members_info = []
                for ai_player in ai_players:
                    members_info.append({
                        "type": 'ai',
                        "name": ai_player['name'],
                        "uuid": ai_player.get('uuid', str(uuid.uuid4())),  # Ensure a unique identifier
                        "path": ai_player['path'],
                    })
                if human_player:
                    members_info.append({
                        "type": 'human',
                        "name": human_player['name'],
                        "uuid": str(uuid.uuid4()),  # Ensure a unique identifier
                    })

                global_game_manager.members_info = members_info  # Assign members_info
                
                # Start the game and broadcast to clients
                global_game_manager.start_game()
                await self.broadcast_start_game(global_game_manager, self.scope["session"].get("sockets", []))

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
        except KeyError as e:
            print(f"KeyError accessing message type: {e}")

    async def broadcast_start_game(self, game_manager, sockets):
        # Broadcast message to browser via sockets
        for soc in sockets:
            try:
                message = MM._gen_start_game_message(self, game_manager, soc.uuid)
                await soc.send(text_data=json.dumps(message))
            except:
                logging.error("Error sending message", exc_info=True)
        
        # Generate game information for AI players
        game_info = MM._gen_game_info(game_manager)
        
        # Broadcast message to AI by invoking the proper callback method
        for uuid, player in game_manager.ai_players.items():
            player.receive_game_start_message(game_info)
            player.set_uuid(uuid)

    def get_default_config(self):
        return {
            'initial_stack': 100,
            'small_blind': 1,
            'ante': 0,
            'max_round': 10,
            'ai_players': [],
        }

    def setup_config(self, game_config):
        global_game_manager.rule = {
            'initial_stack': game_config['initial_stack'],
            'small_blind': game_config['small_blind'],
            'ante': game_config['ante'],
            'max_round': game_config['max_round']
        }

        for ai_player in game_config['ai_players']:
            if 'uuid' not in ai_player:
                ai_player['uuid'] = str(uuid.uuid4())  # Generate a new UUID if missing
        global_game_manager.is_playing_poker = False


def setup_game_config(form_data, default_config):
    game_config = {
        'max_round': 10,
        'initial_stack': form_data.get('initial_stack', default_config['initial_stack']),
        'small_blind': form_data.get('small_blind', default_config['small_blind']),
        'ante': form_data.get('ante', default_config['ante']),
        'ai_players': form_data.get('ai_players', default_config['ai_players'])
    }

    return game_config