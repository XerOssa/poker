import random
from poker_app.pypokergui.players import BasePokerPlayer

class Fish(BasePokerPlayer): 


    def declare_action(self, valid_actions, hole_card, round_state):
    # valid_actions format => [raise_action_info, call_action_info, fold_action_info]
        last_raise_amount = 0
        paid_amount = 0
        for action in round_state['action_histories']['preflop']:
            if action['uuid'] == self.uuid:
                paid_amount = action.get('amount', 0)
                break
        if len(valid_actions) > 2:
            raise_action_info = valid_actions[2]
            if isinstance(raise_action_info["amount"], dict):
                last_raise_amount = raise_action_info["amount"].get("max", 0)
        action = random.choice(valid_actions)["action"]
        # action = "fold"
        if action == "raise":
            max_raise_amount = 2 * last_raise_amount
            action_info = valid_actions[2]
            min_amount = action_info["amount"]["min"]
            max_amount = min(action_info["amount"]["max"], max_raise_amount)
            max_amount = max(0, max_amount - paid_amount)
            min_amount = max(0, min_amount - paid_amount)
            if min_amount > max_amount:
                min_amount, max_amount = max_amount, min_amount
            # amount = random.randint(min_amount, max_amount) if min_amount <= max_amount else min_amount
            amount = 2 * min_amount
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
        elif action == "all_in":
            action_info = next((action_info for action_info in valid_actions if action_info["action"] == "all_in"), None)
            if action_info:
                amount = action_info["amount"]
        print("Fish zagrał:", action, amount)
        return action, amount



    def receive_game_start_message(self, game_info):
        pass

    def receive_round_start_message(self,round_state, round_count, hole_card, seats):
        pass

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        pass


def setup_ai():
    return Fish()
