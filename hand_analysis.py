import glob
import re
import csv

class Hand:
    def __init__(self, hand_text):
        self.hand_text = hand_text
        self.small_blind = self.extract_small_blind()
        self.big_blind = self.extract_big_blind()
        self.hole_cards = self.extract_hole_cards()
        self.preflop_action = self.extract_action()
        self.flop_action = self.extract_action()
        self.turn_action = self.extract_action()
        self.river_action = self.extract_action()
        self.showdown_result = self.extract_showdown()
        self.total_pot, self.rake = self.extract_summary()
        self.position = self.extract_position()

    def extract_small_blind(self):
        pay_sb = re.search(r'Hero: posts small blind \$(\d+\.\d+)', self.hand_text)
        return pay_sb.group(1) if pay_sb else '0.00'

    def extract_big_blind(self):
        pay_bb = re.search(r'Hero: posts big blind \$(\d+\.\d+)', self.hand_text)
        return pay_bb.group(1) if pay_bb else '0.00'

    def extract_hole_cards(self):
        pattern = r'Dealt to Hero \[(\w{2}) (\w{2})\]'
        my_cards = re.search(pattern, self.hand_text)
        return f"{my_cards.group(1)} {my_cards.group(2)}" if my_cards else None

    def extract_action(self):
        text = self.hand_text

        if text:
            if re.search(r'Hero: folds', text):
                return 'F', '0.00'
            for action in ['calls', 'checks', 'bets', 'raises']:
                match = re.search(f'Hero: {action} \\$(\\d+\\.\\d+)', text)
                if match:
                    return action[0].upper(), match.group(1)
        return '', '0.00'

    def extract_showdown(self):
        win_pot_match = re.search(r'Hero collected \$(\d+\.\d+)', self.hand_text)
        return win_pot_match.group(1) if win_pot_match else '0.00'

    def extract_summary(self):
        total_pot_value = '0.00'
        total_pot_match = re.search(r'Total pot \$(\d+\.\d+)', self.hand_text)
        total_pot_value = total_pot_match.group(1) if total_pot_match else total_pot_value

        rake_match = re.search(r'Rake \$(\d+\.\d+)', self.hand_text)
        rake_value = rake_match.group(1) if rake_match else '0.00'
        
        return total_pot_value, rake_value

    def extract_position(self):
        position_start = self.hand_text.find('Table')
        position_end = self.hand_text.find('*** HOLE CARDS ***')
        position_text = self.hand_text[position_start:position_end]

        if position_text:
            seat_button_match = re.search(r'Seat #(\d+) is the button', position_text)
            seat_button = int(seat_button_match.group(1)) if seat_button_match else None
            
            seat_hero_match = re.search(r'Seat (\d+): Hero', position_text)
            seat_hero = int(seat_hero_match.group(1)) if seat_hero_match else None

            if seat_button and seat_hero:
                members = len(re.findall(r'Seat \d+:', position_text))
                if seat_button == seat_hero:
                    return 'BTN'
                if members == 4:
                    return 'CO' if seat_hero == (seat_button - 1) % members else 'SB'
                if members == 5:
                    return 'MP' if seat_hero == (seat_button - 2) % members else 'CO'
                if members > 5:
                    return 'UTG' if seat_hero == (seat_button - 3) % members else 'MP'
        return None

    def line(self):
        move_pre, _ = self.extract_action('HOLE CARDS')
        move_flop, _ = self.extract_action('FLOP')
        move_turn, _ = self.extract_action('TURN')
        move_river, _ = self.extract_action('RIVER')
        return move_pre + move_flop + move_turn + move_river

    def pay_money(self):
        pay_preflop = float(self.preflop_action[1])
        pay_flop = float(self.flop_action[1])
        pay_turn = float(self.turn_action[1])
        pay_river = float(self.river_action[1])
        return [pay_preflop, pay_flop, pay_turn, pay_river]


def process_poker_hand(FILES_PATH: str) -> list:
    PREFIX = 'Poker Hand #HD'
    hh_files = glob.glob(FILES_PATH)
    all_hands = []
    for file in hh_files:
        with open(file, 'r') as f:
            text = f.read()
            hands_text = re.findall(fr'{PREFIX}.+?(?={PREFIX}|\Z)', text, re.DOTALL)
            for hand_text in hands_text:
                hand = from_text(hand_text)
                all_hands.append(hand)
    return all_hands


def from_text(text: str) -> Hand:
    return Hand(text)  # Przekazujemy tekst do klasy Hand


def save_to_csv(hands: list):
    filename = './poker_hand.csv'
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['Hand_ID', 'stakes', 'date', 'win_loss']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for hand in hands:
            # Upewnij się, że dodasz odpowiednie atrybuty w klasie Hand
            writer.writerow({'Hand_ID': hand.hand_text, 'stakes': hand.big_blind, 'date': '', 'win_loss': hand.showdown_result})



hand_text = """
Poker Hand #HD1136287140: Hold'em No Limit  ($0.02/$0.05) - 2023/02/25 22:20:13
Table 'NLHBlue6' 6-max Seat #1 is the button
Seat 1: Hero ($6.51 in chips)
Seat 2: cc8457ef ($5.31 in chips)
Seat 3: 6d5f222 ($5.78 in chips)
Seat 4: beec2bb ($5 in chips)
Seat 5: 14e91709 ($4.54 in chips)
Seat 6: 24cd3922 ($9.54 in chips)
cc8457ef: posts small blind $0.02
6d5f222: posts big blind $0.05
*** HOLE CARDS ***
Dealt to Hero [6s 6h]
Dealt to cc8457ef 
Dealt to 6d5f222 
Dealt to beec2bb 
Dealt to 14e91709 
Dealt to 24cd3922 
beec2bb: folds
14e91709: folds
24cd3922: folds
Hero: raises $0.05 to $0.1
cc8457ef: folds
6d5f222: folds
Uncalled bet ($0.05) returned to Hero
*** SHOWDOWN ***
Hero collected $0.12 from pot
*** SUMMARY ***
Total pot $0.12 | Rake $0 | Jackpot $0 | Bingo $0 | Fortune $0
Seat 1: Hero (button) collected ($0.12)
Seat 2: cc8457ef (small blind) folded before Flop
Seat 3: 6d5f222 (big blind) folded before Flop
Seat 4: beec2bb folded before Flop (didn't bet)
Seat 5: 14e91709 folded before Flop (didn't bet)
Seat 6: 24cd3922 folded before Flop (didn't bet)
"""
hand = Hand(hand_text)

print(f"Small Blind: {hand.small_blind}")
print(f"Big Blind: {hand.big_blind}")
print(f"Hole Cards: {hand.hole_cards}")
print(f"Preflop Action: {hand.preflop_action}")
print(f"Flop Action: {hand.flop_action}")
print(f"Turn Action: {hand.turn_action}")
print(f"River Action: {hand.river_action}")
print(f"Showdown Result: {hand.showdown_result}")
print(f"Total Pot: {hand.total_pot}")
print(f"Rake: {hand.rake}")
print(f"Position: {hand.position}")