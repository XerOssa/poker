import random
from poker_app.pypokergui.players import BasePokerPlayer
# PyPokerEngine-master\pokerAI.\Lib.\site-packages.\
class RandomPlayer(BasePokerPlayer):  # Do not forget to make parent class as "BasePokerPlayer"

    #  we define the logic to make an action through this method. (so this method would be the core of your AI)
    def declare_action(self, valid_actions, hole_card, round_state):
    # valid_actions format => [raise_action_info, call_action_info, fold_action_info]
        action = random.choice(valid_actions)["action"]
        if action == "raise":
            action_info = next((action_info for action_info in valid_actions if action_info["action"] == "raise"), None)
            if action_info:
                amount = random.randint(action_info["amount"]["min"], action_info["amount"]["max"])
                if amount == -1:
                    action = "call"
        elif action == "call":
            action_info = next((action_info for action_info in valid_actions if action_info["action"] == "call"), None)
            if action_info:
                amount = action_info["amount"]
        elif action == "fold":
            action_info = next((action_info for action_info in valid_actions if action_info["action"] == "fold"), None)
            if action_info:
                amount = action_info["amount"]
        elif action == "check":
            action_info = next((action_info for action_info in valid_actions if action_info["action"] == "check"), None)
            if action_info:
                amount = action_info["amount"]              
        return action, amount 

    def receive_game_start_message(self, game_info):
        pass

    def receive_round_start_message(self, round_count, hole_card, seats):
        pass

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        pass


def setup_ai():
    return RandomPlayer()
