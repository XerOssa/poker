import random
import joblib
from poker_app.pypokergui.engine.card import get_range, is_in_range, percentage_table
from poker_app.pypokergui.players import BasePokerPlayer, get_player_position

class Tag(BasePokerPlayer):
    # def __init__(self):
        # super().__init__()
        # # Wczytaj model
        # self.model = joblib.load("poker_ai_model.pkl")
    # def declare_action(self, valid_actions, hole_card, round_state):
    #     # Przetwarzanie danych wejściowych na odpowiedni format
    #     features = [hole_card, round_state, self.get_stack(), self.get_opponent_last_action()]
        
    #     # Przewidywanie akcji
    #     predicted_action = self.model.predict([features])[0]
        
    #     # Przetwarzanie wyjścia na odpowiednią akcję
    #     action_info = next((action for action in valid_actions if action['action'] == predicted_action), None)
        
    #     # Wartość zakładu, jeśli jest potrzebna
    #     amount = action_info["amount"] if action_info and "amount" in action_info else 0
        
    #     print("Fish zagrał:", predicted_action, amount)
    #     return predicted_action, amount

    # def get_stack(self):
    #     # Metoda do pobrania stanu stacka gracza
    #     return self.round_state['seats'][self.seat_position]['stack']
    
    # def get_opponent_last_action(self):
    #     # Metoda do pobrania ostatniej akcji przeciwnika
    #     return self.round_state['action_histories']['preflop'][-1]['action']
    def declare_action(self, valid_actions, hole_card, round_state):
        player_index = next((i for i, seat in enumerate(round_state["seats"]) if seat['name'] == "Tag"), None)
        seats = round_state["seats"]
        dealer_pos = round_state["dealer_btn"]
        sb_pos = round_state["small_blind_pos"]
        bb_pos = round_state["big_blind_pos"]
        seat_count = len(seats)
        
        position = get_player_position(player_index, dealer_pos, sb_pos, bb_pos, seat_count)
        
        preflop_range = get_range(position)
        last_raise_amount = 0
        paid_amount = 0

        raise_action_info = valid_actions[2]
        if isinstance(raise_action_info["amount"], dict):
            last_raise_amount = raise_action_info["amount"].get("max", 0)

        action = random.choice(valid_actions)["action"]

        has_raise_action = any(old_action['action'] == 'RAISE' for old_action in round_state['action_histories']['preflop'])
        
        for last_action in round_state['action_histories']['preflop']:
            if last_action['uuid'] == self.uuid:
                paid_amount = last_action.get('amount', 0)
                break
        
        if not has_raise_action and round_state['street'] == "preflop":
            if is_in_range(hole_card, preflop_range):
                action = "raise"
        else:
            action = "fold"

        if action == "raise":
            max_raise_amount = 2 * last_raise_amount
            action_info = next((old_action for old_action in valid_actions if old_action["action"] == "raise"), None)
            min_amount = action_info["amount"]["min"]
            max_amount = min(action_info["amount"]["max"], max_raise_amount)

            max_amount = max(0, max_amount - paid_amount)
            min_amount = max(0, min_amount - paid_amount)

            if min_amount > max_amount:
                min_amount, max_amount = max_amount, min_amount
            amount = min_amount
        elif action == "call":
            action_info = next((action_info for action_info in valid_actions if action_info["action"] == "call"), None)
            amount = action_info["amount"] if action_info else 0
        elif action == "fold":
            action_info = next((action_info for action_info in valid_actions if action_info["action"] == "fold"), None)
            amount = action_info["amount"] if action_info else 0
        elif action == "check":
            action_info = next((action_info for action_info in valid_actions if action_info["action"] == "check"), None)
            amount = action_info["amount"] if action_info else 0
        elif action == "all_in":
            action_info = next((action_info for action_info in valid_actions if action_info["action"] == "all_in"), None)
            amount = action_info["amount"] if action_info else 0

        print("Tag zagrał:", action, amount)
        return action, amount



    def receive_game_start_message(self, game_info):
        pass

    def receive_round_start_message(self, round_state, round_count, hole_card, seats):
        pass

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners,  round_state):
        pass


def setup_ai():
    return Tag()
