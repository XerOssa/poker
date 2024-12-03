import glob
import re
import csv
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from poker_app.pypokergui.engine.card import processed_hand, percentage_table
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
            if re.search(r'Hero: checks', text):
                return 'X', '0.00'
            for action in ['calls', 'bets', 'raises']:
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
        sb_hero = re.search(r'Hero: posts small blind \$(\d+\.\d+)', self.hand_text)
        bb_hero = re.search(r'Hero: posts big blind \$(\d+\.\d+)', self.hand_text)
        if sb_hero:
            return 'SB'
        if bb_hero:
            return 'BB'
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
                    return 'EP' if seat_hero == (seat_button - 3) % members else 'MP'
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
    return Hand(text)


def save_to_csv(hands: list):
    filename = './poker_hand.csv'
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['hole_cards', 'preflop_action', 'position']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for hand in hands:
            # print(hand.hole_cards, hand.preflop_action, hand.position)  
            action, _ = hand.preflop_action
            # print(action)
            # Sprawdzenie, czy pola nie są puste
            if action:
                if hand.hole_cards and action and hand.position:
                # Zmiana formatu kart
                    cards = hand.hole_cards.split()  # Rozdzielenie np. '6d Ac' na ['6d', 'Ac']
                    hole_cards_tuple = tuple(cards)  # Zamiana na ('6d', 'Ac')

                    writer.writerow({
                        'hole_cards': hole_cards_tuple,  # Zapisujemy jako tuple
                        'position': hand.position,
                        'preflop_action': action  # Zapisujemy tylko akcję (np. 'F', 'R')
                    })



position_map = {'EP': 0, 'MP': 1, 'CO': 2, 'BTN': 3, 'SB': 4, 'BB': 5}
action_map = {'F': 0, 'R': 1}

FILES_PATH = 'hh/*.txt'


# def process_hand_cards(hand):
#     # Przykład: 'Ad Kd' -> [14, 13] (A = 14, K = 13)
#     card_values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, 'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
    
#     card1, card2 = hand[0:2], hand[3:5]
#     return [card_values[card1[0]], card_values[card2[0]]]


# Procesowanie plików z rozdaniami pokerowymi i utworzenie obiektów Hand
hands = process_poker_hand(FILES_PATH)

# Zapisanie wyników do pliku CSV
save_to_csv(hands)

df = pd.read_csv('poker_hand.csv')
# df = df[df['preflop_action'] != "('', '0.00')"]

# df['hole_cards_processed'] = df['hole_cards'].apply(processed_hand)   # [['6d Ac', "('F', '0.00')", 'CO', list([6, 14])]

# Wyświetlenie wybranych kolumn

df['position_processed'] = df['position'].map(position_map)
df = df.dropna(subset=['position_processed'])   #[['6d Ac', "('F', '0.00')", 'CO', list([6, 14]), 2],
df['hole_cards'] = df['hole_cards'].apply(lambda x: eval(x) if isinstance(x, str) else x)

# df['preflop_action_type'] = df['preflop_action'].apply(lambda x: eval(x)[0] if isinstance(eval(x), tuple) else '')
df['preflop_action_processed'] = df['preflop_action'].map(action_map)   #'hole_cards', 'preflop_action', 'position', 'hole_cards_processed','position_processed', 'preflop_action_type', 'preflop_action_processed'],
df['preflop_action_processed'] = df['preflop_action_processed'].fillna(0)   #['hole_cards', 'preflop_action', 'position', 'hole_cards_processed','position_processed', 'preflop_action_type', 'preflop_action_processed'],
print(df['preflop_action_processed'])

# Przygotowanie cech (features) i etykiety docelowej (target)
X = pd.DataFrame({
    'hand_strength': df['hole_cards'].apply(lambda hand: processed_hand(hand, percentage_table)),
    'position': df['position_processed']
})

# print("X:", X)
# print(X.isnull().sum())
y = df['preflop_action_processed']
print(y.value_counts(normalize=True))

# print("y:", y)
# Podział na zestawy treningowy i testowy
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Inicjalizacja i trenowanie modelu
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)
y_pred = model.predict(X_test)
# Przykładowa ręka do predykcji
sample_hand = [('Ad', 'Ks'), 'BTN']
hand_strength = processed_hand(sample_hand[0], percentage_table)
sample_hand_processed = [hand_strength, position_map[sample_hand[1]]]
print("sample_hand_processed:", sample_hand_processed)
# Predykcja akcji
probabilities = np.round(model.predict_proba([sample_hand_processed]), 2)

decision = model.predict([sample_hand_processed])
print("Probabilities:", probabilities)
print("Decision:", "raise" if decision == 1 else "fold")
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy:.2f}")
# print(df['preflop_action_processed'].value_counts())