import asyncio
import json
import logging
import poker_app.pypokergui.server.game_manager as GM
import poker_app.pypokergui.utils.action_utils as AU
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.cache import cache
from poker_app.utils import _gen_game_update_message, _gen_start_game_message

# from poker_app.pypokergui.server.poker import setup_config

global_game_manager = GM.GameManager()
MODE_SPEED = "moderate"

class PokerConsumer(AsyncWebsocketConsumer):

    sockets = set()
    async def connect(self):
        await self.accept()
        if "sockets" not in self.scope["session"]:
            self.scope["session"]["sockets"] = []
            
            self.uuid = str(5)
        self.scope["session"]["sockets"].append(self)

    async def receive(self, text_data):

        js = json.loads(text_data)
        message_type = js.get('type')

        if message_type == 'action_start_game':
            game_config_ai = self.scope["session"].get("game_config")

            form_data = js.get('form_data', {})
            default_config = self.get_default_config()
            game_config = setup_game_config(form_data, default_config)
            self.scope["session"]["game_config"] = game_config


            members_info = setup_config_player(game_config_ai)
            self.scope["session"]["members_info"] = members_info
            human_player = self.scope["session"].get("human_player")
            if human_player:
                uuid_human = str(len(members_info))
                members_info.append({
                    "type": 'human',
                    "name": human_player['name'],
                    "uuid": uuid_human,
                })
                self.scope["session"]["members_info"] = members_info

            global_game_manager.members_info = members_info  # Assign members_info

            # Start the game and broadcast to clients
            result_message = global_game_manager.start_game()  # Zmienna do przechowywania wyniku
            # await self.broadcast_start_game(global_game_manager, self.scope["session"].get("sockets", []))
            if _is_next_player_ai(global_game_manager):
                await self._progress_the_game_till_human(global_game_manager)
            
        elif message_type == 'action_declare_action':
            if self.uuid == global_game_manager.next_player_uuid:
                action, amount = self._correct_action(js)
                global_game_manager.update_game(action, amount)
                await self.broadcast_update_game(global_game_manager, self.scope["session"]["sockets"], MODE_SPEED)
                if _is_next_player_ai(global_game_manager):
                    await self._progress_the_game_till_human(global_game_manager)

    
    # async def broadcast_start_game(self, game_manager, sockets):
    #     for soc in sockets:
    #         message = _gen_start_game_message(game_manager)
    #         await soc.send(text_data=json.dumps(message))
    #     game_info = _gen_game_info(game_manager)
        
    #     for uuid, player in game_manager.ai_players.items():
    #         player.receive_game_start_message(game_info)
    #         player.set_uuid(uuid)


    async def broadcast_update_game(self, game_manager, sockets, mode="moderate"):
        if not sockets:
            logging.error("Sockets list is None or empty")
            return

        for destination, update in game_manager.latest_messages:
            for uuid in _parse_destination(destination, game_manager, sockets):
                if uuid != '5':
                    ai_player = game_manager.ai_players.get(uuid)
                    if ai_player is not None:
                        _broadcast_message_to_ai(ai_player, update)
                else:
                    human_player = game_manager.get_human_player_info(uuid)
                    if human_player is not None:
                        socket = _find_socket_by_uuid(sockets, uuid)
                        if socket is not None:
                            message = _gen_game_update_message(update)

                            try:
                                await socket.send(text_data=json.dumps(message))
                            except Exception as e:
                                logging.error("Error sending message", exc_info=True)
                            await asyncio.sleep(_calc_wait_interval(mode, update))


    async def _progress_the_game_till_human(self, game_manager):
        while _is_next_player_ai(game_manager):
            if GM.has_game_finished(game_manager.latest_messages):
                break
            action_and_amount = game_manager.ask_action_to_ai_player(game_manager.next_player_uuid)
            if action_and_amount is not None:
                action, amount = action_and_amount[:2]
                game_manager.update_game(action, amount)
            await self.broadcast_update_game(game_manager, self.scope["session"]["sockets"], MODE_SPEED)


    def get_default_config(self):
        return {
            'initial_stack': 100,
            'small_blind': 1,
            'ante': 0,
            'ai_players': [],
        }


    def _correct_action(self, data):
        try:
            data["amount"] = int(data["amount"])
            # print(data["amount"])
        except:
            data["amount"] = -1     
        
        players = global_game_manager.engine.current_state["table"].seats.players
        next_player_pos = global_game_manager.engine.current_state["next_player"]
        sb_amount = global_game_manager.engine.current_state["small_blind_amount"]
        actions = AU.generate_legal_actions(players, next_player_pos, sb_amount)

        if data["action"] == "fold":
            data["amount"] = 0
        elif data["action"] == "call":
            data["amount"] = actions[1]["amount"]
        elif data["action"] == "check":
            # Jeśli gracz decyduje się na check i nie było żadnego podbicia, pozwól mu zachować swoją rękę
            data["amount"] = 0
        else:
            legal = actions[2]["amount"]
            if legal["min"] <= data["amount"] <= legal["max"]:
                data["amount"] = data["amount"]
            else:
                data["action"] = "fold"
                data["amount"] = 0
        return data["action"], data["amount"]
    

