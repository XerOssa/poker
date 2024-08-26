import random
from poker_app.pypokergui.players import BasePokerPlayer
# PyPokerEngine-master\pokerAI.\Lib.\site-packages.\
class RandomPlayer(BasePokerPlayer):  # Do not forget to make parent class as "BasePokerPlayer"

    #  we define the logic to make an action through this method. (so this method would be the core of your AI)
    def declare_action(self, valid_actions, hole_card, round_state):
        last_raise_amount = 0

        # Find the last raise amount if available
        if len(valid_actions) > 2:  # Ensure that raise action info is available
            raise_action_info = valid_actions[2]
            if isinstance(raise_action_info["amount"], dict):
                last_raise_amount = raise_action_info["amount"].get("max", 0)

        # Determine the action to take
        action = random.choice(valid_actions)["action"]

        if action == "raise":
            # Set the maximum raise amount to 2x the last raise amount
            max_raise_amount = 2 * last_raise_amount
            action_info = valid_actions[2]
            min_amount = action_info["amount"]["min"]
            max_amount = min(action_info["amount"]["max"], max_raise_amount)
            
            # Ensure min_amount is not greater than max_amount
            if min_amount > max_amount:
                min_amount, max_amount = max_amount, min_amount
            amount = random.randint(min_amount, max_amount) if min_amount <= max_amount else min_amount
        if action == "call":
            action_info = valid_actions[1]
            amount = action_info["amount"]
        if action == "fold":
            action_info = valid_actions[0]
            amount = action_info["amount"]
        return action, amount   # action returned here is sent to the poker engine

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
