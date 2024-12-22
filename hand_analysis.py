import glob
import re
import csv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from poker_app.pypokergui.engine.card import processed_hand, percentiles_table
class Hand:
    def __init__(self, hand_text):
        self.hand_text = hand_text
        self.small_blind = self.extract_small_blind()
        self.big_blind = self.extract_big_blind()
        self.hole_cards = self.extract_hole_cards()
        self.is_hero_first = self.is_hero_first_to_act()
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

    def is_hero_first_to_act(self):

        # Znajdź sekcję preflop
        preflop_start = self.hand_text.find('*** HOLE CARDS ***')
        flop_start = self.hand_text.find('Hero:')
        
        # Sprawdź, czy flop_start jest większy od preflop_start
        if flop_start == -1 or flop_start <= preflop_start:
            # Jeśli flop nie istnieje lub jest źle zlokalizowany, weź tylko sekcję preflop
            preflop_text = self.hand_text[preflop_start:]
        else:
            # Wyciągnij tekst od *** HOLE CARDS *** do *** FLOP ***
            preflop_text = self.hand_text[preflop_start:flop_start]
        
        # Sprawdź, czy jakakolwiek akcja (poza fold) pojawiła się przed Hero
        actions_before_hero = re.findall(r'^(?!Hero: )(.*?: (calls|bets|raises|checks))', preflop_text, re.MULTILINE)
        
        return len(actions_before_hero) == 0  # Jeśli brak akcji, Hero jest pierwszy

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
        fieldnames = ['hole_cards', 'preflop_action', 'position', 'sample_hand_strength']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for hand in hands:
            # print(hand.hole_cards, hand.preflop_action, hand.position)  
            if hand.is_hero_first:
                action, _ = hand.preflop_action
                # print(action)
                # Sprawdzenie, czy pola nie są puste
                if action:
                    if hand.hole_cards and action and hand.position:
                    # Zmiana formatu kart
                        cards = hand.hole_cards.split()  # Rozdzielenie np. '6d Ac' na ['6d', 'Ac']
                        hole_cards_tuple = tuple(cards)  # Zamiana na ('6d', 'Ac')
                        sample_hand_top_range  = processed_hand(hole_cards_tuple, percentiles_table)  # Obliczenie siły kart
                        writer.writerow({
                            'hole_cards': hole_cards_tuple,  # Zapisujemy jako tuple
                            'position': hand.position,
                            'preflop_action': action,  # Zapisujemy tylko akcję (np. 'F', 'R')
                            'sample_hand_strength': sample_hand_top_range
                        })



position_map = {'EP': 0, 'MP': 1, 'CO': 2, 'BTN': 3, 'SB': 4, 'BB': 5}
action_map = {'F': 0, 'R': 1}

FILES_PATH = 'hh/*.txt'

# Procesowanie plików z rozdaniami pokerowymi i utworzenie obiektów Hand
hands = process_poker_hand(FILES_PATH)

# Zapisanie wyników do pliku CSV
save_to_csv(hands)

df = pd.read_csv('poker_hand.csv')
df = df[~df['preflop_action'].isin(['X', 'C', 'B'])]
df['position_processed'] = df['position'].map(position_map)
df = df.dropna(subset=['position_processed'])
df['hole_cards'] = df['hole_cards'].apply(lambda x: eval(x) if isinstance(x, str) else x)

df['preflop_action_processed'] = df['preflop_action'].map(action_map)
df['preflop_action_processed'] = df['preflop_action_processed'].fillna(0)


sample_hand = [('As', '9d'), 'BTN']
hand_strength = processed_hand(sample_hand[0], percentiles_table)

df_filtered = df[
    df['hole_cards'].apply(lambda x: processed_hand(x, percentiles_table) <= hand_strength)
    ]
df_filtered.to_csv('filtered_poker_data.csv', index=False)
X_filtered = pd.DataFrame({
    'hand_strength': df_filtered['hole_cards'].apply(lambda hand: processed_hand(hand, percentiles_table)),
    'position': df_filtered['position_processed']
})
y_filtered = df_filtered['preflop_action_processed']
print(y_filtered.value_counts(normalize=True))
X_train, X_test, y_train, y_test = train_test_split(X_filtered, y_filtered, test_size=0.2, random_state=42)

model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight= 'balanced')
model.fit(X_train, y_train)
y_pred = model.predict(X_test)

sample_hand_processed = pd.DataFrame(
    [[hand_strength, position_map[sample_hand[1]]]],
    columns=['hand_strength', 'position'] 
)
probabilities = np.round(model.predict_proba(sample_hand_processed), 2)
decision = model.predict(sample_hand_processed)
print("Probabilities:", probabilities)
print("Decision:", "raise" if decision == 1 else "fold")
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy:.2f}")

print(f"Rozmiar y_train: {y_train.shape}")
print(f"Rozmiar X_test: {X_test.shape}")
print(f"Rozmiar y_test: {y_test.shape}")

cm = confusion_matrix(y_test, y_pred)

TP = cm[1, 1]
TN = cm[0, 0]
FP = cm[0, 1]
FN = cm[1, 0]
sensitivity = TP / (TP + FN)
specificity = TN / (TN + FP)

print(f"Sensitivity: {sensitivity}")
print(f"Specificity: {specificity}")