def setup_game_config(form_data, default_config):
    game_config = {
        'initial_stack': form_data.get('initial_stack', default_config['initial_stack']),
        'small_blind': form_data.get('small_blind', default_config['small_blind']),
        'ante': form_data.get('ante', default_config['ante']),
    }
    global_game_manager.define_rule(
            game_config['initial_stack'], 
            game_config['small_blind'],
            game_config['ante'], 
    )
    return game_config


def setup_config_player(game_config_ai):
    members_info = []
    for ai_player in game_config_ai['ai_players']:
        global_game_manager.join_ai_player(ai_player['name'], ai_player['path'])
        player_info = gen_ai_player_info(ai_player['name'], str(len(members_info)), ai_player['path'])
        members_info.append(player_info)
    return members_info


def _is_next_player_ai(game_manager):
    uuid = game_manager.next_player_uuid
    return uuid and len(uuid) <= 2 and uuid != '5'


def gen_ai_player_info(name, uuid, path):
    info = _gen_base_player_info("ai", name, uuid)
    info["path"] = path
    return info


def _gen_base_player_info(player_type, name, uuid):
    return {
        "type": player_type,
        "name": name,
        "uuid": uuid
    }



def _gen_game_info(game_manager):
    seats = game_manager.latest_messages[0][1]["message"]["seats"]
    copy_seats = [{k:v for k,v in player.items()} for player in seats]
    for player in copy_seats:
        player["stack"] = game_manager.rule["initial_stack"]
    player_num = len(seats)
    rule = {k:v for k,v in game_manager.rule.items()}
    rule["small_blind_amount"] = rule.pop("small_blind")
    return {
            "seats": copy_seats,
            "player_num": player_num,
            "rule": rule,
            }

def _calc_wait_interval(mode, update):
    message_type = update["message"]["message_type"]
    if 'dev' == mode:
        return 0
    elif 'slow' == mode:
        return SLOW_WAIT_INTERVAL[message_type]
    elif 'moderate' == mode:
        return MODERATE_WAIT_INTERVAL[message_type]
    elif 'fast' == mode:
        return FAST_WAIT_INTERVAL[message_type]
    else:
        raise Exception("Unexpected mode received [ %s ]" % mode)

SLOW_WAIT_INTERVAL = {  # TODO
        'round_start_message': 0,
        'street_start_message': 0,
        'ask_message': 0,
        'game_update_message': 0,
        'round_result_message': 5,
        'game_result_message': 0
}

MODERATE_WAIT_INTERVAL = {
        'round_start_message': 1,
        'street_start_message': 1,
        'ask_message': 0,
        'game_update_message': 1,
        'round_result_message': 5,
        'game_result_message': 0
}

FAST_WAIT_INTERVAL = {
        'round_start_message': 1,
        'street_start_message': 0.5,
        'ask_message': 0,
        'game_update_message': 0.5,
        'round_result_message': 5,
        'game_result_message': 0
}

def _find_socket_by_uuid(sockets, uuid):
    target = [sock for sock in sockets if sock.uuid == uuid]
    return target[0] if target else None

def _parse_destination(destination, game_manager, sockets):
    if destination == -1:
        return [soc.uuid for soc in sockets] + list(game_manager.ai_players.keys())
    else:
        return [destination]
    
def _broadcast_message_to_ai(ai_player, message):
    message_type = message['message']['message_type']
    if 'round_start_message' == message_type:
        round_count = message['message']['round_count']
        hole_card = message['message']['hole_card']
        seats = message['message']['seats']
        ai_player.receive_round_start_message(round_count, hole_card, seats)
    elif 'street_start_message' == message_type:
        street = message['message']['street']
        round_state = message['message']['round_state']
        ai_player.receive_street_start_message(street, round_state)
    elif 'game_update_message' == message_type:
        action = message['message']['action']
        round_state = message['message']['round_state']
        ai_player.receive_game_update_message(action, round_state)
    elif 'round_result_message' == message_type:
        winners = message['message']['winners']
        round_state = message['message']['round_state']
        hand_info = message['message']['hand_info']
        ai_player.receive_round_result_message(winners, hand_info, round_state)
    elif 'game_result_message' == message_type:
        pass  # ai does not handle game result
    elif 'ask_message' == message_type:
        pass  # ask message handling is done in global_game_config.ask_action_to_ai
    else:
        raise Exception("Unexpected message received : %r" % message)