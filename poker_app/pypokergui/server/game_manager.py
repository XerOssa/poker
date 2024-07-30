import poker_app.pypokergui.engine_wrapper as Engine
import poker_app.pypokergui.ai_generator as AG

class GameManager:


    def __init__(self):
        self.config = {}
        self.rule = None
        self.members_info = []
        self.engine = None
        self.ai_players = {}
        self.is_playing_poker = False
        self.latest_messages = []
        self.next_player_uuid = None


    def define_rule(self, initial_stack, small_blind, ante):
        self.rule = Engine.gen_game_config(initial_stack, small_blind, ante)


    def join_ai_player(self, name, path):
        ai_uuid = str(len(self.members_info))
        self.members_info.append(gen_ai_player_info(name, ai_uuid, path))


    def join_human_player(self, name):
        uuid = str(len(self.members_info))
        self.members_info.append(gen_human_player_info(name, uuid))


    def get_human_player_info(self, uuid):
        for info in self.members_info:
            if info["type"] == "human":
                return info


    def remove_human_player_info(self, uuid):
        member_info = self.get_human_player_info(uuid)
        assert member_info
        self.members_info.remove(member_info)


    def start_game(self):
        uuid_list = [member["uuid"] for member in self.members_info]
        name_list = [member["name"] for member in self.members_info]
        players_info = Engine.gen_players_info(uuid_list, name_list)  
        self.ai_players = build_ai_players(self.members_info)
        self.engine = Engine.EngineWrapper()

        self.latest_messages = self.engine.start_game(players_info, self.rule)

        self.is_playing_poker = True
        self.next_player_uuid = fetch_next_player_uuid(self.latest_messages)

        return self.latest_messages


    def get_next_player(self):
        next_player_pos = self.current_state["next_player"]
        return self.current_state["table"].seats.players[next_player_pos]

    def update_game(self, action, amount):
        assert len(self.latest_messages) != 0  # check that start_game has already called
        self.latest_messages = self.engine.update_game(action, amount)
        self.next_player_uuid = fetch_next_player_uuid(self.latest_messages)


    def ask_action_to_ai_player(self, uuid):
        if uuid != '5':
            ai_player = self.ai_players[uuid]
        ask_uuid, ask_message = self.latest_messages[-1]
        assert ask_message['type'] == 'ask' and uuid == ask_uuid
        return ai_player.declare_action(
            ask_message['message']['valid_actions'],
            ask_message['message']['hole_card'],
            ask_message['message']['round_state']
        )
    

    def configure_game(self, config):
        self.config = config


def fetch_next_player_uuid(new_messages):
    if not has_game_finished(new_messages):
        ask_uuid, ask_message = new_messages[-1]
        assert ask_message['type'] == 'ask'
        print(f"DEBUG: Fetching next player UUID: {ask_uuid}")  # Dodano logowanie
        return ask_uuid
    else:
        print("DEBUG: Game has finished")  # Dodano logowanie
        return None


def has_game_finished(new_messages):
    last_message = new_messages[-1]
    return "game_result_message" == last_message[1]['message']['message_type']


def build_ai_players(members_info):
    holder = {}
    for member in members_info:
        if member["type"] == "human":
            continue
        holder[member["uuid"]] = _build_ai_player(member["path"])
    return holder


def _build_ai_player(path):
    if not AG.healthcheck(path, quiet=True):
        raise Exception("Failed to setup AI from [ %s ]" % path)
    setup_method = AG._import_setup_method(path)
    return setup_method()


def gen_ai_player_info(name, uuid, path):
    info = _gen_base_player_info("ai", name, uuid)
    info["path"] = path
    return info


def gen_human_player_info(name, uuid):
    return _gen_base_player_info("human", name, uuid)


def _gen_base_player_info(player_type, name, uuid):
    return {
        "type": player_type,
        "name": name,
        "uuid": uuid
    }
